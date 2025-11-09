# Browser Signals — Visual in‑browser cues for Selenium tests

Non‑blocking, DOM-based visual signals that appear inside the page during automated UI tests. Great for CI/Xvfb recordings so you can instantly see when a test failed.

Quick links:

- Example project: `examples/basic-pytest`
- Pytest usage: auto-annotates failures when your test has a `driver` fixture
- Script usage (no pytest): call `mark_failure`, `mark_info`, or wrap with `annotate_failures`

Install for local dev:

```bash
pip install -e ".[pytest,selenium]"
# alternatively, install from requirements.txt at repo root
pip install -r requirements.txt
```

Run the example:

```bash
cd examples/basic-pytest
# Headed run with a small pause so you can see the banner
../../.venv/bin/python -m pytest -q

# Customize the pause
BROWSER_SIGNALS_PAUSE_SECONDS=4 ../../.venv/bin/python -m pytest -q

# CI/headless (no pause by default)
HEADLESS=true ../../.venv/bin/python -m pytest -q
```

## Features

- Failure banners (top-of-page red banner with message)
- Brief translucent "timeline" flash
- Optional info/warning banners
- Non-blocking (no alerts that halt execution)
- Works with or without pytest (pytest plugin auto-annotates failures)

## Usage with pytest

The plugin is auto-discovered by pytest via entry-points. If your test has a Selenium driver fixture named `driver`, `browser`, or `web_driver`, a failure will inject a red banner and a short flash into the DOM.

```python
def test_missing_element_injects_banner(driver):
    driver.find_element("css selector", "#definitely-not-here")  # fails -> banner + flash
```

Controls:

- Disable plugin: `BROWSER_SIGNALS_DISABLE_PYTEST=true`
- Pause after banner (for local visibility): `BROWSER_SIGNALS_PAUSE_SECONDS=2`
- Show a running banner during tests (opt-in): `BROWSER_SIGNALS_SHOW_RUNNING=true`

## Usage without pytest

```python
from browser_signals import mark_failure, mark_warning, mark_info, annotate_failures

mark_info(driver, "Starting login", use_flash=True)

with annotate_failures(driver, label="Login flow"):
    driver.get("https://example.com")
    driver.find_element("css selector", "#definitely-not-here")  # banners + re-raise
```

API:

- `mark_failure(driver, message, use_flash=True, frame=None)`
- `mark_warning(driver, message, use_flash=False, frame=None)`
- `mark_info(driver, message, use_flash=False, frame=None)`
- `annotate_failures(driver, label="", use_flash=True, frame=None)` (context manager)
- `alert_on_exception(driver, label="", use_flash=True, frame=None)` (decorator)

Running banner helpers:

- `show_test_banner(driver, text="Running Test...", color="#facc15", frame=None)`
- `remove_test_banner(driver, frame=None)`
- `navigate_with_banner(driver, url, banner_text="Running Test...", color="#facc15", frame=None)`

Unified banners:

- `show_banner(driver, text, persistent=False, flash=False, duration_ms=5000, position="top-left", full_banner=False, color=None, log=True, frame=None, id=None)`
  - Chips (full_banner=False): position can be `top-left` or `top-right`. Persistent chips remain until you call `remove_banner`; otherwise they auto-remove after `duration_ms`.
  - Full-width (full_banner=True): uses the large page-top banner; transient by default, or simulated persistent if `persistent=True`.
  - `flash=True` adds a short translucent flash. `log=True` writes a console entry with a millisecond timestamp.
- `remove_banner(driver, id=None, full_banner=False, frame=None)`
  - Removes by id; defaults to the running chip id when `full_banner=False`, or the main banner id when `full_banner=True`.

Examples:

```python
# Chip (top-right), persistent
from browser_signals import show_banner, remove_banner
show_banner(driver, "Running: checkout flow", position="top-right", persistent=True, color="#fde047")
# ... later
remove_banner(driver)

# Full-width transient info banner
show_banner(driver, "Fetched dashboard data", full_banner=True, duration_ms=4000)

# Chip with a timeline flash
show_banner(driver, "Step complete", flash=True, duration_ms=1200)
```

## Configuration and env vars

- `BROWSER_SIGNALS_DISABLE_PYTEST` — set to `true`/`1` to disable the pytest plugin.
- `BROWSER_SIGNALS_PAUSE_SECONDS` — seconds to sleep after injecting a failure (useful for local demos). Disabled by default; the example enables 2s in headed runs.
- `HEADLESS` — if set to `true`/`1`, the example fixture runs Chrome headless and does not add the pause.

Recommended Chrome flags for CI/Xvfb (used in the example fixture): `--no-sandbox`, `--disable-dev-shm-usage`, `--disable-gpu`, `--window-size=1280,800`.

## Troubleshooting

- Chromedriver not found / version mismatch: ensure a compatible chromedriver is on PATH, or install `webdriver-manager` and let the example fall back automatically.
- Duplicate plugin registration: avoid manually adding `pytest_plugins = ["browser_signals.pytest_plugin"]` if the package is installed with the pytest entry-point; use one or the other.
- Not seeing the banner in recordings: increase `BROWSER_SIGNALS_PAUSE_SECONDS` locally, or adjust banner duration in `core.py` for your needs.

## License

MIT
