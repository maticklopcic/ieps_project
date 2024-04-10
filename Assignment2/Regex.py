import re
from pathlib import Path


class Regex:
    def __init__(self) -> None:
        pass

    def rtv(self):
        # Example regex patterns
        title_pattern = r'<h1[^>]*>(.*?)</h1>'
        item_pattern = r'<li[^>]*>(.*?)</li>'  # Assuming items are in list elements
        price_pattern = r'\$\d+\.\d+'  # Matches prices like $19.99

        # Extract titles
        titles1 = re.findall(title_pattern, self.rtv1_html_content)
        titles2 = re.findall(title_pattern, self.rtv2_html_content)

        # Extract item lists (assuming they are within <li> tags)
        items1 = re.findall(item_pattern, self.rtv1_html_content)
        items2 = re.findall(item_pattern, self.rtv2_html_content)

        # Extract prices
        prices1 = re.findall(price_pattern, self.rtv1_html_content)
        prices2 = re.findall(price_pattern, self.rtv2_html_content)

        extracted_info = {
            "titles": {"rtv1": titles1, "rtv2": titles2},
            "items": {"rtv1": items1, "rtv2": items2},
            "prices": {"rtv1": prices1, "rtv2": prices2}
        }
        print(extracted_info)
        return extracted_info
    
    def overstock(self):
        print(self.ovs1_html_content)
        return "regex"
    
    def custom(self, html):
        return "regex"
