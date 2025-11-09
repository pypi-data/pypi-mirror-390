import os
import sys
import time
import pathlib
import pytest

# Make the package importable when running pytest from this example folder
_SRC = pathlib.Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# If you run without installing the package (editable mode), uncomment:
# pytest_plugins = ["browser_signals.pytest_plugin"]

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
try:
    # Optional runtime fallback to fetch a matching chromedriver
    from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
    from selenium.webdriver.chrome.service import Service  # type: ignore
    _HAS_WDM = True
except Exception:
    _HAS_WDM = False

@pytest.fixture(scope="function")
def driver():
    """
    A small, CI-friendly Chrome driver fixture.
    - Headed by default so you can watch it locally
    - Switch to headless with env HEADLESS=true
    - Uses standard Chrome on PATH; adapt to webdriver-manager if desired
    """
    headless = os.environ.get("HEADLESS", "").lower() in ("1", "true", "yes")
    # For local demo visibility: default to a 2s pause on failure unless overridden.
    if not headless and not os.environ.get("BROWSER_SIGNALS_PAUSE_SECONDS"):
        os.environ["BROWSER_SIGNALS_PAUSE_SECONDS"] = "2"
    opts = ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    # CI/Xvfb-friendly flags:
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,800")

    # Try local Chrome/Chromedriver first; if that fails and webdriver-manager is
    # available, fall back to downloading a compatible driver.
    try:
        drv = webdriver.Chrome(options=opts)
    except WebDriverException as e:
        if not _HAS_WDM:
            raise RuntimeError(
                "Could not start Chrome WebDriver. Install 'webdriver-manager' or "
                "ensure a compatible chromedriver is on PATH. Original error: "
                f"{e}"
            )
        service = Service(ChromeDriverManager().install())
        drv = webdriver.Chrome(service=service, options=opts)

    # Small helper so you always start from a known page
    drv.get("https://example.com")
    time.sleep(0.2)

    yield drv

    # Teardown
    drv.quit()