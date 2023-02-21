import unittest
from pathlib import Path
from shutil import rmtree
from typing import List

from src.corpus import Corpus
from src.bipartite import EmbeddingComparator
from src.biorxiv import Preprint
from src.review_process import ReviewProcess
from src.embed import Embedder
from src.config import config

"""Test cases for testing the methods of the Bipartite class"""

class TestBipartite(unittest.TestCase):

    # class setup method
    @classmethod
    def setUpClass(cls):
        cls.doi_list = [
            '10.1101/2021.05.12.443743',  # 3 reviews
            '10.1101/2022.11.25.517987',  # 2 reviews
        ]
        cls.basedir = Path("/tmp/test_bipartite")
        print(f"Creating {cls.basedir} ...")
        cls.basedir.mkdir(parents=True, exist_ok=True)
        # cls.corpus = Corpus(doi_list=cls.doi_list)
        # cls.corpus.save(cls.basedir)
        cls.embedder = Embedder(model=config.embedding_model)
        cls.doi = "10.1101/2021.05.12.443743"
        cls.preprint = Preprint(doi=cls.doi)
        cls.review_process = ReviewProcess(doi=cls.doi)

    @classmethod
    def tearDownClass(cls):
        # delete the directories created
        print(f"Cleaning up {cls.basedir} ...")
        rmtree(cls.basedir)

    def test_comparision(self):
        preprint_paragraphs = self.preprint.get_section_paragraphs("results")
        review_paragraphs = self.review_process.reviews[0].get_paragraphs()
        comp = EmbeddingComparator(self.embedder)
        similarity_matrix = comp.compare(preprint_paragraphs, review_paragraphs)
        self.assertEqual(tuple(similarity_matrix.size()), (len(preprint_paragraphs), len(review_paragraphs)))
