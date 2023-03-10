import unittest
import torch
import pandas as pd

from src.corpus import Corpus
from src.sampler import Sampler
from src.embed import SBERTEmbedder
from src.utils import split_paragraphs, split_sentences

# Test case for testing the methods of the ReviewedPreprin class

""""""
class TestSample(unittest.TestCase):
    # setup class method
    @classmethod
    def setUpClass(cls):
        # Comprehensive mapping of mutations to the SARS-CoV-2 receptor-binding domain that affect recognition by polyclonal human serum antibodies
        # https://www.biorxiv.org/content/10.1101/2020.12.31.425021v1
        # https://api.biorxiv.org/details/biorxiv/10.1101/2020.12.31.425021
        # https://www.biorxiv.org/content/early/2021/01/04/2020.12.31.425021.source.xml
        cls.doi_list = [
            '10.1101/2021.05.12.443743',  # 3 reviews
            '10.1101/2022.11.25.517987',  # 2 reviews
            '10.1101/2022.01.04.474903',  # 3 reviews
            '10.1101/2022.09.09.507210',  # 3 reviews
        ]
        cls.corpus = Corpus(doi_list=cls.doi_list)

    def test_sample(self):
        sampler = Sampler(self.corpus, embedder=SBERTEmbedder(), chunking_fn=split_paragraphs)
        distros = sampler.sample(n_sample=2)
        self.assertGreater(len(distros['null']), 0)
        self.assertGreater(len(distros['enriched']), 0)
        self.assertEqual(torch.Tensor(distros['null']).dim(), 1)
        self.assertEqual(torch.Tensor(distros['enriched']).dim(), 1)

    def test_sample_with_two_embedders(self):
        sampler = Sampler(self.corpus, embedder=[SBERTEmbedder(), SBERTEmbedder()], chunking_fn=[split_sentences, split_paragraphs])
        distros = sampler.sample(n_sample=2)
        self.assertGreater(len(distros['null']), 0)
        self.assertGreater(len(distros['enriched']), 0)
        self.assertEqual(torch.Tensor(distros['null']).dim(), 1)
        self.assertEqual(torch.Tensor(distros['enriched']).dim(), 1)
