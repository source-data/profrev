from pathlib import Path
import json

from .review_process import ReviewProcess
from .biorxiv import Preprint
from .utils import stringify_doi


"""This module contains classes to generate the corpus of article and referee reports."""

class ReviewedPreprint: 
    """A class to represent a reviewed preprint and save it to disk"""
    def __init__(self, doi: str) -> None:
       self.doi = doi
       self.review_process = ReviewProcess(doi)
       self.preprint = Preprint(doi)

    def save(self, directory: str) -> None:
        """Save the referee report to a file.
        Args:
            directory: The directory to save the file in.
        """
        doi_dir = Path(directory) / stringify_doi(self.doi)
        doi_dir.mkdir(parents=True, exist_ok=True)
        self._save_reviews(doi_dir)
        self._save_preprint(doi_dir)

    def _save_reviews(self, dir: Path):
        # save the individual referee reports to individual subdirectories
        rev_dir = dir / f'reviews'
        rev_dir.mkdir(exist_ok=True)
        for rev in self.review_process.reviews:
            # make dir with the index of the review
            rev_i_dir = rev_dir / f"{rev.review_idx}"
            rev_i_dir.mkdir(exist_ok=True)
            # save the referee report to a file named 'review.txt'
            rev_file = rev_i_dir / f'review.txt'
            with open(rev_file, 'w') as f:
                f.write(rev.text)

    def _save_preprint(self, dir: Path):
        preprint_dir = dir / 'preprint'
        preprint_dir.mkdir(exist_ok=True)
        # save the sections to text file named after the section
        for sec, content in self.preprint.sections.items():
            sec_file = preprint_dir / f'{sec}.txt'
            with open(sec_file, 'w') as f:
                f.write(content)
        metadata_file = preprint_dir / 'metadata.json'
        with open(metadata_file, 'w') as jf:
            biorxiv_meta = self.preprint.biorxiv_meta.asdict()
            json.dump(biorxiv_meta, jf, indent=4)
