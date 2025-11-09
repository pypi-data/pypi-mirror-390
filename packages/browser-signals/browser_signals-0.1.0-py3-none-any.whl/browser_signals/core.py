# Non-blocking, DOM-based visual signals for Selenium runs (Xvfb-friendly).
# Works with or without pytest. No external deps besides Selenium.

from __future__ import annotations
import sys
from contextlib import contextmanager
from typing import Optional, Callable

# ---- Public API -------------------------------------------------------------

def mark_failure(driver, message: str, use_flash: bool = True, frame: Optional[object] = None):
    _console(driver, f"TEST FAILURE: {message}", level="error")
    _inject_banner(driver, f"❌ TEST FAILED: {message}", color="red", frame=frame)
    if use_flash:
        _inject_flash(driver, rgba="rgba(255,0,0,0.2)", frame=frame)

def mark_warning(driver, message: str, use_flash: bool = False, frame: Optional[object] = None):
    _console(driver, f"TEST WARNING: {message}", level="warn")
    _inject_banner(driver, f"⚠️ TEST WARNING: {message}", color="#d97706", frame=frame)
    if use_flash:
        _inject_flash(driver, rgba="rgba(217,119,6,0.2)", frame=frame)

def mark_info(driver, message: str, use_flash: bool = False, frame: Optional[object] = None):
  _console(driver, f"TEST INFO: {message}", level="log")
  _inject_banner(driver, f"ℹ️ {message}", color="#2563eb", frame=frame)
  if use_flash:
    _inject_flash(driver, rgba="rgba(37,99,235,0.2)", frame=frame)

# ---- Running banner (persistent) -------------------------------------------------

def show_test_banner(driver, text: str = "Running Test...", color: str = "#facc15", frame: Optional[object] = None):
    """Show a small persistent banner indicating a test is running.

    Args:
        driver: Selenium WebDriver
        text: Banner text
        color: CSS color for the banner background (default: yellow-400)
        frame: Optional frame/iframe reference or index
    """
    safe_text = _js_safe(text)
    safe_color = _js_safe(color)
    script = f"""
    (function() {{
      try {{
        const id = 'browser-signals-running';
        let banner = document.getElementById(id);
        if (!banner) {{
          banner = document.createElement('div');
          banner.id = id;
          banner.setAttribute('role', 'status');
          banner.style.position = 'fixed';
          banner.style.top = '0';
          banner.style.left = '0';
          banner.style.height = '20px';
          banner.style.lineHeight = '20px';
          banner.style.padding = '0 8px';
          banner.style.background = '{safe_color}';
          banner.style.color = 'black';
          banner.style.fontSize = '12px';
          banner.style.borderRadius = '0 0 5px 0';
          banner.style.whiteSpace = 'nowrap';
          banner.style.zIndex = '2147483647';
          document.body.appendChild(banner);
        }}
        banner.textContent = '{safe_text}';
      }} catch (e) {{ try {{ console.error('browser_signals running banner failed', e); }} catch(_ ){{}} }}
    }})();
    """
    with _with_frame(driver, frame):
        driver.execute_script(script)

def remove_test_banner(driver, frame: Optional[object] = None):
    """Remove the running test banner if present."""
    script = """
    (function() {
      try {
        const el = document.getElementById('browser-signals-running');
        if (el) el.remove();
      } catch (e) { try { console.error('browser_signals remove running banner failed', e); } catch(_ ){} }
    })();
    """
    with _with_frame(driver, frame):
        driver.execute_script(script)

def navigate_with_banner(driver, url: str, banner_text: str = "Running Test...", color: str = "#facc15", frame: Optional[object] = None):
    """Navigate to a URL and show the running banner afterward.

    Mirrors helper behavior: first navigate, then display the banner.
    """
    driver.get(url)
    show_test_banner(driver, text=banner_text, color=color, frame=frame)

# ---- Unified banner API (Option C minimal) ---------------------------------------

