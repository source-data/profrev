from pathlib import Path
import json

from .review_process import ReviewProcess
from .preprint import Preprint
from .utils import stringify_doi


"""This module contains classes to generate the corpus of article and referee reports."""

class ReviewedPreprint: 
    """A class to represent a reviewed preprint and save it to disk"""
    def __init__(self, doi: str = None):
        self.doi = None
        self.review_process = None
        self.preprint = None
        if doi is not None:
            self.doi = doi
            self.review_process = ReviewProcess(self.doi)
            self.preprint = Preprint(self.doi)

    def from_objects(self, preprint: Preprint, review_process: ReviewProcess):
        self.doi = preprint.doi
        assert preprint.doi == review_process.doi, f"doi in review and preprint are discrepant: {preprint.doi} vs {review_process.doi}"
        self.preprint = preprint
        self.review_process = review_process

    def save(self, directory: str) -> None:
        """Save the referee report to a file.        Args:
            directory: The directory to save the file in.
        """
        doi_dir = Path(directory) / stringify_doi(self.doi)
        doi_dir.mkdir(parents=True, exist_ok=True)
        self._save_reviews(doi_dir)
        self._save_preprint(doi_dir)

    def from_dir(self, directory: Path):
        preprint_dir = directory / 'preprint'
        preprint = Preprint().from_dir(preprint_dir)
        review_dir = directory / 'review_process'
        review_process = ReviewProcess().from_dir(review_dir)
        self.from_objects(preprint, review_process)
        return self

    def _save_reviews(self, dir: Path):
        # save the individual referee reports to individual subdirectories
        rev_dir = dir / f'review_process'
        rev_dir.mkdir(exist_ok=True)
        self.review_process.save(rev_dir)

    def _save_preprint(self, dir: Path):
        preprint_dir = dir / 'preprint'
        preprint_dir.mkdir(exist_ok=True)
        self.preprint.save(preprint_dir)
