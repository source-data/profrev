from dataclasses import dataclass, field, InitVar, asdict
from lxml.etree import tostring, fromstring, XMLParser, parse, Element
from tenacity import retry, stop_after_attempt, wait_fixed
import requests
import json
from io import StringIO
from pathlib import Path
from typing import List

from .api_tools import BioRxiv
from .utils import innertext, split_paragraphs

# JATS XML parser
# not sure where DTD should live...
JATS_PARSER = XMLParser(load_dtd=True, no_network=True, recover=True) # https://lxml.de/resolvers.html
# namespace prefix to specif regex usage in XPath
NS_RE = {"re": "http://exslt.org/regular-expressions"}

"""
{
    doi: "10.1101/339747",
    title: "Oxygen restriction induces a viable but non-culturable population in bacteria",
    authors: "Kvich, L. A.; Fritz, B. G.; Crone, S. G.; Kragh, K. N.; Kolpen, M.; Sonderholm, M.; Andersson, M.; Koch, A.; Jensen, P. O.; Bjarnsholt, T.",
    author_corresponding: "Thomas  Bjarnsholt",
    author_corresponding_institution: "University of Copenhagen",
    date: "2018-06-05",
    version: "1",
    type: "new results",
    license: "cc_no",
    category: "microbiology",
    jatsxml: "https://www.biorxiv.org/content/early/2018/06/05/339747.source.xml",
    abstract: "Induction of....",
    published: "NA",
    server: "biorxiv"
}
"""

class Preprint:
    """Parse the JATS XML to extract metadata and full text of a bioRixv preprint.

    Attributes:
        doi: The DOI of the preprint.
        biorxiv_meta: The metadata of the preprint.
        sections: The sections of the preprint.
    """

    def __init__(self, doi: str = None):
        """Initialize the Preprint object.
        """
        self.doi = None
        self.biorxiv_meta = None
        self.sections = {}
        if doi is not None:
            self.from_biorxiv_api(doi)

    def from_biorxiv_api(self, doi: str):
        """Initialize the Preprint object from the bioRxiv API.
        Args:
            doi: The DOI of the preprint.
        """
        self.doi = doi
        response = BioRxiv().get_preprint(doi)
        self.biorxiv_meta = BioRxivMetadata(data=response)
        xml_source = response['jatsxml']
        xml = self.get_jatsxml(xml_source)
        self.sections = {
            "introduction": self._introduction(xml),
            "results": self._results(xml),
            "methods": self._methods(xml),
            "discussion": self._discussion(xml)
        }

    def save(self, dir: Path):
        for sec, content in self.sections.items():
            sec_file = dir / f'{sec}.txt'
            with open(sec_file, 'w') as f:
                f.write(content)
        metadata_file = dir / 'metadata.json'
        with open(metadata_file, 'w') as jf:
            biorxiv_meta = self.biorxiv_meta.asdict()
            json.dump(biorxiv_meta, jf, indent=4)

    def from_dir(self, dir: Path):
        self.sections = {}
        for sec_file in dir.glob('*.txt'):
            sec = sec_file.stem
            with open(sec_file, 'r') as f:
                content = f.read()
            self.sections[sec] = content
        metadata_file = dir / 'metadata.json'
        with open(metadata_file, 'r') as jf:
            biorxiv_meta = json.load(jf)
            self.biorxiv_meta = BioRxivMetadata(data=biorxiv_meta)
        self.doi = self.biorxiv_meta.doi
        return self

    @property
    def introduction(self):
        return self.sections['introduction']

    @property
    def results(self):
        return self.sections['results']

    @property
    def methods(self):
        return self.sections['methods']

    @property
    def discussion(self):
        return self.sections['discussion']

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def get_jatsxml(self, url: str) -> Element:
        """Return the JATS XML of the preprint."""
        headers = {'Accept': 'application/xml'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        xml_string = response.text
        xml_def = """<?xml version="1.0"?><!DOCTYPE article PUBLIC "-///NLM//DTD JATS (Z39.96) Journal Publishing DTD v1.1 20151215//EN" "JATS-journalpublishing1-3.dtd">"""
        xml_string = xml_def + xml_string
        xml = parse(StringIO(xml_string), JATS_PARSER)
        root = xml.getroot()
        return root

    def _introduction(self, xml: Element) -> str:
        """Extract the introduction section of the preprint using the JATS XML and the appropriate XPath."""
        return self._extract_section('//sec/title[re:match(text(), "^introduction", "i")]/..//p', xml)

    def _results(self, xml: Element) -> str:
        """Extract the results section of the preprint using the JATS XML and the appropriate XPath."""
        # Results, Results and Discussion
        return self._extract_section('//sec/title[re:match(text(), "^result", "i")]/..//p', xml)

    def _methods(self, xml: Element) -> str:
        """Extract the methods section of the preprint using the JATS XML and the appropriate XPath."""
        return self._extract_section('//sec/title[re:match(text(), "methods", "i")]/..//p', xml)

    def _discussion(self, xml:Element) -> str:
        """Extract the discussion section of the preprint using the JATS XML and the appropriate XPath."""
        # Has to start with discussion to disambiguate from "Results and Discussion" combined section
        return self._extract_section('//sec/title[re:match(text(), "^discussion", "i")]/..//p', xml)

    def _extract_section(self, xpath: str, xml: Element) -> str:
        """Extract a section of the preprint using the JATS XML and the appropriate XPath."""
        elements = xml.xpath(xpath, namespaces=NS_RE)
        return self._extract_text(elements)

    def _extract_text(self, elements: List[Element]) -> str:
        """Extract the innertext from list of xml etree Elements. Paragraphs are joined with double newline."""
        return '\n\n'.join([innertext(el) for el in elements])
    
    def get_section_paragraphs(self, section: str) -> List[str]:
        """Return the paragraphs of a section of the preprint."""
        return split_paragraphs(self.sections[section])

@dataclass
class BioRxivMetadata:
    """extract the biorxiv metadata from the API response"""
    doi: str = field(default='')
    title: str = field(default='')
    authors: str = field(default='')
    author_corresponding: str = field(default='')
    author_corresponding_institution: str = field(default='')
    date: str = field(default='')
    version: str = field(default='')
    type: str = field(default='')
    license: str = field(default='')
    category: str = field(default='')
    abstract: str = field(default='')
    published: str = field(default='')
    server: str = field(default='')

    data: InitVar = None

    def __post_init__(self, data: dict):
        # only a subset of the data fields are used
        self.doi = data['doi']
        self.title = data['title']
        self.authors = data['authors']
        self.author_corresponding = data['author_corresponding']
        self.author_corresponding_institution = data['author_corresponding_institution']
        self.date = data['date']
        self.version = data['version']
        self.type = data['type']
        self.license = data['license']
        self.category = data['category']
        self.abstract = data['abstract']
        self.published = data['published']
        self.server = data['server']

    def asdict(self):
        return asdict(self)