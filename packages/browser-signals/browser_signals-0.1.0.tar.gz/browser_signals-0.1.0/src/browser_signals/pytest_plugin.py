"""
Pytest plugin entry point. Auto-loaded via project.entry-points.pytest11.
You can disable at runtime:  BROWSER_SIGNALS_DISABLE_PYTEST=true pytest

Optional local dev pause to visually inspect banners:
    BROWSER_SIGNALS_PAUSE_SECONDS=2 pytest

Optional running banner (opt-in):
    BROWSER_SIGNALS_SHOW_RUNNING=true pytest
Shows a small persistent banner while a test is running; removed at teardown.
"""

import os
import traceback
import time
from .core import mark_failure, show_test_banner, remove_test_banner

def pytest_runtest_makereport(item, call):
    # Respect opt-out
    if os.environ.get("BROWSER_SIGNALS_DISABLE_PYTEST", "").lower() in ("1", "true", "yes"):
        return

    if call.when != "call":
        return  # only annotate test body failures

    if call.excinfo is None:
        return  # passed or skipped

    # Try to grab a WebDriver from common fixture names
    driver = None
    for key in ("driver", "browser", "web_driver"):
        if key in getattr(item, "funcargs", {}):
            driver = item.funcargs[key]
            break
    if driver is None:
        return

    tb_text = "".join(traceback.format_exception(call.excinfo.type, call.excinfo.value, call.excinfo.tb))
    first_line = (tb_text.splitlines() or ["Test failed"])[0]
    msg = f"{item.name}: {first_line[:240]}"

    try:
        mark_failure(driver, msg, use_flash=True)
        # Optional pause so humans can see the banner before teardown
        pause_env = os.environ.get("BROWSER_SIGNALS_PAUSE_SECONDS", "").strip()
        if pause_env:
            try:
                pause = float(pause_env)
            except (TypeError, ValueError):
                pause = 0.0
            if pause and pause > 0:
                time.sleep(pause)
    except Exception as e:
        # Never mask the original test failure
        item.config.warn(code="BROWSER_SIGNALS_INJECTION_FAILED", message=str(e))


def _maybe_get_driver(item):
    for key in ("driver", "browser", "web_driver"):
        if key in getattr(item, "funcargs", {}):
            return item.funcargs[key]
    return None


def pytest_runtest_setup(item):
    # Respect opt-out
    if os.environ.get("BROWSER_SIGNALS_DISABLE_PYTEST", "").lower() in ("1", "true", "yes"):
        return
    # Running banner is opt-in
    if os.environ.get("BROWSER_SIGNALS_SHOW_RUNNING", "").lower() not in ("1", "true", "yes"):
        return

    driver = _maybe_get_driver(item)
    if not driver:
        return
    # Keep message compact; include nodeid for uniqueness
    text = f"▶ Running: {item.name}"
    try:
        show_test_banner(driver, text=text, color="#fde047")  # amber-300
    except Exception as _e:
        # Never block setup on banner errors; ignore
        return


def pytest_runtest_teardown(item):
    if os.environ.get("BROWSER_SIGNALS_DISABLE_PYTEST", "").lower() in ("1", "true", "yes"):
        return
    if os.environ.get("BROWSER_SIGNALS_SHOW_RUNNING", "").lower() not in ("1", "true", "yes"):
        return
    driver = _maybe_get_driver(item)
    if not driver:
        return
    try:
        remove_test_banner(driver)
    except Exception as _e:
        return

