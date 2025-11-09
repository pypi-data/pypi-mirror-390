# basic-pytest example

This folder demonstrates `browser-signals` in both pytest and non-pytest flows.

## Set up

From repo root (where `pyproject.toml` lives):

```bash
# install the package in editable mode + pytest extra
pip install -e ".[pytest,selenium]"

# alternatively, install from requirements.txt at repo root
pip install -r requirements.txt
```

## What's included

- `test_passes.py` — a passing test that shows how to use the running banner API:
  - `show_test_banner(driver, text="Running: ...")` at the start
  - `remove_test_banner(driver)` in a `finally` block
  - includes a tiny `time.sleep(0.5)` so the banner is visible in headed runs

- `test_fails.py` — an intentionally failing test (marked `xfail`) to demonstrate the red failure banner and flash injected by the pytest plugin. This keeps the suite green while still exercising the failure overlays.

- `conftest.py` — provides a Chrome WebDriver fixture with CI-friendly flags. It tries a local chromedriver first and, if unavailable and `webdriver-manager` is installed, falls back automatically. For local headed runs, it also defaults `BROWSER_SIGNALS_PAUSE_SECONDS=2` so you can see failure banners.

## Run

```bash
cd examples/basic-pytest

# Headed run
../../.venv/bin/python -m pytest -q

# Customize the failure pause duration (seconds)
BROWSER_SIGNALS_PAUSE_SECONDS=4 ../../.venv/bin/python -m pytest -q

# CI/headless (no pause by default)
HEADLESS=true ../../.venv/bin/python -m pytest -q
```

## Optional: auto "running" banners

The passing test already demonstrates manual banners via `show_test_banner`/`remove_test_banner`.
If you prefer automatic banners for each test, opt in via an environment variable:

```bash
BROWSER_SIGNALS_SHOW_RUNNING=true ../../.venv/bin/python -m pytest -q
```

This will show a small "▶ Running: test-name" banner at setup and remove it at teardown.

## Using the unified banner API

In addition to the helpers above, you can use the flexible `show_banner` / `remove_banner` APIs:

```python
from browser_signals import show_banner, remove_banner

# Chip (top-right), persistent until removed
show_banner(driver, "Running: checkout flow", position="top-right", persistent=True, color="#fde047")
remove_banner(driver)

# Full-width transient banner (auto-fades)
show_banner(driver, "Fetched dashboard data", full_banner=True, duration_ms=3000)

# Chip with a quick timeline flash
show_banner(driver, "Step complete", flash=True, duration_ms=1000)
```
