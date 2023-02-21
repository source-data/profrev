from typing import List

from .reviewed_preprint import ReviewedPreprint

# a class to create a corpus of reviewed preprints from a list of DOIs
class Corpus:
    """A class to represent a corpus of reviewed preprints."""
    def __init__(self, doi_list: List[str]) -> None:
        self.doi_list = doi_list

    def save(self, directory: str) -> None:
        """Save the corpus to a directory.
        Args:
            directory: The directory to save the corpus in.
        """
        for doi in self.doi_list:
            reviewed_preprint = ReviewedPreprint(doi)
            reviewed_preprint.save(directory)


