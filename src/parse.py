from pathlib import Path
from typing import List
import re

from .utils import clean_text

# class to import text from a file and parse it into a list of paragraphs
class Parser:
    """A class to parse text from a file into a list of paragraphs.
    Attributes:
        file: The file to parse.
    """
    def __init__(self, file: str):
        """"""
        self.file = file

    def parse(self) -> List[str]:
        """Parse the file into a list of paragraphs.
        Returns:
            A list of paragraphs.
        """
        with open(self.file, 'r') as f:
            text = f.read()
            text = clean_text(text)
        paragraphs = text.split('\n\n')
        return paragraphs
