from lxml.etree import Element
from typing import List, Callable
import re


# a function to extract the inner text from the JATS XML using itertext()
def innertext(el: Element) -> str:
    """Extract the inner text from an XML element.
    Args:
        el: The XML element to extract the inner text from.
        encoding: The encoding to use to decode the inner text.
    Returns:
        The inner text of the XML element.
    """
    txt = ''.join(el.itertext())
    return txt

# a function that replaces dots by underscores and slashes by dashes
def stringify_doi(doi: str) -> str:
    """Clean a DOI by replacing dots by underscores and slashes by dashes.
    Args:
        doi: The DOI to clean.
    Returns:
        The cleaned DOI.
    """
    doi = doi.replace('.', '_')
    doi = doi.replace('/', '-')
    return doi

def split_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs.
    Args:   
        text: The text to split into paragraphs.
    Returns:
        A list of paragraphs.
    """
    text = re.sub('\r\n', '\n\n', text)
    text = re.sub('\n +', '\n', text)
    para = text.split('\n')
    para = [p.strip() for p in para]
    filtered = filter(lambda p: len(p) >= 70, para)
    filtered = list(filtered)
    return filtered

doi_str_re = re.compile(r'^10_\d{4,9}-[-._;()/:A-Z0-9]+$', re.IGNORECASE)
