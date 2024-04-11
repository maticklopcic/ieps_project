import re
from pathlib import Path


class Regex:
    def __init__(self) -> None:
        pass

    def rtv(self, rtv1_html_content, rtv2_html_content):
        # Example regex patterns
        title_pattern = r'<h1[^>]*>(.*?)</h1>'
        item_pattern = r'<li[^>]*>(.*?)</li>'
        price_pattern = r'\$\d+\.\d+'

        # Extract titles
        titles1 = re.findall(title_pattern, rtv1_html_content)
        titles2 = re.findall(title_pattern, rtv2_html_content)

        # Extract item lists (assuming they are within <li> tags)
        items1 = re.findall(item_pattern, rtv1_html_content)
        items2 = re.findall(item_pattern, rtv2_html_content)

        # Extract prices
        prices1 = re.findall(price_pattern, rtv1_html_content)
        prices2 = re.findall(price_pattern, rtv2_html_content)

        extracted_info = {
            "titles": {"rtv1": titles1, "rtv2": titles2},
            "items": {"rtv1": items1, "rtv2": items2},
            "prices": {"rtv1": prices1, "rtv2": prices2}
        }
        print(extracted_info)
        return extracted_info
    
    def overstock(self, ovs1_html_content, ovs2_html_content):
        title_pattern = r'<a href="http://www.overstock.com/cgi-bin/d2.cgi\?PAGE=PROFRAME&amp;PROD_ID=\d+"><b>([^<]+)</b></a><br>'
        list_prices_pattern = r'<s>([^<]+)</s>'
        price_pattern = r'<td align="right" nowrap="nowrap"><b>Price:</b></td><td align="left" nowrap="nowrap"><span class="bigred"><b>([^<]+)</b></span></td>'
        saved_pattern = r'<td align="right" nowrap="nowrap"><b>You Save:</b></td><td align="left" nowrap="nowrap"><span class="littleorange">([^<]+)</span></td>'
        content_pattern = r'<td valign="top"><span class="normal">([^<]+)<br><a href'
        
        titles1 = re.findall(title_pattern, ovs1_html_content)
        titles2 = re.findall(title_pattern, ovs2_html_content)
        
        list_prices1 = re.findall(list_prices_pattern, ovs1_html_content)
        list_prices2 = re.findall(list_prices_pattern, ovs2_html_content)
        
        prices1 = re.findall(price_pattern, ovs1_html_content)
        prices2 = re.findall(price_pattern, ovs2_html_content)

        saved1 = re.findall(saved_pattern, ovs1_html_content)
        saved2 = re.findall(saved_pattern, ovs2_html_content)
        
        content1 = re.findall(content_pattern, ovs1_html_content)
        print("CONTENT IN OVS1:")
        for i in range(len(content1)):
            content1[i] = content1[i].replace("\n", " ")
            #print(content1[i] + "\n\n")
        content2 = re.findall(content_pattern, ovs2_html_content)
        print("CONTENT IN OVS2:")
        for i in range(len(content2)):
            content2[i] = content2[i].replace("\n", " ")
            #print(content2[i] + "\n\n")

        extracted_info = {
            "TITLES": {"OVS1": titles1, "OVS2": titles2},
            "LIST_PRICES": {"OVS1": list_prices1, "OVS2": list_prices2},
            "PRICES": {"OVS1": prices1, "OVS2": prices2},
            "SAVED": {"OVS1": saved1, "OVS2": saved2},
            "CONTENT": {"OVS1": content1, "OVS2": content2}
        }
        print(extracted_info)
        return extracted_info
    
    def custom(self, html):
        return "regex"
