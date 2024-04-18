from pathlib import Path 
from lxml import html
import json


class Xpath:
    def __init__(self) -> None:
        pass

    def overstock(self, ovs1_html_content, ovs2_html_content):
        # Parse the HTML content
        html_contents = [ovs1_html_content, ovs2_html_content]
        for html_page in html_contents:
            tree = html.fromstring(html_page)

            list_price = tree.xpath('//td[b[text()="List Price:"]]/following-sibling::td/s/text()')
            price = tree.xpath('//td[b[text()="Price:"]]/following-sibling::td/span/b/text()')
            you_save = tree.xpath('//td[b[text()="You Save:"]]/following-sibling::td/span/text()')
            #saving = you_save[0].split(" ")[0] 
            #saving_percent = you_save[0].split(" ")[1]
            content = tree.xpath('//span[@class="normal"]/text()') 
            title = tree.xpath("/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody//a/b/text()")

            for idx, title in enumerate(title):
                data = {
                    "TITLE": title,
                    "LIST_PRICE": list_price[idx],
                    "PRICE": price[idx],
                    "SAVED_AMOUNT": you_save[idx].split(" ")[0],
                    "SAVED_PERCENTAGE": you_save[idx].split(" ")[1],
                    "CONTENT": content[idx]
                }
                json_data = json.dumps(data, indent=4)
                print(json_data)
