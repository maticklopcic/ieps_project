import json
from bs4 import BeautifulSoup, NavigableString, Comment, Tag
class RoadRunner:
    def __init__(self):
        self.ignore_tags = ["b", "script", "br", "em", "hr"]
        self.self_closing_tags = ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"]

    #def test_method(self):
    #   print("Test method called successfully.")

    def extract_data(self, html1, html2):
        soup1 = self.prepare_soup(html1)
        soup2 = self.prepare_soup(html2)
        wrapper = self.road_runner(soup1, soup2)

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
        #self.clean_soup(soup)

        return soup
    
    def decompose_unwanted(self, soup):
        for tag in  self.ignore_tags + ['script', 'style', 'meta']:
            for element in soup.find_all(tag):
                element.decompose()

        comments = soup.findAll(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()

    """
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
    """

    def tokenize_and_compare(self, html1, html2):
        tokens1 = self.tokenize(html1)
        tokens2 = self.tokenize(html2)

        return self.road_runner(tokens1, tokens2)

    def tokenize(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        tokens = []
        
        for element in soup.recursiveChildGenerator():
            if isinstance(element, Tag):
                open_tag = f"<{element.name}>"
                tokens.append(open_tag)
                if element.string:
                    tokens.append(element.string.strip())
                tokens.append(f"</{element.name}>")
                if element.name not in self.self_closing_tags:
                    tokens.append(f"</{element.name}>")
        return tokens

    """
    def match_structures(self, soup1, soup2):
        if soup1.name != soup2.name:
            return False
        for s1, s2 in zip(soup1.contents, soup2.contents):
            if isinstance(s1, NavigableString) and isinstance(s2, NavigableString):
                if s1 != s2:
                    s1.replace_with(self.generalize_strings(str(s1), str(s2)))
            elif s1.name == s2.name:
                self.match_structures(s1, s2)
    """
    def check_repeating(self, tokens, index):
        start_tag = tokens[index]
        count = 1
        i = index + 1
        while i < len(tokens) and count > 0:
            if tokens[i] == start_tag:
                count += 1
            elif tokens[i] == f"</{start_tag[1:]}":
                count -= 1
            i += 1
        return tokens[index:i], i
    
    def format_repeating(self, tokens):
        return f"({tokens[0]} ... {tokens[-1]})?"

    def merge_repeating(self, repeat1, repeat2):
        return f"Merge({repeat1[0]} ... {repeat1[-1]}, {repeat2[0]} ... {repeat2[-1]})?"
    
    def road_runner(self, tokens1, tokens2):
        if tokens1.name != tokens2.name:
            return f"<{tokens1.name}> #PCDATA </{tokens1.name}>"
        result = [f"<{tokens1.name}>"]
        if tokens1.name not in self.self_closing_tags and tokens1.name not in self.ignore_tags:
            children1 = list(tokens1.children)
            children2 = list(tokens2.children)
            i, j = 0, 0
            while i < len(children1) and j < len(children2):
                if isinstance(children1[i], NavigableString) or isinstance(children2[j], NavigableString):
                    if str(children1[i]).strip() != str(children2[j]).strip():
                        result.append("#PCDATA")
                    else:
                        result.append(str(children1[i]).strip())
                    i += 1
                    j += 1
                else:
                    result.append(self.road_runner(children1[i], children2[j]))
                    i += 1
                    j += 1
            result.append(f"</{tokens1.name}>")
        return ' '.join(result)
    
    