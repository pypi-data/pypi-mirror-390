import time
from browser_signals import show_test_banner, remove_test_banner

def test_title_has_example(driver):
    # Demonstrate the running banner while this test executes
    show_test_banner(driver, text="Running: test_title_has_example")
    try:
        assert "Example Domain" in driver.title
        # tiny pause to make banner visible in headed runs
        time.sleep(2)
    finally:
        remove_test_banner(driver)