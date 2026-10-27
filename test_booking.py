
import os
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

GRID_URL = "http://localhost:4444"
TEST_URL = "https://www.selenium.dev/selenium/web/web-form.html"


@pytest.fixture
def driver():
    browser = os.environ.get("BROWSER", "chrome").lower()

    if browser == "firefox":
        options = webdriver.FirefoxOptions()
    else:
        options = webdriver.ChromeOptions()

    browser_driver = webdriver.Remote(
        command_executor=GRID_URL,
        options=options
    )

    yield browser_driver
    browser_driver.quit()


def test_web_form(driver, request):
    browser = os.environ.get("BROWSER", "chrome").lower()

    screenshot_dir = Path(
        os.environ.get("SCREENSHOT_DIR", f"screenshots/{browser}")
    )
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    try:
        driver.get(TEST_URL)

        # Check the page title
        assert driver.title == "Web form"

        # Enter text in the form
        text_box = driver.find_element(By.ID, "my-text-id")
        text_box.send_keys("DevOps Cross Browser Test")

        # Submit the form
        driver.find_element(By.CSS_SELECTOR, "button").click()

        # Wait for the confirmation heading
        result = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.TAG_NAME, "h1"))
        )

        assert result.text == "Form submitted"

        print(f"Test passed in {browser}")

    except Exception:
        screenshot = screenshot_dir / f"{request.node.name}.png"
        driver.save_screenshot(str(screenshot))
        print(f"Failure screenshot saved: {screenshot}")
        raise
