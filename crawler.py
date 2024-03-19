import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import queue
import logging
import psycopg2

import requests
from urllib import robotparser
from urllib.parse import urlparse, urlunparse
import ssl

from datetime import datetime

from DbLogic import DbLogic

ssl._create_default_https_context = ssl._create_unverified_context
#logging.basicConfig(level=logging.INFO)
WEB_DRIVER_LOCATION = r"C:\Users\jurea\Desktop\Faks\MAG\12\IEPS\Projekt1\ieps_project\geckodriver" #TODO: change to your location
TIMEOUT = 5

#############################
html_hash = open("html_hashes.txt", "w", encoding="utf-8")
urls_file = open("urls.txt", "w")
##########

frontier = queue.Queue()
added_urls_set = {"https://www.gov.si/", "https://www.evem.gov.si/", "https://e-uprava.gov.si/", "https://www.e-prostor.gov.si/"}
frontier.put("https://www.evem.gov.si/")
frontier.put("https://www.gov.si/")
frontier.put("https://e-uprava.gov.si/")
frontier.put("https://www.e-prostor.gov.si/")

firefox_options = FirefoxOptions()
firefox_options.add_argument("--headless")
firefox_options.add_argument("user-agent=fri-ieps-42")

# database class instance
db_logic = DbLogic()


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

def get_response_code(url):
    try:
        response = requests.head(url)       #TODO: head ali get?
        return response.status_code
    except requests.exceptions.RequestException:
        return False    


def is_html(url):
    try:
        response = requests.head(url)
        content_type = response.headers.get('Content-Type', '')
        return 'text/html' in content_type
    except Exception as e:
        print("Error:", e)
        return False

def is_binary(url):
    parts = url.split("/")
    filename = parts[-1]
    extension_parts = filename.split(".")
    if len(extension_parts) > 1:
        return "." + extension_parts[-1]
    else:
        return ""
    
def ends_with_extension(url):
    document_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx']
    for extension in document_extensions:
        if url.endswith(extension):
            return True, extension
    return False

def get_url_extension(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    extension_parts = path.split(".")
    if len(extension_parts) > 1:
        return "." + extension_parts[-1]
    else:
        return ""
    
def get_html_and_links(frontier):
    with webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=firefox_options) as driver:
        i = 0
        old_robots_url = ""
        html_hash_value = None
        while not frontier.empty():
            web_address = frontier.get()
            print(f"{i}Retrieving web page URL '{web_address}'")

            robots_url = web_address + "robots.txt"
            #if is_allowed(web_address, "*", robots_url):
            crawl_delay = get_crawl_delay(robots_url)
            wait = WebDriverWait(driver, crawl_delay)
            try:
                driver.get(web_address)
            except Exception as e:
                print(f"An exception occurred: {e}") 

            html = driver.page_source
            links = driver.find_elements(By.TAG_NAME, "a")

            for link in links:
                href = link.get_attribute("href")
                start_time = time.time()
                
                #print(f"{robots_url}  {time.time() - start_time} seconds ---, ------>>>>> , ??? {exi}")

                if href is not None and href[0:4] == "http":
                    if is_binary(web_address):
                        extension = get_url_extension(web_address)
                        if extension in ['.pdf', '.doc', '.docx', '.ppt', '.pptx']:
                            print("Binary file: ", extension, "web: ", web_address)
                            #dont read it, just save it as binary with extension
                            continue
                    href = remove_query_and_fragment(href)

                    if href in added_urls_set:                  #checks if url was/is in frontier
                        continue
                    
                    robots_url = "https://" + get_domain(href) + "/robots.txt"
                    if robots_url != old_robots_url:
                        old_robots_url = robots_url
                        if url_exists(robots_url):
                            allowance = is_allowed(href, "*", robots_url)
                        else:
                            allowance = True
                    if allowance:
                        frontier.put(href)
                        html_hash_value = hash(html)
                        response_status_code = get_response_code(href)
                        timestamp = datetime.now()
                        #Tukaj zdaj lhko polnis bazo s podatki: url = href, html_content = html, hash_value = html_hash1, 
                        #    http_status_code = response_status_code, accessed_time = timestamp
                        #
                        db_logic.save_page(1, href, html, html_hash_value, response_status_code, timestamp)
                        added_urls_set.add(href)
            
            html_hash.write(str(html_hash_value) + '\n')
            if i == 100:
                for item in added_urls_set:
                    urls_file.write(str(item) + "\n")
                break
                
            i += 1


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

db_logic.save_site("gov.si", "")
get_html_and_links(frontier)
#print_frontier(frontier)
html_hash.close()
urls_file.close()




#driver.get(robots_url)
#robots_txt = driver.find_element(By.TAG_NAME, "pre").text