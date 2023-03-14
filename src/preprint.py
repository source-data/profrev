from dataclasses import dataclass, field, InitVar, asdict
from lxml.etree import XMLParser, parse, Element
from copy import deepcopy
from tenacity import retry, stop_after_attempt, wait_fixed
import requests
import json
from io import StringIO
from pathlib import Path
from typing import List, Callable, Dict, Any, Optional, Tuple

from .api_tools import BioRxiv
from .utils import innertext
from .config import config

# JATS XML parser
# not sure where DTD should live...
JATS_PARSER = XMLParser(load_dtd=True, no_network=True, recover=True) # https://lxml.de/resolvers.html

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

    data: InitVar[Optional[Dict[str, Any]]] = None

    def __post_init__(self, data: Optional[Dict[str, Any]]):
        if data:
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


class Preprint:
    """Parse the JATS XML to extract metadata and full text of a bioRixv preprint.

    Attributes:
        doi: The DOI of the preprint.
        biorxiv_meta: The metadata of the preprint.
        sections: The sections of the preprint.
    """

    def __init__(self, doi: Optional[str] = None):
        """Initialize the Preprint object.
        """
        self.doi = doi
        if doi is not None:
            self.biorxiv_meta, self.sections = self._from_biorxiv_api(doi)
        else:
            self.biorxiv_meta = None
            self.sections = {
                "introduction": "",
                "results": "",
                "result_headings": "",
                "figures": "",
                "fig_titles": "",
                "methods": "",
                "discussion": ""
            }


    def _from_biorxiv_api(self, doi: str) -> Tuple[BioRxivMetadata, Dict[str, str]]:
        """Initialize the Preprint object from the bioRxiv API.
        Args:
            doi: The DOI of the preprint.
        """
        response = BioRxiv().get_preprint(doi)
        biorxiv_meta = BioRxivMetadata(data=response)
        xml_source = response['jatsxml']  # nice! For ex jatsxml: "https://www.biorxiv.org/content/early/2018/06/05/339747.source.xml"
        xml = self.get_jatsxml(xml_source)
        sections = {
            "introduction": self._introduction(xml),
            "results": self._results(xml),
            "result_headings": self._result_headings(xml),
            "figures": self._figures(xml),
            "fig_titles": self._fig_titles(xml),
            "methods": self._methods(xml),
            "discussion": self._discussion(xml)
        }
        return biorxiv_meta, sections

    def save(self, dir: Path):
        if any(self.sections.values()):
            for sec, content in self.sections.items():
                sec_file = dir / f'{sec}.txt'
                with open(sec_file, 'w') as f:
                    f.write(content)
        else:
            raise ValueError('No sections to save')
        if self.biorxiv_meta is not None:
            metadata_file = dir / 'metadata.json'
            with open(metadata_file, 'w') as jf:
                biorxiv_meta = self.biorxiv_meta.asdict()
                json.dump(biorxiv_meta, jf, indent=4)
        else:
            raise ValueError('No metadata to save')

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
    def result_headings(self):
        return self.sections['result_headings']
    
    @property
    def figures(self):
        return self.sections['figures']

    @property
    def fig_titles(self):
        return self.sections['fig_titles']

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
        return self._extract_section('//sec/title[re:match(text(), "^result", "i")]/..//p', xml, internal_element_to_remove='//fig')

    def _result_headings(self, xml: Element) -> str:
        """Extract the results headings section of the preprint using the JATS XML and the appropriate XPath."""
        # Results, Results and Discussion
        return self._extract_section('//sec/title[re:match(text(), "^result", "i")]/../sec/title', xml)
    
    def _figures(self, xml: Element) -> str:
        """Extract the figures section of the preprint using the JATS XML and the appropriate XPath."""
        return self._extract_section('//fig/caption', xml, remove_newlines_first=True)
    
    def _fig_titles(self, xml: Element) -> str:
        """Extract the figure title section of the preprint using the JATS XML and the appropriate XPath."""
        return self._extract_section('//fig/caption/title', xml)

    def _methods(self, xml: Element) -> str:
        """Extract the methods section of the preprint using the JATS XML and the appropriate XPath."""
        return self._extract_section('//sec/title[re:match(text(), "methods", "i")]/..//p', xml)

    def _discussion(self, xml:Element) -> str:
        """Extract the discussion section of the preprint using the JATS XML and the appropriate XPath."""
        # Has to start with discussion to disambiguate from "Results and Discussion" combined section
        return self._extract_section('//sec/title[re:match(text(), "^discussion", "i")]/..//p', xml)

    def _extract_section(self, xpath: str, xml: Element, remove_newlines_first:bool = False, internal_element_to_remove: str='') -> str:
        """Extract a section of the preprint using the JATS XML and the appropriate XPath."""
        if internal_element_to_remove:
            xml = deepcopy(xml)  # don't modify the original xml
            internal_elements = xml.xpath(internal_element_to_remove, namespaces={"re": "http://exslt.org/regular-expressions"})
            for el in internal_elements:
                el.getparent().remove(el)
        elements = xml.xpath(xpath, namespaces={"re": "http://exslt.org/regular-expressions"})  # namespace prefix to enable regex usage in XPath
        return self._extract_text(elements, remove_newlines_first)

    def _extract_text(self, elements: List[Element], remove_newlines_first: bool = False) -> str:
        """Extract the innertext from list of xml etree Elements. Paragraphs are joined with double newline.
        Args:
            elements: The list of etree Elements.
            remove_newlines_first: Whether to remove newlines from the text of each element first.
        """
        if remove_newlines_first:
            text_elements = []
            for el in elements:
                text = innertext(el)
                if text: 
                    text = text.replace('\n', ' ')
                    text_elements.append(text)
            return '\n\n'.join(text_elements)
        else:
            return '\n\n'.join([innertext(el) for el in elements])
    
    def get_chunks(self, chunking_fn: Callable, sections: str = config.sections) -> List[str]:
        """Return the paragraphs of a sections of the preprint.
        Args:L
            chunking_fn: The function to use to chunk the text.
            sections: The sections to extract. Can be a combination of 'introduction', 'results', 'methods', 'discussion' using the '+' operator.
        Returns:
            A list of chunks.
        """
        section_list = sections.split('+')
        chunks = []
        for section in section_list:
            chunks += chunking_fn(self.sections[section])
        return chunks
