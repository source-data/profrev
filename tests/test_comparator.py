import unittest
from pathlib import Path
from shutil import rmtree

from src.comparator import Comparator
from src.preprint import Preprint
from src.review_process import ReviewProcess
from src.embed import (
    OpenAIEmbedder, SBERTEmbedder,
    BarlowEmbedder, BarlowParagraphEmbedder, BarlowSentenceEmbedder,
)
from src.utils import split_paragraphs, split_sentences
from src.config import config

"""Test cases for testing the methods of the Bipartite class"""

class TestComparator(unittest.TestCase):

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
        cls.embedders = [SBERTEmbedder(), BarlowEmbedder(),]  # leaving out OpenAIEmbedder() because it's paid service
        cls.doi = "10.1101/2021.05.12.443743"
        cls.preprint = Preprint(doi=cls.doi)
        cls.review_process = ReviewProcess(doi=cls.doi)

    @classmethod
    def tearDownClass(cls):
        # delete the directories created
        print(f"Cleaning up {cls.basedir} ...")
        rmtree(cls.basedir)

    def test_comparison(self):
        preprint_paragraphs = self.preprint.get_chunks(split_paragraphs, config.sections)
        review_paragraphs = self.review_process.reviews[0].get_chunks(split_paragraphs)
        for embedder in self.embedders:
            comp = Comparator(embedder)
            similarity_matrix_dot = comp.compare_dot(preprint_paragraphs, review_paragraphs)
            self.assertEqual(tuple(similarity_matrix_dot.size()), (len(preprint_paragraphs), len(review_paragraphs)))

            similarity_matrix_cos = comp.compare_cosine(preprint_paragraphs, review_paragraphs)
            self.assertEqual(tuple(similarity_matrix_cos.size()), (len(preprint_paragraphs), len(review_paragraphs)))

    def test_comparison_sentence_paragraph(self):
        review_sentences = self.review_process.reviews[0].get_chunks(split_sentences)
        preprint_paragraphs = self.preprint.get_chunks(split_paragraphs, config.sections)
        barlow_sentence_embedder = BarlowSentenceEmbedder()
        barlow_paragraph_embedder = BarlowParagraphEmbedder()
        comp = Comparator([barlow_sentence_embedder, barlow_paragraph_embedder])
        similarity_matrix_dot = comp.compare_dot(review_sentences, preprint_paragraphs)
        self.assertEqual(tuple(similarity_matrix_dot.size()), (len(review_sentences), len(preprint_paragraphs)))
