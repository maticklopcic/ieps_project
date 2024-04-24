from pathlib import Path 
from lxml import html
import json

#TODO: vprasaj za " " v izpisu in \n
#porocilo ali je prevec strani
#kopiramo takst ali prilepimo sliko izhoda?

class Xpath:
    def __init__(self) -> None:
        pass

    def overstock(self, ovs1_html_content, ovs2_html_content):
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
                json_data = json.dumps(data, ensure_ascii=False, indent=4)
                print(json_data)
    
    def rtvslo(self, content1, content2):
        html_contents = [content1, content2]
        for html_page in html_contents:
            tree = html.fromstring(html_page)
            author = tree.xpath('//div/div[3]/div/header/div[3]/div[1]/strong/text()')
            timestamp = tree.xpath('normalize-space(substring-after(//div[@class="author-timestamp"]/strong/following-sibling::text()[1], "|"))')
            title = tree.xpath('//header[@class="article-header"]/h1/text()')
            #/html/body/div[9]/div[3]/div/header/h1

            subtitle = tree.xpath('//div[@class="subtitle"]/text()')
            lead = tree.xpath('//p[@class="lead"]/text()')
            content = tree.xpath('//article[@class="article"]//p/text()')

            data = {
                "TITLE": title[0],
                "AUTHOR": author[0],
                "PUBLISHED_TIME": timestamp,
                "SUBTITLE": subtitle[0],
                "LEAD": lead[0],
                "CONTENT": content
            }
            json_data = json.dumps(data, ensure_ascii=False, indent=4)
            print(json_data)
        
    def rotten_tomatoes(self, content1, content2):
        html_contents = [content1, content2]
        for html_page in html_contents:
            tree = html.fromstring(html_page)
            site_name = tree.xpath('/html/body/div[3]/main/div[1]/div[1]/div[1]/discovery-title/h1/text()')[0]
            audience_score = tree.xpath('//score-pairs-deprecated/@audiencescore')
            critics_score = tree.xpath('//score-pairs-deprecated/@criticsscore')
            title = tree.xpath('//span[@data-qa="discovery-media-list-item-title"]/text()')
            timestamp = tree.xpath('//span[@data-qa="discovery-media-list-item-start-date"]/text()')
            
            title = [t.strip() for t in title]
            timestamp = [t.strip() for t in timestamp]

            print("Page title:", site_name)
            for idx ,title in enumerate(title):
                data = {
                    "title": title,
                    "streaming_date": timestamp[idx],
                    "audience_score": audience_score[idx]+"%",
                    "critic_score": critics_score[idx]+"%"
                }   
                json_data = json.dumps(data, ensure_ascii=False, indent=4)
                print(json_data)

        