import unittest
from pathlib import Path
from shutil import rmtree

from src.comparator import Comparator
from src.preprint import Preprint
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
        comp = Comparator(self.embedder)
        similarity_matrix_dot = comp.compare_dot(preprint_paragraphs, review_paragraphs)
        self.assertEqual(tuple(similarity_matrix_dot.size()), (len(preprint_paragraphs), len(review_paragraphs)))

        similarity_matrix_cos = comp.compare_cosine(preprint_paragraphs, review_paragraphs)
        self.assertEqual(tuple(similarity_matrix_cos.size()), (len(preprint_paragraphs), len(review_paragraphs)))
