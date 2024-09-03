import hashlib
import json
import os
import tempfile
import subprocess
import sys
from bs4 import BeautifulSoup
from utilities.parsers.readability.simplifiers import normalise_text
from bs4.element import Comment, NavigableString, CData


def add_content_digest(element):
    if not is_text(element):
        element["data-content-digest"] = content_digest(element)
    return element


def content_digest(element):
    if is_text(element):
        # Hash
        trimmed_string = element.string.strip()
        if trimmed_string == "":
            digest = ""
        else:
            digest = hashlib.sha256(trimmed_string.encode('utf-8')).hexdigest()
    else:
        contents = element.contents
        num_contents = len(contents)
        if num_contents == 0:
            # No hash when no child elements exist
            digest = ""
        elif num_contents == 1:
            # If single child, use digest of child
            digest = content_digest(contents[0])
        else:
            # Build content digest from the "non-empty" digests of child nodes
            digest = hashlib.sha256()
            child_digests = list(
                filter(lambda x: x != "", [content_digest(content) for content in contents]))
            for child in child_digests:
                digest.update(child.encode('utf-8'))
            digest = digest.hexdigest()
    return digest


def is_leaf(element):
    return (element.name in ['p', 'li'])


def is_text(element):
    return isinstance(element, NavigableString)


def is_non_printing(element):
    return any(isinstance(element, _e) for _e in [Comment, CData])


def add_node_indexes(element, node_index="0"):
    # Can't add attributes to string types
    if is_text(element):
        return element
    # Add index to current element
    element["data-node-index"] = node_index
    # Add index to child elements
    for local_idx, child in enumerate(
            [c for c in element.contents if not is_text(c)], start=1):
        # Can't add attributes to leaf string types
        child_index = f"{node_index}.{local_idx}"
        add_node_indexes(child, node_index=child_index)
    return element

def plain_content(readability_content, content_digests, node_indexes):
    # Load article as DOM
    soup = BeautifulSoup(readability_content, 'html.parser')
    # Make all elements plain
    elements = plain_elements(soup.contents, content_digests, node_indexes)
    if node_indexes:
        # Add node index attributes to nodes
        elements = [add_node_indexes(element) for element in elements]
    # Replace article contents with plain elements
    soup.contents = elements
    return str(soup)


def plain_elements(elements, content_digests, node_indexes):
    # Get plain content versions of all elements
    elements = [plain_element(element, content_digests, node_indexes)
                for element in elements]
    if content_digests:
        # Add content digest attribute to nodes
        elements = [add_content_digest(element) for element in elements]
    return elements


def plain_element(element, content_digests, node_indexes):
    # For lists, we make each item plain text
    if is_leaf(element):
        # For leaf node elements, extract the text content, discarding any HTML tags
        # 1. Get element contents as text
        plain_text = element.get_text()
        # 2. Normalise the extracted text string to a canonical representation
        plain_text = normalise_text(plain_text)
        # 3. Update element content to be plain text
        element.string = plain_text
    elif is_text(element):
        if is_non_printing(element):
            # The simplified HTML may have come from Readability.js so might
            # have non-printing text (e.g. Comment or CData). In this case, we
            # keep the structure, but ensure that the string is empty.
            element = type(element)("")
        else:
            plain_text = element.string
            plain_text = normalise_text(plain_text)
            element = type(element)(plain_text)
    else:
        # If not a leaf node or leaf type call recursively on child nodes, replacing
        element.contents = plain_elements(element.contents, content_digests, node_indexes)
    return element



def simple_json_from_html_string(html: str, content_digests=False, node_indexes=False, use_is_probably_readable=False):
    # Write input HTML to temporary file so it is available to the node.js script
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", encoding="utf-8") as f_html:
        f_html.write(html)
        f_html.close()
    html_path = f_html.name

    # Call Mozilla's Readability.js Readability.parse() function via node, writing output to a temporary file
    article_json_path = f_html.name + ".json"
    jsdir = os.path.join(os.path.dirname(__file__), 'javascript')
    js_file = "ExtractArticle.js" if not use_is_probably_readable else "ExtractArticleIfReadable.js"
    try:
        subprocess.check_call(
                ["node", js_file, "-i", html_path, "-o", article_json_path], cwd=jsdir)
    except subprocess.CalledProcessError:
        return None
            

    # Read output of call to Readability.parse() from JSON file and return as Python dictionary
    with open(article_json_path, "r", encoding="utf-8") as json_file:
        input_json = json.load(json_file)

    # Deleting files after processing
    os.unlink(article_json_path)
    os.unlink(f_html.name)

    # Only keep the subset of Readability.js fields we are using (and therefore testing for accuracy of extraction)
    # NB: Need to add tests for additional fields and include them when we look at packaging this wrapper up for PyPI
    # Initialise output article to include all fields with null values
    article_json = {
        "title": None,
        "byline": None,
        "date": None,
        "content": None,
        "plain_content": None,
        "plain_text": None
    }
    # Populate article fields from readability fields where present
    if input_json:
        if "title" in input_json and input_json["title"]:
            article_json["title"] = input_json["title"]
        if "byline" in input_json and input_json["byline"]:
            article_json["byline"] = input_json["byline"]
        if "date" in input_json and input_json["date"]:
            article_json["date"] = input_json["date"]
        if "content" in input_json and input_json["content"]:
            article_json["content"] = input_json["content"]
            article_json["plain_content"] = plain_content(article_json["content"], content_digests, node_indexes)
            article_json["plain_text"] = extract_text_blocks_js(article_json["plain_content"])

    return article_json


def extract_text_blocks_js(paragraph_html):
    # Load article as DOM
    soup = BeautifulSoup(paragraph_html, 'html.parser')
    # Select all text blocks
    text_blocks = [{"text": str(s)} for s in soup.find_all(string=True)]
    return text_blocks


def extract_text_with_readability(html: str) -> str | None:
    parsed_data = simple_json_from_html_string(html, use_is_probably_readable=True)
    if parsed_data == None:
        return None
    text_parts = [text["text"] for text in parsed_data["plain_text"]]
    full_text = " ".join(text_parts)
    return full_text
