import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def get_webdriver(browser_dir: str) -> webdriver.Chrome:

    if not os.path.exists(browser_dir):
        os.makedirs(browser_dir)

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument(f"--user-data-dir={browser_dir}")

    service = Service(
        executable_path='/usr/bin/chromedriver'
    )

    driver = webdriver.Chrome(
        service=service,
        options=options
    )

    return driver
