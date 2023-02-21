import unittest
from pathlib import Path
from shutil import rmtree

from src.corpus import Corpus
from src.utils import stringify_doi

# Test case for testing the methods of the ReviewedPreprin class

""""""
class TestReviewedPreprint(unittest.TestCase):
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
        ]
        cls.corpus = Corpus(doi_list=cls.doi_list)
        cls.basedir = Path("/tmp/test_reviewed_preprint")
        print(f"Creating {cls.basedir} ...")
        cls.basedir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        # delete the directories created
        print(f"Cleaning up {cls.basedir} ...")
        rmtree(cls.basedir)

    # test the introduction method
    def test_save(self):
        self.corpus.save(self.basedir)
        doi_dir_str_list = [stringify_doi(doi) for doi in self.doi_list]

        for doi_dir_str in doi_dir_str_list:
            doi_dir = self.basedir / doi_dir_str
            self.assertTrue(doi_dir.exists())