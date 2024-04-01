import dataclasses
import time
from typing import List
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import queue
import logging
import psycopg2
import sys
from enum import Enum

import requests
from urllib import robotparser
from urllib.parse import urlparse, urlunparse
import ssl

from datetime import datetime

from DbLogic import DbLogic
import concurrent.futures
import threading
from dataclasses import dataclass

lock = threading.Lock()

ssl._create_default_https_context = ssl._create_unverified_context
#WEB_DRIVER_LOCATION = r"C:\Users\jurea\Desktop\Faks\MAG\12\IEPS\Projekt1\ieps_project\geckodriver" #TODO: change to your location
#WEB_DRIVER_LOCATION = "ieps_project/geckodriver"
TIMEOUT = 5

#############################
#html_hash = open("html_hashes.txt", "w", encoding="utf-8")
#urls_file = open("urls.txt", "w")
##########

frontier = queue.Queue()
#added_urls_set = {"https://www.gov.si/", "https://www.evem.gov.si/", "https://e-uprava.gov.si/", "https://www.e-prostor.gov.si/"}

class BinaryType(Enum):
    PDF = "PDF"
    DOC = "DOC"
    DOCX = "DOCX"
    PPT = "PPT"
    PPTX = "PPTX"
    JPG = "JPG"
    PNG = "PNG"
    SVG = "SVG"
    HTML = "HTML"
    OTHER = "OTHER"

firefox_options = FirefoxOptions()
firefox_options.add_argument("--headless")
firefox_options.add_argument("user-agent=fri-ieps-42")

# database class instance
db_logic = DbLogic()


def init_log():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s [%(threadName)s] [%(lineno)d]")
    #log = logging.getLogger()
    #log.setLevel(logging.getLevelName('INFO'))
    #log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s [%(threadName)s] ")

    #console_handler = logging.StreamHandler()
    #console_handler.setFormatter(log_formatter)
    #log.addHandler(console_handler)

def get_html_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            #print("Failed to fetch robots.txt. Status code:", response.status_code)
            logging.error(f"Failed to fetch robots.txt. Status code: {response.status_code}")
            return ""    
    except Exception as e:
        print("Error while fetching robots.txt content:", e)
        return ""

# TODO
# (DONE) dodaj robots.txt content v bazo
# (DONE) če se ne procesira pri continoue odstrani iz FRONTIRJA v bazi 
# (DONE) poglej za duplikate v bazi (ce je isti url ga ne damo v frontier; isti hash damo kot duplikat in damo link -> novo polje v db)
# (DONE) implementiraj paralelno obdelavo
# (DONE) sitemap
# poglej za ostale file (zip, rar, ...) -> binary
# (DONE) poglej elemente ki niso a in imajo href (onclick, ...)
# (DONE) from in to linki za page
# (DONE) poglej za slike in dodaj v bazo
# timeout za linke 5s

@dataclass
class RobotsTxt:
    can_fetch: bool = False
    site_maps: List[str] = dataclasses.field(default_factory=list)
    crawl_delay: int = TIMEOUT


def parse_robots_txt(url, user_agent, robots_txt_url):
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_txt_url)
    rp.read()
    crawl_delay = rp.crawl_delay("*")

    if crawl_delay is None:
        crawl_delay = TIMEOUT
    return RobotsTxt(can_fetch=rp.can_fetch(user_agent, url), 
                     site_maps=rp.sitemaps, 
                     crawl_delay=crawl_delay)
    
"""def is_allowed_and_sitemap(url, user_agent, robots_txt_url):
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_txt_url)
    rp.read()
    return rp.can_fetch(user_agent, url), rp.sitemaps

def get_crawl_delay(robots_txt_url):
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_txt_url)
    rp.read()
    crawl_delay = rp.crawl_delay("*")

    if crawl_delay is None:
        crawl_delay = TIMEOUT
    return crawl_delay"""

def url_exists(url_link):
    try:
        response = requests.get(url_link)  # Use HEAD request to check existence
        if response.status_code >= 200 and response.status_code < 300:
            return True
        else:
            return False
    except requests.exceptions.RequestException as ex:
        logging.error("Can not check if url exists.", ex)
        return False    

