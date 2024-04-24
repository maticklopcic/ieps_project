import json
from bs4 import BeautifulSoup, NavigableString, Comment, Tag
class RoadRunner:
    def __init__(self):
        self.ignore_tags = ["b", "script", "br", "em", "hr"]
        self.self_closing_tags = ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"]

    #def test_method(self):
    #   print("Test method called successfully.")

    def extract_data(self, html1, html2):
        # parses HTML + extracts data
        soup1 = self.prepare_soup(html1)
        soup2 = self.prepare_soup(html2)
        wrapper = self.road_runner(soup1, soup2)

        extracted_data = {
            #'html1': str(soup1),
            #'html2': str(soup2),
            'wrapper': wrapper
        }
        
        # LEPSI IZPIS
        #print(self.pretty_format(wrapper))
        #return wrapper
    
        # MAL MANJ LEPSI IZPIS
        json_data = json.dumps(extracted_data, ensure_ascii=False, indent=4)
        print(json_data)
        return extracted_data
    
    def pretty_format(self, wrapper, indent=0):
        # lepsi izpis HTML wrapperja
        lines = []
        tokens = wrapper.split()
        i = 0
        while i < len(tokens):
            if tokens[i].startswith('<') and not tokens[i].startswith('</'):
                # Handle opening tag and potentially closing tag on same line
                tag_content = [tokens[i]]  # Opening tag
                i += 1
                while i < len(tokens) and not tokens[i].startswith('<'):
                    tag_content.append(tokens[i])  # Content between tags
                    i += 1
                if i < len(tokens) and tokens[i].startswith('</'):
                    tag_content.append(tokens[i])  # Closing tag
                    i += 1
                lines.append(' ' * indent + ' '.join(tag_content))
            else:
                # This case handles free floating text nodes or misplaced tokens
                lines.append(' ' * indent + tokens[i])
                i += 1
        return '\n'.join(lines)
    
    def prepare_soup(self, html_content):
        # soup object created + removed uwanted elements
        soup = BeautifulSoup(html_content, 'html.parser')
        self.decompose_unwanted(soup)
        #self.clean_soup(soup)

        return soup
    
    def decompose_unwanted(self, soup):
        # removes specified tags from the soup object
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
        # HTML contetn into structured tokens
        tokens1 = self.tokenize(html1)
        tokens2 = self.tokenize(html2)

        return self.road_runner(tokens1, tokens2)

    def tokenize(self, html):
        # parse HTML to create a list of tokens representhig strcture
        soup = BeautifulSoup(html, 'html.parser')
        tokens = []
        # iterate over all elements in HTML, generating tokens for each element
        for element in soup.recursiveChildGenerator():
            if isinstance(element, Tag):
                # generate tokens for opening tag
                open_tag = f"<{element.name}>"
                tokens.append(open_tag)
                # if tag contains a string, add it as a separate token, trimmed of excess whitespace
                if element.string:
                    tokens.append(element.string.strip())
                # generate tokens for closing tag
                tokens.append(f"</{element.name}>")
                # non-self-closing tags have explicit closing tags to mirror HTML structure correctly
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
        # checks for repeating sequence of tokens
        start_tag = tokens[index]
        count = 1
        i = index + 1
        # iterate through tokens until we match all opening and corresponding closing tags
        while i < len(tokens) and count > 0:
            if tokens[i] == start_tag:
                count += 1
            elif tokens[i] == f"</{start_tag[1:]}":
                count -= 1
            i += 1
        # returns sequence of repeating tokens and the next index to continue processing
        return tokens[index:i], i
    
    # format sequence of repeating tokens for readability
    def format_repeating(self, tokens):
        return f"({tokens[0]} ... {tokens[-1]})?"

    # combine two repeating sequences into a single, merged representation
    def merge_repeating(self, repeat1, repeat2):
        return f"Merge({repeat1[0]} ... {repeat1[-1]}, {repeat2[0]} ... {repeat2[-1]})?"
    
    def road_runner(self, tokens1, tokens2):
        # compares HTML structures + identify common patterns
        if tokens1.name != tokens2.name:
            # mismatch returns #PCDATA
            return f"<{tokens1.name}> #PCDATA </{tokens1.name}>"
        result = [f"<{tokens1.name}>"]
        # procedes only if both elements are not n the ognore list + not self closing
        if tokens1.name not in self.self_closing_tags and tokens1.name not in self.ignore_tags:
            # compare child eleemnts
            children1 = list(tokens1.children)
            children2 = list(tokens2.children)
            i, j = 0, 0
            while i < len(children1) and j < len(children2):
                # Handle direct text comparisons or recurse into nested tags
                if isinstance(children1[i], NavigableString) or isinstance(children2[j], NavigableString):
                    # Compare stripped text content
                    if str(children1[i]).strip() != str(children2[j]).strip():
                        result.append("#PCDATA")
                    else:
                        result.append(str(children1[i]).strip())
                    i += 1
                    j += 1
                else:
                    # Recursive call to handle nested tag structures
                    result.append(self.road_runner(children1[i], children2[j]))
                    i += 1
                    j += 1
            result.append(f"</{tokens1.name}>")
        return ' '.join(result)
    
    