import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def login_airbnb(driver: webdriver.Chrome, abuser: str, abpass: str):

    test_url = "https://www.airbnb.com/hosting"
    redirect_url = "https://www.airbnb.com/login?redirect_url=%2Fhosting"

    driver.get(test_url)
    time.sleep(10)
    current_url = driver.current_url

    if current_url == test_url:
        return

    if current_url != redirect_url:
        raise Exception(f"unexpected redirect url {current_url}")

    print(f"login_airbnb: redirected to {current_url} for new login")

    # wait for the "Continue with email" button to be present and click it
    continue_with_email_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                'button[data-testid="social-auth-button-email"]'
            )
        )
    )
    continue_with_email_button.click()

    # wait for the email input to be present and enter the email
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                'input[data-testid="email-login-email"]'
            )
        )
    )
    email_input.send_keys(abuser)

    # wait for the submit button to be present and click it
    submit_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                'button[data-testid="signup-login-submit-btn"]'
            )
        )
    )
    submit_button.click()

    # wait for the password input to be present and enter the password
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                'input[data-testid="email-signup-password"]'
            )
        )
    )
    password_input.send_keys(abpass)

    # wait for the submit button to be present and click it
    submit_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                'button[data-testid="signup-login-submit-btn"]'
            )
        )
    )
    submit_button.click()

    # important to wait to so browser successfully caches everything
    time.sleep(10)

    return True
