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
import sys

import requests
from urllib import robotparser
from urllib.parse import urlparse, urlunparse
import ssl

from datetime import datetime

from DbLogic import DbLogic

ssl._create_default_https_context = ssl._create_unverified_context
#logging.basicConfig(level=logging.INFO)
WEB_DRIVER_LOCATION = r"C:\Users\jurea\Desktop\Faks\MAG\12\IEPS\Projekt1\ieps_project\geckodriver" #TODO: change to your location
#WEB_DRIVER_LOCATION = "ieps_project/geckodriver"
TIMEOUT = 5

#############################
html_hash = open("html_hashes.txt", "w", encoding="utf-8")
urls_file = open("urls.txt", "w")
##########

frontier = queue.Queue()
#added_urls_set = {"https://www.gov.si/", "https://www.evem.gov.si/", "https://e-uprava.gov.si/", "https://www.e-prostor.gov.si/"}


firefox_options = FirefoxOptions()
firefox_options.add_argument("--headless")
firefox_options.add_argument("user-agent=fri-ieps-42")

# database class instance
db_logic = DbLogic()

def get_html_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Content of robots.txt:")
            print(response.text)
            return response.text
        else:
            print("Failed to fetch robots.txt. Status code:", response.status_code)
            return ""    
    except Exception as e:
        print("Error while fetching robots.txt content:", e)
        return ""

# TODO
# dodaj robots.txt content v bazo
# (DONE) če se ne procesira pri continoue odstrani iz FRONTIRJA v bazi 
# (DONE) poglej za duplikate v bazi (ce je isti url ga ne damo v frontier; isti hash damo kot duplikat in damo link -> novo polje v db)
# implementiraj paralelno obdelavo
# sitemap
# poglej za ostale file (zip, rar, ...) -> binary
# poglej elemente ki niso a in imajo href (onclick, ...)
# from in to linki za page
# poglej za slike in dodaj v bazo

