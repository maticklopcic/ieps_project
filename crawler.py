import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions

WEB_DRIVER_LOCATION = "/home/matic/Documents/faks/mag_1.letnik/2_semester/ieps/geckodriver"
TIMEOUT = 5
WEB_PAGE_ADDRESS = "https://vreme.arso.gov.si"

firefox_options = FirefoxOptions()
#firefox_options.add_argument("--headless")

firefox_options.add_argument("user-agent=fri-ieps-42")
print(f"Retrieving web page URL '{WEB_PAGE_ADDRESS}'")

driver = webdriver.Firefox(executable_path=WEB_DRIVER_LOCATION, options=firefox_options)
driver.get(WEB_PAGE_ADDRESS)

time.sleep(TIMEOUT)

html = driver.page_source
print(f"Retreived web content (truncated to first 900 characters): \n\n'\n{html[:900]}\n'\n")
page_msg = driver.find_element(By.CSS_SELECTOR, ".panel-header")

print(f"Web page message: {page_msg.text}")
driver.close()
