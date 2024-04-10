import sys
from Regex import Regex
from Xpath import Xpath
from RoadRunner import RoadRunner

def extract_using_regex():
    regex = Regex()
    regex.rtv()
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
        print("method: regex, xpath, or road_runner")
        sys.exit(1)

    method = sys.argv[1]
    html_content = "<html>...</html>"

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
