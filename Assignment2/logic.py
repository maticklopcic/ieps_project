import sys
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from Regex import Regex
from Xpath import Xpath
from RoadRunner import RoadRunner
"""
paths = [
    Path('strani', 'rtvslo.si', 'Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html'),
    Path('strani', 'rtvslo.si', 'Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html'),
    Path('strani', 'overstock.com', 'jewelry01.html'),
    Path('strani', 'overstock.com', 'jewelry02.html')
]

options = FirefoxOptions()
options.add_argument("--headless")
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)
rendered_file_path = os.path.join('strani', 'rendered.txt')
os.makedirs(os.path.dirname(rendered_file_path), exist_ok=True)

html_contents = []

with open(rendered_file_path, 'w', encoding='utf-8') as file:
    for path in paths:
        file_uri = path.resolve().as_uri()
        driver.get(file_uri)
        file.write(driver.page_source + "\n\n--- End of HTML Content ---\n\n")

driver.quit()
"""
html_contents = []
file_path = os.path.join('strani', 'rendered.txt')

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    html_contents = [section for section in content.split("\n\n--- End of HTML Content ---\n\n") if section.strip()]

    print("Number of HTML contents loaded:", len(html_contents))
else:
    print("File not found:", file_path)

def extract_using_regex():
    regex = Regex()
    #regex.rtv(html_contents[0], html_contents[1])
    regex.overstock(html_contents[2], html_contents[3])
    print("Extracting using regex...")
    return []

def extract_using_xpath():
    xpath = Xpath()
    xpath
    print("Extracting using XPath...")
    return []

def extract_using_road_runner():
    road_runner = RoadRunner()
    print("Extracting using Road Runner algorithm...")
    return []

def main():
    if len(sys.argv) != 2:
        print("Usage: python logic.py [method]")
        print("method: 'A', 'B', 'C'")
        sys.exit(1)

    method = sys.argv[1]

    if method == 'A':
        result = extract_using_regex()
    elif method == 'B':
        result = extract_using_xpath()
    elif method == 'C':
        result = extract_using_road_runner()
    else:
        print("Invalid method. Use 'A', 'B', or 'C'.")
        sys.exit(1)

    print(result)

if __name__ == "__main__":
    main()
