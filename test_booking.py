
import os
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


BASE = "https://www.practiceqaautomation.com"
GRID_URL = os.getenv("GRID_URL", "http://localhost:4444/wd/hub")
BROWSER = os.getenv("BROWSER", "chrome").lower()


def tid(test_id):
    return (By.CSS_SELECTOR, f"[data-testid='{test_id}']")


class Ui:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def centre(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element
        )
        return element

    def ready(self, locator):
        return self.centre(
            self.wait.until(EC.element_to_be_clickable(locator))
        )

    def click(self, locator):
        self.ready(locator).click()

    def nth(self, test_id, n):
        self.wait.until(
            lambda d: len(d.find_elements(*tid(test_id))) > n
        )
        return self.centre(
            self.driver.find_elements(*tid(test_id))[n]
        )

    def type(self, locator, value):
        element = self.ready(locator)
        element.clear()
        element.send_keys(value)

    def select(self, locator, value):
        Select(self.ready(locator)).select_by_value(value)

    def check(self, locator):
        element = self.ready(locator)
        if not element.is_selected():
            element.click()

    def expect_text(self, locator, text):
        self.wait.until(
            EC.text_to_be_present_in_element(locator, text)
        )

    def expect_visible(self, locator):
        self.wait.until(
            EC.visibility_of_element_located(locator)
        )


@pytest.fixture
def driver():
    if BROWSER == "firefox":
        options = webdriver.FirefoxOptions()
    elif BROWSER == "chrome":
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
        })
    else:
        pytest.fail(
            f"Unsupported browser: {BROWSER}. Use chrome or firefox."
        )

    browser_driver = webdriver.Remote(
        command_executor=GRID_URL,
        options=options
    )

    yield browser_driver
    browser_driver.quit()


def test_books_a_hotel_end_to_end(driver):
    ui = Ui(driver)

    try:
        driver.get(BASE + "/apps/hotel")

        # Search for a hotel in Goa
        ui.select((By.ID, "city"), "goa")
        ui.nth("checkin-day", 2).click()
        ui.click((By.CSS_SELECTOR, "[aria-label='Increase Nights']"))
        ui.click((By.XPATH, "//button[normalize-space()='Search hotels']"))

        ui.wait.until(EC.url_contains("/apps/hotel/results"))

        # Filter and select a hotel
        ui.check(tid("star-5"))
        ui.select((By.NAME, "sort"), "price-asc")
        ui.expect_text(tid("result-count"), "2 properties")

        ui.click(tid("view-rooms-g1"))
        ui.wait.until(EC.url_contains("/apps/hotel/hotel/g1"))

        ui.expect_text(tid("hotel-title"), "Palm Grove Resort")
        ui.click(tid("select-room-deluxe"))
        ui.check((By.ID, "addon-breakfast"))
        ui.expect_visible(tid("price-total"))

        ui.click(
            (By.XPATH, "//button[normalize-space()='Continue to booking']")
        )

        # Enter fictional guest details
        ui.type((By.NAME, "guest-first-name"), "Ada")
        ui.type((By.ID, "guest-last-name"), "Lovelace")
        ui.type((By.NAME, "guest-email"), "ada@example.com")
        ui.type((By.ID, "guest-phone"), "5551234567")

        ui.select((By.NAME, "arrival-time"), "14:00 – 16:00")
        ui.click(tid("pay-now"))

        # Use only the practice site's documented test card details
        ui.type((By.ID, "card-number"), "4242424242424242")
        ui.type((By.CSS_SELECTOR, "[placeholder='MM/YY']"), "1230")
        ui.type((By.NAME, "card-cvv"), "123")
        ui.check((By.ID, "accept-policy"))

        ui.click(
            (By.XPATH, "//button[normalize-space()='Confirm booking']")
        )

        # Verify the booking confirmation
        ui.expect_visible(tid("booking-confirmed"))
        ui.expect_text(tid("reservation-id"), "SE-")
        ui.expect_text(tid("confirmed-room"), "Deluxe Room")

    except Exception:
        os.makedirs(f"screenshots/{BROWSER}", exist_ok=True)
        driver.save_screenshot(
            f"screenshots/{BROWSER}/booking_failure.png"
        )
        raise
