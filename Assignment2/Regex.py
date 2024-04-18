import json
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
        content_text_pattern1 = r'^(?:.*)<div class="article-body">|<div class="gallery">(?:.*)$|<script[^>]*>.*?</script>|<[^>]+>'

        titles1 = re.findall(title_pattern, rtv1_html_content)
        titles2 = re.findall(title_pattern, rtv2_html_content)

        authors_dates1 = re.search(author_date_pattern, rtv1_html_content)
        authors_dates2 = re.search(author_date_pattern, rtv2_html_content)

        subtitles1 = re.findall(subtitle_pattern, rtv1_html_content)
        subtitles2 = re.findall(subtitle_pattern, rtv2_html_content)

        lead1 = re.findall(lead_pattern, rtv1_html_content)
        lead2 = re.findall(lead_pattern, rtv2_html_content)
        #print("LEAD1:", lead1)
        #print("LEAD2:", lead2)


        if authors_dates1:
            author1 = authors_dates1.group(1)
            publishedTime1 = authors_dates1.group(2)

        if authors_dates2:
            author2 = authors_dates2.group(1)
            publishedTime2 = authors_dates2.group(2)

        
        content1 = re.sub(content_text_pattern1, '', rtv1_html_content, flags=re.S)
        cleaned_lines1 = [line.strip() for line in content1.split('\n') if line.strip()]
        content1 = ' '.join(cleaned_lines1)
        #print("CONTENT:", content1)
        content2 = re.sub(content_text_pattern1, '', rtv2_html_content, flags=re.S)
        cleaned_lines2 = [line.strip() for line in content2.split('\n') if line.strip()]
        content2 = ' '.join(cleaned_lines2)
        #print("CONTENT:", content2)

        """content1 = re.findall(content_text_pattern1, rtv1_html_content)
        content2 = re.findall(content_text_pattern1, rtv2_html_content)
        for i in range(len(content1)):
            content1[i] = self.process_html_content(content1[i])
        for i in range(len(content2)):
            content2[i] = self.process_html_content(content2[i])
        if not content1:
            content1 = re.findall(content_text_pattern2, rtv1_html_content)
        if not content2:
            content2 = re.findall(content_text_pattern2, rtv2_html_content)"""
        #print("CONTENT1:", content1)
        #print("CONTENT2:", content2)

        extracted_info = {
            "RTV1": [],
            "RTV2": []
        }

        extracted_info["RTV1"].append({
            "TITLE": titles1[0],
            "AUTHOR": author1,
            "PUBLISHED_TIME": publishedTime1,
            "SUBTITLE": subtitles1[0],
            "LEAD": lead1[0],
            "CONTENT": content1
        })

        extracted_info["RTV2"].append({
            "TITLE": titles2[0],
            "AUTHOR": author2,
            "PUBLISHED_TIME": publishedTime2,
            "SUBTITLE": subtitles2[0],
            "LEAD": lead2[0],
            "CONTENT": content2
        })

        json_data = json.dumps(extracted_info, ensure_ascii=False, indent=4)
        print(json_data)
        return
    
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
        #print("CONTENT IN OVS1:")
        for i in range(len(content1)):
            content1[i] = content1[i].replace("\n", " ")
            #print(content1[i] + "\n\n")
        content2 = re.findall(content_pattern, ovs2_html_content)
        #print("CONTENT IN OVS2:")
        for i in range(len(content2)):
            content2[i] = content2[i].replace("\n", " ")
            #print(content2[i] + "\n\n")
        extracted_info = {
            "OVS1": [],
            "OVS2": []
        }
        for i in range(len(titles1)):
            extracted_info["OVS1"].append({
                "TITLE": titles1[i],
                "LIST_PRICE": list_prices1[i],
                "PRICE": prices1[i],
                "SAVED_AMOUNT": saved1[i].split(" ")[0],
                "SAVED_PERCENTAGE": saved1[i].split(" ")[1],
                "CONTENT": content1[i]
            })

        for i in range(len(titles2)):
            extracted_info["OVS2"].append({
                "TITLE": titles2[i],
                "LIST_PRICE": list_prices2[i],
                "PRICE": prices2[i],
                "SAVED_AMOUNT": saved2[i].split(" ")[0],
                "SAVED_PERCENTAGE": saved2[i].split(" ")[1],
                "CONTENT": content2[i]
            })
        
        json_data = json.dumps(extracted_info, indent=4)
        print(json_data)
        #print(extracted_info)
        return
    
    def custom(self, custom1_html_content, custom2_html_content):
        title_pattern = r'<title>([^<]+)</title>'
        title1 = re.search(title_pattern, custom1_html_content)
        title2 = re.search(title_pattern, custom2_html_content)
        

        data_pattern = re.compile(
            r'<score-pairs-deprecated.*?audiencescore="(\d+)".*?criticsscore="(\d+)".*?</score-pairs-deprecated>\s*'
            r'<span class="p--small" data-qa="discovery-media-list-item-title">\s*(.*?)\s*</span>\s*'
            r'<span class="smaller" data-qa="discovery-media-list-item-start-date">\s*(.*?)\s*</span>'
            , re.DOTALL
        )
        matches1 = data_pattern.findall(custom1_html_content)
        matches2 = data_pattern.findall(custom2_html_content)
        movies1 = []
        for match in matches1:
            audience_score, critic_score, title, streaming_date = match
            movie_info = {
                "title": title,
                "streaming_date": streaming_date,
                "audience_score": audience_score + "%",
                "critic_score": critic_score + "%"
            }
            movies1.append(movie_info)
        json_output1 = json.dumps(movies1, indent=4, ensure_ascii=False)
        print("Title1:", title1.group(1))
        print(json_output1)
        
        movies2 = []
        for match in matches2:
            audience_score, critic_score, title, streaming_date = match
            movie_info = {
                "title": title,
                "streaming_date": streaming_date,
                "audience_score": audience_score + "%",
                "critic_score": critic_score + "%"
            }
            movies2.append(movie_info)

        # Convert list of dictionaries to JSON
        json_output2 = json.dumps(movies2, indent=4)
        print("Title2:", title2.group(1))
        print(json_output2)


        #print("Custom1:", custom1_html_content)
        #print("Custom2:", custom2_html_content)
        return
    
    def process_html_content(self, html_content):
        processed_content = re.sub(r'<br\s*/?>', ' ', html_content)

        processed_content = re.sub(r'<iframe.*?</iframe>', '', processed_content, flags=re.DOTALL)

        processed_content = re.sub(r'</?strong>', '', processed_content)

        return processed_content
