import sys
from bs4 import BeautifulSoup, NavigableString

def read_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def parse_html(html):
    return BeautifulSoup(html, 'html.parser')

def tokenize_html(soup):
    """Tokenizes the HTML document into a list of tags and text."""
    tokens = []
    for element in soup.recursiveChildGenerator():
        if isinstance(element, NavigableString):
            if element.strip():
                tokens.append(('TEXT', element.strip()))
        elif element.name:
            tokens.append(('TAG', element.name))
    return tokens

def align_and_handle_mismatches(tokens1, tokens2):
    """Aligns tokens from two HTML documents and handles mismatches."""
    aligned = []
    i, j = 0, 0
    while i < len(tokens1) and j < len(tokens2):
        token1, token2 = tokens1[i], tokens2[j]
        if token1 == token2:
            aligned.append(token1)
            i += 1
            j += 1
        else:
            # Handling tag mismatches by introducing optional tags
            aligned.append(('OPTIONAL', token1, token2))
            i += 1
            j += 1
    return aligned

def extract_structure(soup):
    structure = {}
    for tag in soup.find_all(True):
        path = '>'.join(parent.name for parent in tag.parents if parent.name)
        siblings = [sib.name for sib in tag.previous_siblings if not isinstance(sib, NavigableString)]
        sequence = siblings.count(tag.name)
        structure[(path, tag.name)] = max(structure.get((path, tag.name), 0), sequence)
    return structure

def generalize_structure(structure1, structure2):
    generalized = {}
    for path_tag, sequence1 in structure1.items():
        sequence2 = structure2.get(path_tag, 0)
        generalized[path_tag] = min(sequence1, sequence2)
    return generalized

def print_structure(structure):
    for (path, tag), count in structure.items():
        print(f'{path}>{tag} [{count} times]')

def create_wrapper(generalized_structure, soup):
    wrapper = {}
    for (path, tag), count in generalized_structure.items():
        if count > 0:
            # Use a generalized selector to find elements
            elements = soup.select(f'{path} {tag}')
            for element in elements:
                if element.name == 'option':  # Special handling for options
                    text = element.get_text(strip=True)
                    value = element.get('value', '')
                    text = f'{text} (Value: {value})'
                else:
                    text = ' '.join(element.stripped_strings).strip()
                
                if text:  # Make sure text is not empty
                    wrapper.setdefault(path, []).append({'tag': tag, 'text': text, 'count': count})

    # Handle title separately if it's common but not captured
    title = soup.find('title')
    if title and title.text:
        wrapper['<title>'] = [{'tag': 'title', 'text': title.text.strip(), 'count': 1}]

    return wrapper

def print_extracted_data(wrapper):
    print("\nExtracted Data:")
    for path, elements in wrapper.items():
        print(f"{path}:")
        for item in elements:
            print(f"  <{item['tag']}>: '{item['text']}' ({item['count']} times)")

def RoadRunner(html_content1, html_content2):
    soup1 = parse_html(html_content1)
    soup2 = parse_html(html_content2)
    
    # Extract structures and then generalize
    structure1 = extract_structure(soup1)
    structure2 = extract_structure(soup2)
    generalized_structure = generalize_structure(structure1, structure2)
    
    # Print the generalized structure
    print("Generalized Structure:")
    print_structure(generalized_structure)
    
    # Create the wrapper
    wrapper = create_wrapper(generalized_structure, soup1)
    
    # Print the wrapper with actual text
    print_extracted_data(wrapper)

    return wrapper

# Entry point
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python RoadRunner.py <html_file1> <html_file2>")
        sys.exit(1)
    
    html_content1 = read_html(sys.argv[1])
    html_content2 = read_html(sys.argv[2])
    RoadRunner(html_content1, html_content2)
