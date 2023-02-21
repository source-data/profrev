from typing import List
from dataclasses import dataclass, field, InitVar

from .api_tools import EEB
from .utils import split_paragraphs

"""Classes to retrieve the peer review process including the individual referee reports linked to a preprint specified by its DOI."""


class ReviewProcess:

    api = EEB()

    """A class to represent the review process for an article based on the response of the EEB API."""
    def __init__(self, doi: str) -> None:
        self.doi = doi
        response = self.api.get_referee_reports(doi)
        self.reviews = self._reviews(response)

    def _reviews(self, response: dict) -> List['Review']:
        """Get the referee reports for the article."""
        review_process_reviews = response['review_process']['reviews']
        reviews = [Review(review=r) for r in review_process_reviews]
        return reviews


@dataclass
class Review:
    """A class to represent a referee report from the EEB API response."""
    posting_date: str = field(default="")  #  "2020-09-09T12:18:53.424343+00:00",
    hypothesis_id:str = field(default="")    # "oDimTPKWEeqldYv8lyZT3A",
    review_idx: str = field(default="")    # "1",
    tags: List[str] = ""    # ["PeerReviewed"],
    related_article_uri: str = field(default="")    # "https://www.biorxiv.org/content/10.1101/2020.05.14.095968v1",
    highlight: str  = ""   # "...",
    elated_article_doi: str = field(default="")    # "10.1101/2020.05.14.095968",
    text: str = field(default="")    # "..."
    reviewed_by: str = field(default="")    # "review commons",
    link_html: str = field(default="")    # "https://hypothes.is/a/oDimTPKWEeqldYv8lyZT3A",
    link_json: str = field(default="")    # "https://hypothes.is/api/annotations/oDimTPKWEeqldYv8lyZT3A",
    doi: str = field(default="")    # "10.15252/rc.2022492035",
    link_incontext: str = field(default="")    # "https://hyp.is/oDimTPKWEeqldYv8lyZT3A/www.biorxiv.org/content/10.1101/2020.05.14.095968v1"

    review: InitVar = None

    def __post_init__(self, review: dict):
        """Parse the json dict to the class attributes.
        
        Example of review process dict return by the EEB API:

        review_process: {
            reviews: [
                {
                    posting_date: "2020-09-09T12:18:53.424343+00:00",
                    hypothesis_id: "oDimTPKWEeqldYv8lyZT3A",
                    review_idx: "1",
                    tags: ["PeerReviewed"],
                    related_article_uri: "https://www.biorxiv.org/content/10.1101/2020.05.14.095968v1",
                    highlight: "...",
                    elated_article_doi: "10.1101/2020.05.14.095968",
                    text: "..."
                    reviewed_by: "review commons",
                    link_html: "https://hypothes.is/a/oDimTPKWEeqldYv8lyZT3A",
                    link_json: "https://hypothes.is/api/annotations/oDimTPKWEeqldYv8lyZT3A",
                    doi: "10.15252/rc.2022492035",
                    link_incontext: "https://hyp.is/oDimTPKWEeqldYv8lyZT3A/www.biorxiv.org/content/10.1101/2020.05.14.095968v1"
                },
                {},
                {}
            ],
            response: {},
            annot: []
        },
        """
        self.posting_date = review['posting_date']
        self.hypothesis_id = review['hypothesis_id']
        self.review_idx = review['review_idx']
        self.tags = review['tags']
        self.related_article_uri = review['related_article_uri']
        self.highlight = review['highlight']
        self.elated_article_doi = review['related_article_doi']
        self.text = review['text']
        self.reviewed_by = review['reviewed_by']
        self.link_html = review['link_html']
        self.link_json = review['link_json']
        self.doi = review.get('doi', '')  # doi is not always present
        self.link_incontext = review['link_incontext']

    def get_paragraphs(self):
        """Get the paragraphs of the text of the review."""
        return split_paragraphs(self.text)