def show_banner(
  driver,
  text: str,
  *,
  persistent: bool = False,
  flash: bool = False,
  duration_ms: int = 5000,
  position: str = "top-left",
  full_banner: bool = False,
  color: Optional[str] = None,
  log: bool = True,
  frame: Optional[object] = None,
  id: Optional[str] = None,
):
  """Display a banner or small status chip with consistent options.

  - full_banner=True renders a full-width banner (like mark_info/mark_failure)
    and auto-fades after duration_ms unless persistent=True.
  - full_banner=False renders a compact chip in a corner (position top-left/right).

  Args:
    text: The message to display
    persistent: If True, do not auto-remove (chips); for full banners, uses a very long duration
    flash: If True, also add a brief translucent screen flash
    duration_ms: Duration before fade-out for transient banners (ignored when persistent=True for chips)
    position: "top-left" or "top-right" for chips (ignored when full_banner=True)
    full_banner: Use the full-width banner style instead of a chip
    color: Optional override for background color
    log: If True, log to console with timestamp
    frame: Optional frame to target
    id: Optional DOM id to use (chips default to 'browser-signals-running'; full banner uses 'browser-signals-banner')
  """
  if log:
    _console(driver, f"SHOW: {text}", level="log")

  if full_banner:
    # Use existing banner injector; emulate persistence with a long duration
    use_color = color or "#2563eb"
    long_ms = duration_ms if not persistent else 86_400_000  # 24h
    _inject_banner(driver, text, color=use_color, duration_ms=long_ms, frame=frame)
  else:
    use_color = color or "#facc15"  # default amber
    chip_id = id or "browser-signals-running"
    _inject_chip(driver, text, color=use_color, position=position, persistent=persistent, duration_ms=duration_ms, elem_id=chip_id, frame=frame)

  if flash:
    _inject_flash(driver, rgba="rgba(37,99,235,0.2)", frame=frame)


def remove_banner(driver, *, id: Optional[str] = None, full_banner: bool = False, frame: Optional[object] = None):
  """Remove a banner/chip by id. Defaults to running-chip id or full banner id."""
  target_id = id or ("browser-signals-banner" if full_banner else "browser-signals-running")
  script = f"""
  (function() {{
    try {{ var el = document.getElementById('{_js_safe(target_id)}'); if (el) el.remove(); }}
    catch (e) {{ try {{ console.error('browser_signals remove failed', e); }} catch(_ ){{}} }}
  }})();
  """
  with _with_frame(driver, frame):
    driver.execute_script(script)


@contextmanager
def annotate_failures(driver, label: str = "", use_flash: bool = True, frame: Optional[object] = None):
    try:
        yield
    except Exception as e:
        title = f"{label}: {e}" if label else str(e)
        mark_failure(driver, title, use_flash=use_flash, frame=frame)
        raise

def alert_on_exception(driver, label: str = "", use_flash: bool = True, frame: Optional[object] = None) -> Callable:
    def _decorator(fn):
        def _wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                title = f"{label}: {e}" if label else str(e)
                mark_failure(driver, title, use_flash=use_flash, frame=frame)
                raise
        return _wrapper
    return _decorator

# ---- Internals -------------------------------------------------------------

def _console(driver, message: str, level: str = "log"):
  safe = _js_safe(message)
  # Include ms timestamp from Date.now() for easier timeline correlation
  driver.execute_script(f"console.{level}('BROWSER_SIGNALS [' + Date.now() + 'ms]: ' + '{safe}');")

def _with_frame(driver, frame):
    class _FrameCtx:
        def __init__(self, d, f): self.d, self.f = d, f
        def __enter__(self):
            if self.f is not None:
                self.d.switch_to.frame(self.f)
            return self.d
        def __exit__(self, exc_type, exc, tb):
            if self.f is not None:
                self.d.switch_to.default_content()
    return _FrameCtx(driver, frame)