def is_allowed_and_sitemap(url, user_agent, robots_txt_url):
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
            web_address = frontier.get()#"https://www.gov.si" #
            print(f"{i}Retrieving web page URL '{web_address}'")
            web_address = remove_query_and_fragment(web_address)
            #TODO check da page se ni v bazi (za prve 4)
            robots_url = "https://" + get_domain(web_address) + "/robots.txt"
            robots_content = ""
            sitemap_content = ""

            if url_exists(robots_url):
                allowance, all_sitemaps = is_allowed_and_sitemap(web_address, "*", robots_url)
                robots_content = get_html_content(robots_url)
                for sitemap in all_sitemaps:
                    if sitemap is not None:
                        sitemap_content += get_html_content(sitemap)
            else:
                allowance = True
            if not allowance:
                print(f"URL: {web_address} not allowed by robots.txt")
                db_logic.save_page_invalid(web_address)
                continue
            # TODO vzemi iz frontirja (baza)
            print(f"URL: {web_address} allowed by robots.txt")
            crawl_delay = get_crawl_delay(robots_url)
            wait = WebDriverWait(driver, crawl_delay)
            if db_logic.check_page_exists(web_address) is None:
                print(f"URL: {web_address} not in database")
                response_status_code = get_response_code(web_address)
                if(200 <= response_status_code < 300):
                    #frontier.put(web_address)
                    db_logic.save_page_frontier(web_address, response_status_code, datetime.now())
            try:
                driver.get(web_address)
            except Exception as e:
                print(f"Error retrieving web page URL '{web_address}'")
                print(f"An exception occurred: {e}")
                db_logic.save_page_invalid(web_address)
                continue
            response_status_code = get_response_code(web_address)
            if not (200 <= response_status_code < 300):
                print(f"URL: {web_address} returned status code: {response_status_code}")
                db_logic.save_page_invalid(web_address)
                continue
            if web_address is not None and web_address[0:4] == "http":
                if is_binary(web_address):
                    extension = get_url_extension(web_address)
                    if extension in ['.pdf', '.doc', '.docx', '.ppt', '.pptx']: # dodaj .zip in poglej za ostale file
                        print("Binary file: ", extension, "web: ", web_address)
                        db_logic.save_page_binary(web_address)
                        page_id = db_logic.check_page_exists(web_address)
                        db_logic.save_page_data(page_id, extension)
                        
                        continue
                #web_address = remove_query_and_fragment(web_address)
            html = driver.page_source
            html_hash_value = hash(html)
            #timestamp = datetime.now()
            site_id = db_logic.check_site_exists(get_domain(web_address))
            if site_id is None:
                db_logic.save_site(get_domain(web_address), robots_content, "")
                site_id = db_logic.check_site_exists(get_domain(web_address))
            link_original = db_logic.check_hash_exists(html_hash_value)
            if link_original is not None:
                db_logic.save_page_duplicate(web_address, link_original)
                continue
            db_logic.save_page_update(site_id, web_address, html, html_hash_value, "HTML") #TODO PREVERI ZA DUPLIKATE!!!!
            links = driver.find_elements(By.TAG_NAME, "a")
            #TODO poglej elemente ki niso a in omajo href
            for link in links:
                href = link.get_attribute("href")
                start_time = time.time()
                
                #print(f"{robots_url}  {time.time() - start_time} seconds ---, ------>>>>> , ??? {exi}")

                if href is not None and href[0:4] == "http":
                    #if is_binary(web_address):
                    #   extension = get_url_extension(web_address)
                    #    if extension in ['.pdf', '.doc', '.docx', '.ppt', '.pptx']:
                            #print("Binary file: ", extension, "web: ", web_address)
                            #dont read it, just save it as binary with extension
                            #if(response_status_code == 200):
                            #db_logic.save_page_frontier(site_id, href, 200, timestamp, "BINARY")
                    #        continue
                    href = remove_query_and_fragment(href)

                    #if href in added_urls_set:                  #checks if url was/is in frontier
                    #    continue
                    
                    robots_url = "https://" + get_domain(href) + "/robots.txt"
                    if robots_url != old_robots_url:
                        old_robots_url = robots_url
                        if url_exists(robots_url):
                            allowance, all_sitemaps = is_allowed_and_sitemap(href, "*", robots_url)
                            #TODO:all_sitemaps
                        else:
                            allowance = True
                    if allowance:

                        #print(f"URL: {href} added to frontier.")
                        response_status_code = get_response_code(href)
                        if(200 <= response_status_code < 300):
                            if db_logic.check_page_exists(href) is None:
                                frontier.put(href)
                                db_logic.save_page_frontier(href, response_status_code, datetime.now())
                        #added_urls_set.add(href)
            
            html_hash.write(str(html_hash_value) + '\n')
            #if i == 100:
            #    for item in added_urls_set:
            #        urls_file.write(str(item) + "\n")
            #    break
                
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

#db_logic.save_site("gov.si", "")
frontier_raw = db_logic.get_frontier()

if frontier_raw == []:
    print("The list is empty.")
    frontier.put("https://www.evem.gov.si/")
    response_status_code = get_response_code("https://www.evem.gov.si/")
    if(200 <= response_status_code < 300):
        db_logic.save_page_frontier("https://www.evem.gov.si/", response_status_code, datetime.now())
    frontier.put("https://www.gov.si/")
    response_status_code = get_response_code("https://www.gov.si/")
    if(200 <= response_status_code < 300):
        db_logic.save_page_frontier("https://www.gov.si/", response_status_code, datetime.now())
    frontier.put("https://e-uprava.gov.si/")
    response_status_code = get_response_code("https://e-uprava.gov.si/")
    if(200 <= response_status_code < 300):
        db_logic.save_page_frontier("https://e-uprava.gov.si/", response_status_code, datetime.now())
    frontier.put("https://www.e-prostor.gov.si/")
    response_status_code = get_response_code("https://www.e-prostor.gov.si/")
    if(200 <= response_status_code < 300):
        db_logic.save_page_frontier("https://www.e-prostor.gov.si/", response_status_code, datetime.now())

else:
    for url in frontier_raw:
        frontier.put(url)
print("VSI URLJI V FRONTIERJU: ", frontier.queue)
get_html_and_links(frontier)
#db_logic.save_page_binary("https://www.gov.si/")
#db_logic.save_page_data(1, ".pdf")
html_hash.close()
urls_file.close()




#driver.get(robots_url)
#robots_txt = driver.find_element(By.TAG_NAME, "pre").text