def get_response_code(url):
    try:
        response = requests.get(url)   
        return response.status_code, binary_type(response)
    except requests.exceptions.RequestException:
        return False    


#def is_html(url) -> bool:
#    try:
#        response = requests.head(url)
#        content_type = response.headers.get('Content-Type', '')
#        return 'text/html' in content_type
#    except Exception as e:
#        print("Error:", e)
#        return False

def binary_type(response):
    try:
        content_type = response.headers.get('Content-Type', '')
        if "text/html" in content_type:
            return BinaryType.HTML
        if "application/pdf" in content_type:
            return BinaryType.PDF
        elif "application/msword" in content_type:
            return BinaryType.DOC
        elif "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in content_type:
            return BinaryType.DOCX
        elif "application/vnd.ms-powerpoint" in content_type:
            return BinaryType.PPT
        elif "application/vnd.openxmlformats-officedocument.presentationml.presentation" in content_type:
            return BinaryType.PPTX
        elif "image/jpeg" in content_type:
            return BinaryType.JPG
        elif "image/png" in content_type:
            return BinaryType.PNG
        elif "image/svg+xml" in content_type:
            return BinaryType.SVG
        else:
            return BinaryType.OTHER
        
    except Exception as e:
        print("Error:", e)
        return False
    
"""def ends_with_extension(url):
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
"""
    
def crawl_web(i, driver, old_robots_url, html_hash_value):
    while not frontier.empty():
        with lock:
            web_address = frontier.get()
        if (i % 1) == 0: 
            logging.info(f"{i} Retrieving web page URL '{web_address}'")
            sys.stdout.flush()
        web_address = remove_query_and_fragment(web_address)
        #TODO check da page se ni v bazi (za prve 4)
        robots_url = "https://" + get_domain(web_address) + "/robots.txt"
        robots_content = ""
        sitemap_content = ""

        if url_exists(robots_url):
            robots_txt = parse_robots_txt(web_address, "*", robots_url)
            allowance = robots_txt.can_fetch
            robots_content = get_html_content(robots_url)
            crawl_delay = robots_txt.crawl_delay
            for sitemap in robots_txt.site_maps:
                if sitemap is not None:
                    sitemap_content += get_html_content(sitemap)
        else:
            allowance = True
            crawl_delay = TIMEOUT
        if not allowance:
            db_logic.save_page_invalid(web_address)
            continue
        # TODO vzemi iz frontirja (baza)
        wait = WebDriverWait(driver, crawl_delay)
        response_status_code, type = get_response_code(web_address)        
        
        if not (200 <= response_status_code < 300):
            db_logic.save_page_invalid(web_address)
            continue

        if db_logic.check_page_exists(web_address) is None:
            frontier.put(web_address)
            db_logic.save_page_frontier(web_address, datetime.now())

        try:
            driver.get(web_address)
        except Exception as e:
            logging.error(f"Error retrieving web page URL '{web_address}'", exc_info=e)
            db_logic.save_page_invalid(web_address)
            continue

        pageId = db_logic.check_page_exists(web_address)
        if web_address is not None and web_address[0:4] == "http":
            if type in [BinaryType.PDF, BinaryType.DOC, BinaryType.DOCX, BinaryType.PPT, BinaryType.PPTX]:
                db_logic.save_page_binary(web_address)
                db_logic.save_page_data(pageId, type)
                continue
            elif type == BinaryType.JPG or type == BinaryType.PNG or type == BinaryType.SVG:
                db_logic.save_page_binary(web_address)
                imageId = db_logic.check_page_exists(web_address)
                filename = web_address.split("/")[-1]
                type_string = type.value

                db_logic.insert_image(imageId, filename, type_string, datetime.now())
                continue
        
        else:
            logging.error("Unexpected web address type")

        html = driver.page_source
        html_hash_value = hash(html)
        #timestamp = datetime.now()
        site_id = db_logic.check_site_exists(get_domain(web_address))
        if site_id is None:
            db_logic.save_site(get_domain(web_address), robots_content, sitemap_content)
            site_id = db_logic.check_site_exists(get_domain(web_address))
        link_original = db_logic.check_hash_exists(html_hash_value)
        if link_original is not None:
            db_logic.save_page_duplicate(web_address, link_original)
            continue
        db_logic.save_page_update(site_id, web_address, html, html_hash_value, "HTML", response_status_code)
        links = driver.find_elements(By.TAG_NAME, "a")

        elements_with_onclick = driver.find_elements(By.XPATH, '//*[@href]')
        # Extract links from other href attributes
        for element in elements_with_onclick:
            if element not in links:
                links.append(element)

        links_ids = []

        for link in links:
            href = link.get_attribute("href")
            logging.info(f"  Checking href {href}")

            if href is not None and href[0:4] == "http" and '.gov.si' in href:
                href = remove_query_and_fragment(href)
                
                if db_logic.check_page_exists(href) is None:
                    robots_url = "https://" + get_domain(href) + "/robots.txt"
                    if robots_url != old_robots_url:
                        old_robots_url = robots_url
                        if url_exists(robots_url):
                            robots_txt = parse_robots_txt(href, "*", robots_url)
                            allowance = robots_txt.can_fetch
                        else:
                            allowance = True
                    if allowance:
                        #logging.info(f"    get_response")
                        #response_status_code, _ = get_response_code(href)
                        logging.info(f"    href allowed")

                        #if(200 <= response_status_code < 300):
                        #logging.info(f"    status code {response_status_code}")

                        with lock:
                            frontier.put(href)
                        #logging.info(f"    put")
                        db_logic.save_page_frontier(href, datetime.now(), pageId)
                        #logging.info(f"    save_page")
                        pageIDFrontier = db_logic.check_page_exists(href)
                        #logging.info(f"    check_page")
                        links_ids.append(pageIDFrontier)
                        #logging.info(f"    append")
                        db_logic.insert_link(pageId, pageIDFrontier)
                        #logging.info(f"    insert")

                    #added_urls_set.add(href)
        logging.info(f"frontier size: {frontier.qsize()}")
        db_logic.save_link_to(pageId, links_ids)
        i += 1