def _inject_banner(driver, text: str, color: str, duration_ms: int = 5000, frame=None):
    safe_text = _js_safe(text)
    safe_color = _js_safe(color)
    script = f"""
    (function() {{
      try {{
        const id = 'browser-signals-banner';
        let old = document.getElementById(id);
        if (old) old.remove();

        let style = document.getElementById('browser-signals-style');
        if (!style) {{
          style = document.createElement('style');
          style.id = 'browser-signals-style';
          style.textContent = `
            #browser-signals-banner {{
              position: fixed; top: 0; left: 0; width: 100%;
              color: #fff; font-size: 20px; font-weight: 700;
              text-align: center; padding: 10px;
              z-index: 2147483647; opacity: 0.97;
              box-shadow: 0 2px 8px rgba(0,0,0,0.4);
            }}
            .browser-signals-fade {{ transition: opacity 1.5s ease-out; }}
          `;
          document.head.appendChild(style);
        }}

        const banner = document.createElement('div');
        banner.id = id;
        banner.className = 'browser-signals-fade';
        banner.setAttribute('role', 'alert');
        banner.textContent = '{safe_text}';
        banner.style.background = '{safe_color}';
        document.body.appendChild(banner);

        setTimeout(() => {{
          banner.style.opacity = '0';
          setTimeout(() => banner.remove(), 1600);
        }}, {int(duration_ms)});
      }} catch (e) {{
        try {{ console.error('browser_signals banner failed', e); }} catch(_){{}}
      }}
    }})();
    """
    with _with_frame(driver, frame):
        driver.execute_script(script)

def _inject_flash(driver, rgba: str, ms: int = 800, frame=None):
    safe_rgba = _js_safe(rgba)
    script = f"""
    (function() {{
      try {{
        const flash = document.createElement('div');
        flash.id = 'browser-signals-flash';
        flash.style.position = 'fixed';
        flash.style.inset = '0';
        flash.style.background = '{safe_rgba}';
        flash.style.zIndex = '2147483646';
        flash.style.opacity = '1';
        flash.style.pointerEvents = 'none';
        flash.style.transition = 'opacity {(ms/1000):.2f}s ease-out';
        document.body.appendChild(flash);
        requestAnimationFrame(() => {{ flash.style.opacity = '0'; }});
        setTimeout(() => flash.remove(), {ms + 120});
      }} catch (e) {{
        try {{ console.error('browser_signals flash failed', e); }} catch(_){{}}
      }}
    }})();
    """
    with _with_frame(driver, frame):
        driver.execute_script(script)

def _inject_chip(
    driver,
    text: str,
    color: str,
    *,
    position: str = "top-left",
    persistent: bool = False,
    duration_ms: int = 5000,
    elem_id: str = "browser-signals-running",
    frame=None,
):
    safe_text = _js_safe(text)
    safe_color = _js_safe(color)
    safe_id = _js_safe(elem_id)
    # Map position to CSS sides
    side_css = "left: 0; right: auto;" if position == "top-left" else "right: 0; left: auto;"
    rm_logic = "" if persistent else f"setTimeout(()=>el.remove(), {int(duration_ms)});"
    script = f"""
    (function() {{
      try {{
        var el = document.getElementById('{safe_id}');
        if (!el) {{
          el = document.createElement('div');
          el.id = '{safe_id}';
          el.setAttribute('role', 'status');
          el.style.position = 'fixed';
          el.style.top = '0';
          el.style.{ 'left' if position=='top-left' else 'right' } = '0';
          el.style.height = '20px';
          el.style.lineHeight = '20px';
          el.style.padding = '0 8px';
          el.style.background = '{safe_color}';
          el.style.color = 'black';
          el.style.fontSize = '12px';
          el.style.borderRadius = '{ '0 0 5px 0' if position=='top-left' else '0 0 0 5px' }';
          el.style.whiteSpace = 'nowrap';
          el.style.zIndex = '2147483647';
          document.body.appendChild(el);
        }}
        el.textContent = '{safe_text}';
        {rm_logic}
      }} catch (e) {{ try {{ console.error('browser_signals chip failed', e); }} catch(_ ){{}} }}
    }})();
    """
    with _with_frame(driver, frame):
        driver.execute_script(script)

def _js_safe(s: str) -> str:
    if s is None:
        return ""
    return str(s).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r")

