import json
import re
import copy
from bs4 import BeautifulSoup, NavigableString, Comment, Tag
class RoadRunner:
    def __init__(self):
        pass

    #def test_method(self):
    #   print("Test method called successfully.")

    def extract_data(self, html1, html2):
        soup1 = self.prepare_soup(html1)
        soup2 = self.prepare_soup(html2)
        wrapper = self.tokenize_and_compare(str(soup1), str(soup2))
        
        extracted_data = {
            #'html1': str(soup1),
            #'html2': str(soup2),
            'wrapper': wrapper
        }
        json_data = json.dumps(extracted_data, ensure_ascii=False, indent=4)
        print(json_data)
        return extracted_data
    
    def prepare_soup(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        self.decompose_unwanted(soup)
        self.clean_soup(soup)

        return soup
    
    def decompose_unwanted(self, soup):
        for element in soup.find_all(['script', 'style', 'meta']):
            element.decompose()

        comments = soup.findAll(string=lambda text: isinstance(text, Comment))
        # Remove comments.
        [comment.extract() for comment in comments]

    def clean_soup(self, soup):
        stack = [soup]
        while stack:
            current = stack.pop()
            if isinstance(current, BeautifulSoup):
                stack.extend(current.contents)
            elif isinstance(current, NavigableString):
                if current.string.isspace():
                    current.extract()
                else:
                    current.replace_with(current.string.strip())
            elif current:
                stack.extend(list(current.children))

    def tokenize_and_compare(self, html1, html2):
        tokens1 = self.tokenize(html1)
        tokens2 = self.tokenize(html2)

        wrapper = self.road_runner(tokens1, tokens2)
        return wrapper

    def tokenize(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        tokens = []
        for element in soup.recursiveChildGenerator():
            if isinstance(element, str):
                if element.strip():
                    tokens.append(element.strip())
            else:
                if element.name:
                    # Capture the tag with its attributes
                    #attrs = ''.join([f' {k}="{v}"' for k, v in element.attrs.items()])
                    #tokens.append(f"<{element.name}{attrs}>")
                    tokens.append(f"<{element.name}>")
                    if element.contents:
                        tokens.append(f"</{element.name}>")
        return tokens
    
    def match_structures(self, soup1, soup2):
        if soup1.name != soup2.name:
            return False
        for s1, s2 in zip(soup1.contents, soup2.contents):
            if isinstance(s1, NavigableString) and isinstance(s2, NavigableString):
                if s1 != s2:
                    s1.replace_with(self.generalize_strings(str(s1), str(s2)))
            elif s1.name == s2.name:
                self.match_structures(s1, s2)
    
    def road_runner(self, tokens1, tokens2):
        index1 = 0
        index2 = 0
        wrapper = []

        while index1 < len(tokens1) and index2 < len(tokens2):
            if tokens1[index1] == tokens2[index2]:
                wrapper.append(tokens1[index1])
                index1 += 1
                index2 += 1
            else:
                # Check if skipping a token in tokens1 aligns them
                if index1 + 1 < len(tokens1) and tokens1[index1 + 1] == tokens2[index2]:
                    index1 += 1
                # Check if skipping a token in tokens2 aligns them
                elif index2 + 1 < len(tokens2) and tokens1[index1] == tokens2[index2 + 1]:
                    index2 += 1
                else:
                    # If no direct or single-skip alignment is found, skip both
                    index1 += 1
                    index2 += 1

        return ' '.join(wrapper)  # Joining all tokens into a single string with spaces


    def generalize_strings(self, str1, str2):
        # Pattern to detect if the string contains mainly digits
       
        if str1 != str2:
            return ".*"
        return str1  # Return the original string if they are the same