def get_html_and_links(frontier):
    with webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=firefox_options) as driver:
        i = 0
        old_robots_url = ""
        html_hash_value = None
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            executor.submit(crawl_web, i, driver, old_robots_url, html_hash_value)


#def print_frontier(frontier):
#    for l in frontier.queue:
#        print(l)

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

def main():
    init_log()
    frontier_raw = db_logic.get_frontier()

    if frontier_raw == []:
        frontier.put("https://evem.gov.si/")
        response_status_code, _ = get_response_code("https://evem.gov.si/")
        if(200 <= response_status_code < 300):
            db_logic.save_page_frontier("https://evem.gov.si/", datetime.now())
        frontier.put("https://www.gov.si/")
        response_status_code, _ = get_response_code("https://www.gov.si/")
        if(200 <= response_status_code < 300):
            db_logic.save_page_frontier("https://www.gov.si/", datetime.now())
        frontier.put("https://e-uprava.gov.si/")
        response_status_code, _ = get_response_code("https://e-uprava.gov.si/")
        if(200 <= response_status_code < 300):
            db_logic.save_page_frontier("https://e-uprava.gov.si/", datetime.now())
        frontier.put("https://www.e-prostor.gov.si/")
        response_status_code, _ = get_response_code("https://www.e-prostor.gov.si/")
        if(200 <= response_status_code < 300):
            db_logic.save_page_frontier("https://www.e-prostor.gov.si/", datetime.now())

    else:
        for url in frontier_raw:
            frontier.put(url)
        logging.info(f"initial frontier size: {frontier.qsize()}")
    get_html_and_links(frontier)
#db_logic.save_page_binary("https://www.gov.si/")
#db_logic.save_page_data(1, ".pdf")
#html_hash.close()
#urls_file.close()

if __name__ == "__main__":
    main()


#driver.get(robots_url)
#robots_txt = driver.find_element(By.TAG_NAME, "pre").text