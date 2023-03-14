from lxml.etree import Element
from typing import List
import spacy
import nltk
nltk.download('punkt')
import re

from .config import config

nlp = spacy.load("en_core_web_sm")

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

BOILERPLATE = [
    "This preprint has been reviewed by subject experts for *Review Commons*",
    "Content has not been altered except for formatting.",
    "Learn more at [Review Commons](https://reviewcommons.org)",
    "### Referee \#",
    "### Reviewer \#",
    "#### Evidence, reproducibility and clarity",
    "**Minor",
    "**Major",
    "#### Significance",
]


def filtering(docs: List[str]) -> List[str]:
    filtered = filter(lambda p: len(p) >= config.min_length, docs)
    filtered = filter(lambda p: not any(b in p for b in BOILERPLATE), filtered)
    filtered = list(filtered)
    return filtered


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
    filtered = filtering(para)
    return filtered


def split_sentences(text: str) -> List[str]:
    """Split text into sentences.
    Args:   
        text: The text to split into sentences.
    Returns:
        A list of sentences.
    """
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    filtered = filtering(sentences)
    return filtered


def split_sentences_nltk(text: str) -> List[str]:
    """Split text into sentences with nltk
    Args:   
        text: The text to split into sentences.
    Returns:
        A list of sentences.
    """
    sentences = nltk.sent_tokenize(text)
    filtered = filtering(sentences)
    return filtered


doi_str_re = re.compile(r'^10_\d{4,9}-[-._;()/:A-Z0-9]+$', re.IGNORECASE)
