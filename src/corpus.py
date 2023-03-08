from typing import List
from pathlib import Path

from .reviewed_preprint import ReviewedPreprint
from .utils import doi_str_re

# a class to create a corpus of reviewed preprints from a list of DOIs
class Corpus:
    """A class to represent a corpus of reviewed preprints."""
    def __init__(self, doi_list: List[str] = []):
        self.doi_list = doi_list
        self.reviewed_preprints = [ReviewedPreprint(doi) for doi in doi_list] if doi_list else []
        assert len(doi_list) == len(self.reviewed_preprints), f"Number of DOIs ({len(doi_list)}) does not match number of reviewed preprints ({len(self.reviewed_preprints)})."

    def save(self, directory: Path):
        """Save the corpus to a directory.
        Args:
            directory: The directory to save the corpus in.
        """
        for reviewed_preprint in self.reviewed_preprints:
            reviewed_preprint.save(directory)

    def from_dir(self, directory: Path):
        """Load the corpus from a directory that contains reviewed preprints.
        Each reviewed preprint is in a directory named after its DOI.
        Args:
            directory: The directory that contains the reviewed preprint.
        """
        # doi_str_match matches a stringified DOI, whereby the doit are underscore and slash are hyphens
        doi_dir_list = [d for d in Path(directory).iterdir() if d.is_dir() and doi_str_re.match(d.name)]
        self.reviewed_preprints = [ReviewedPreprint().from_dir(d) for d in doi_dir_list]
        doi_list = [reviewed_preprint.doi for reviewed_preprint in self.reviewed_preprints]
        self.doi_list = doi_list
        return self
    
    def __len__(self):
        return len(self.doi_list)
