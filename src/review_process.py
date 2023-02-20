from typing import List, Optional
from dataclasses import dataclass

from .api_tools import EEB

"""Classes to retrieve the peer review process including the individual referee reports linked to a preprint specified by its DOI."""


class ReviewProcess:

    api = EEB()

    """A class to represent the review process for an article based on the response of the EEB API."""
    def __init__(self, doi: str) -> None:
        self.doi = doi
        response = self.api.get_referee_reports(doi)
        self.referee_reports = self._referee_reports(response)

    def _referee_reports(self, response: dict) -> List['RefereeReport']:
        """Get the referee reports for the article."""
        referee_reports_list = response['review_process']['referee_reports']
        self.referee_reports = [RefereeReport(r) for r in referee_reports_list] 


@dataclass
class RefereeReport:
    """A class to represent a referee report from the EEB API response."""
    posting_date: str  #  "2020-09-09T12:18:53.424343+00:00",
    hypothesis_id:str  # "oDimTPKWEeqldYv8lyZT3A",
    review_idx: str  # "1",
    tags: List[str]  # ["PeerReviewed"],
    related_article_uri: str  # "https://www.biorxiv.org/content/10.1101/2020.05.14.095968v1",
    highlight: str  # "...",
    elated_article_doi: str  # "10.1101/2020.05.14.095968",
    text: str  # "..."
    reviewed_by: str  # "review commons",
    link_html: str  # "https://hypothes.is/a/oDimTPKWEeqldYv8lyZT3A",
    link_json: str  # "https://hypothes.is/api/annotations/oDimTPKWEeqldYv8lyZT3A",
    doi: str  # "10.15252/rc.2022492035",
    link_incontext: str  # "https://hyp.is/oDimTPKWEeqldYv8lyZT3A/www.biorxiv.org/content/10.1101/2020.05.14.095968v1"

    def __post_init__(self, review: dict) -> None:
        """Parese the json dict to the class attributes.
        
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
        self.elated_article_doi = review['elated_article_doi']
        self.text = review['text']
        self.reviewed_by = review['reviewed_by']
        self.link_html = review['link_html']
        self.link_json = review['link_json']
        self.doi = review['doi']
        self.link_incontext = review['link_incontext']
