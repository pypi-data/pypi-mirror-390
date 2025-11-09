import pytest
from selenium.common.exceptions import NoSuchElementException

@pytest.mark.xfail(reason="Demonstration of browser-signals on failures", strict=False)
def test_missing_element_injects_banner(driver):
    # This will raise NoSuchElementException -> test failure
    # The browser-signals pytest plugin should inject a red banner + flash.
    driver.find_element("css selector", "#definitely-not-here")