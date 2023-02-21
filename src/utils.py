from lxml.etree import Element, tostring, fromstring

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

# a function to clean up text by removing whitespaces between paragraphs
def clean_text(text: str) -> str:
    """Clean up text by removing whitespaces between paragraphs.
    Args:
        text: The text to clean.
    Returns:
        The cleaned text.
    """
    clean_text = re.sub('\n\s+\n', '\n\n', text)
    return clean_text

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


