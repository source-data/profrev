from pathlib import Path

from api_tools import EEB, BioRxiv

"""This module contains classes to generate the corpus of article and referee reports."""

# a function that replaces dots by underscores and slashes by dashes
def _clean_doi(doi: str) -> str:
    """Clean a DOI by replacing dots by underscores and slashes by dashes.
    Args:
        doi: The DOI to clean.
    Returns:
        The cleaned DOI.
    """
    doi = doi.replace('.', '_')
    doi = doi.replace('/', '-')
    return doi


class RefereeReports: 
    """A class to represent a referee report."""
    def __init__(self, doi) -> None:
       self.doi = doi
       self.referee_reports = self._download()
       self.api = EEB()

    def _downlaod(self) -> None:
        """Download the referee report from the Early Evidence Base API."""
        ref_reps = self.api.get_referee_reports(self.doi)

    def save(self, directory: str) -> None:
        """Save the referee report to a file.
        Args:
            directory: The directory to save the file in.
        """
        doi_dir = Path(directory) / _clean_doi(self.doi)
        doi_dir.mkdir(parents=True, exist_ok=True)
        # save the individual referee reports to individual subdirectories
        for i, ref_rep in enumerate(self.referee_reports):
            ref_rep_dir = doi_dir / f'referee_report_{i}'
            ref_rep_dir.mkdir(parents=True, exist_ok=True)
            # save the referee report to a file named 'content.txt'
            ref_rep_file = ref_rep_dir / 'content.txt'
            with open(ref_rep_file, 'w') as f:
                f.write(ref_rep)

class Article:
    """A class to represent an article."""
    def __init__(self, doi) -> None:
        self.doi = doi
        self.article = self._download()
        self.api = BioRxiv()

    def _download(self) -> None:
        """Download the article from the Early Evidence Base API."""
        article = self.api.get_article(self.doi)

    def save(self, directory: str) -> None:
        """Save the article to a file.
        Args:
            directory: The directory to save the file in.
        """
        doi_dir = Path(directory) / _clean_doi(self.doi)
        doi_dir.mkdir(parents=True, exist_ok=True)
        # save the article to a file named 'article.txt'
        article_file = doi_dir / 'article.txt'
        with open(article_file, 'w') as f:
            f.write(self.article)




