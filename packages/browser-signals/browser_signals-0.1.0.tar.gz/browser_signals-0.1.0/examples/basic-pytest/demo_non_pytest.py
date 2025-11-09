"""
Standalone demo: run with `python demo_non_pytest.py`
Shows how to use browser_signals without pytest.
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from browser_signals import annotate_failures, mark_info

def make_driver():
    opts = ChromeOptions()
    # For local visibility, keep headed. For CI, set HEADLESS=true env var.
    import os
    if os.environ.get("HEADLESS", "").lower() in ("1", "true", "yes"):
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,800")
    return webdriver.Chrome(options=opts)

def main():
    drv = make_driver()
    try:
        drv.get("https://example.com")
        mark_info(drv, "Starting standalone demo…")
        time.sleep(0.5)

        # Any exception inside this context will inject a red banner + flash
        with annotate_failures(drv, "Standalone flow"):
            # Intentionally fail
            drv.find_element("css selector", "#not-found")
    finally:
        time.sleep(1.0)  # Give you a moment to see the banner
        drv.quit()

if __name__ == "__main__":
    main()