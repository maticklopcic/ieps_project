import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import queue
import logging

import requests
from urllib import robotparser
from urllib.parse import urlparse, urlunparse

#logging.basicConfig(level=logging.INFO)
WEB_DRIVER_LOCATION = "/home/matic/Documents/faks/mag_1.letnik/2_semester/ieps/geckodriver"
TIMEOUT = 5

frontier = queue.Queue()
added_urls_set = {"https://www.gov.si/", "https://www.evem.gov.si/", "https://www.e-uprava.gov.si/", "https://www.e-prostor.gov.si/"}
frontier.put("https://www.gov.si/")
frontier.put("https://www.evem.gov.si/")
frontier.put("https://www.e-uprava.gov.si/")
frontier.put("https://www.e-prostor.gov.si/")

firefox_options = FirefoxOptions()
firefox_options.add_argument("--headless")

firefox_options.add_argument("user-agent=fri-ieps-42")

def is_allowed(url, user_agent, robots_txt_url):
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_txt_url)
    rp.read()
    return rp.can_fetch(user_agent, url)

def get_crawl_delay(robots_txt_url):
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_txt_url)
    rp.read()
    crawl_delay = rp.crawl_delay("*")

    if crawl_delay is None:
        crawl_delay = TIMEOUT
    return crawl_delay

def url_exists(url_link):
    try:
        response = requests.head(url_link)  # Use HEAD request to check existence
        if response.status_code >= 200 and response.status_code < 300:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

def get_html_and_links(frontier):
    with webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=firefox_options) as driver:
        while not frontier.empty():
            web_address = frontier.get()
            print(f"Retrieving web page URL '{web_address}'")

            robots_url = web_address + "robots.txt"
            if is_allowed(web_address, "*", robots_url):
                crawl_delay = get_crawl_delay(robots_url)
                wait = WebDriverWait(driver, crawl_delay)

                driver.get(web_address)

                html = driver.page_source
                links = driver.find_elements(By.TAG_NAME, "a")

                for link in links:
                    href = link.get_attribute("href")
                    href = remove_query_and_fragment(href)
                    robots_url = get_robots_url(href)
                    start_time = time.time()
                    
                    #print(f"{robots_url}  {time.time() - start_time} seconds ---, ------>>>>> , ??? {exi}")

                    if href is not None and href[0:4] == "http":
                        if href in added_urls_set:                  #checks if url was/is in frontier
                            continue
                        if url_exists(get_domain(robots_url)):
                            allowance = is_allowed(href, "*", robots_url)
                        else:
                            allowance = True
                        if allowance:
                            frontier.put(href)
                            added_urls_set.add(href)

            return html, links

def get_robots_url(url):
    return url + "robots.txt" 

def print_frontier(frontier):
    for l in frontier.queue:
        print(l)

def get_domain(link):
    domain = urlparse(link).netloc
    return domain   
 
def remove_query_and_fragment(url):
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc
    path = parsed_url.path
    params = parsed_url.params

    # Remove query parameters and fragment
    new_url = urlunparse((scheme, netloc, path, params, '', ''))
    return new_url


html, links = get_html_and_links(frontier)
print_frontier(frontier)





#driver.get(robots_url)
#robots_txt = driver.find_element(By.TAG_NAME, "pre").text