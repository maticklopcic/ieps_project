import re
from pathlib import Path


class Regex:
    def __init__(self) -> None:
        pass

    def rtv(self, rtv1_html_content, rtv2_html_content):
        title_pattern = r'<h1[^>]*>(.*?)</h1>'
        author_date_pattern = r'<strong>([^<]+)</strong>\|\s*([\d]{1,2}\.\s*[a-zA-Z]+\s*[\d]{4}\s*ob\s*[\d]{1,2}:[\d]{2})'
        subtitle_pattern = r'<div class="subtitle">([^<]+)</div>'
        lead_pattern = r'<p class="lead">([^<]+)</p>'
        
        titles1 = re.findall(title_pattern, rtv1_html_content)
        titles2 = re.findall(title_pattern, rtv2_html_content)

        authors_dates1 = re.search(author_date_pattern, rtv1_html_content)
        authors_dates2 = re.search(author_date_pattern, rtv2_html_content)

        subtitles1 = re.findall(subtitle_pattern, rtv1_html_content)
        subtitles2 = re.findall(subtitle_pattern, rtv2_html_content)

        lead1 = re.findall(lead_pattern, rtv1_html_content)
        lead2 = re.findall(lead_pattern, rtv2_html_content)

        if authors_dates1:
            author1 = authors_dates1.group(1)
            publishedTime1 = authors_dates1.group(2)

        if authors_dates2:
            author2 = authors_dates2.group(1)
            publishedTime2 = authors_dates2.group(2)

        extracted_info = {
            "TITLES": {"RTV1": titles1, "RTV2": titles2},
            "AUTHOR": {"RTV1": author1, "RTV2": author2},
            "PUBLISHED_TIME": {"RTV1": publishedTime1, "RTV2": publishedTime2},
            "SUBTITLES": {"RTV1": subtitles1, "RTV2": subtitles2},
            "LEADS": {"RTV1": lead1, "RTV2": lead2}
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
