import unittest
from pathlib import Path
from shutil import rmtree

from src.reviewed_preprint import ReviewedPreprint
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
        cls.doi = '10.1101/2021.05.12.443743'
        cls.reviewed_preprint = ReviewedPreprint(doi=cls.doi)
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
        self.reviewed_preprint.save(self.basedir)
        doi_dir_str = stringify_doi(self.doi)

        doi_dir = self.basedir / doi_dir_str
        self.assertTrue(doi_dir.exists())

        preprint_dir = doi_dir / 'preprint'
        self.assertTrue(preprint_dir.exists())

        introduction_file = preprint_dir / 'introduction.txt'
        self.assertTrue(introduction_file.exists())

        methods_file = preprint_dir / 'methods.txt'
        self.assertTrue(methods_file.exists())

        results_file = preprint_dir / 'results.txt'
        self.assertTrue(results_file.exists())

        discussion_file = preprint_dir / 'discussion.txt'
        self.assertTrue(discussion_file.exists())

        metadata_file = preprint_dir / 'metadata.json'
        self.assertTrue(metadata_file.exists())

        reviews_dir = doi_dir / 'reviews'
        self.assertTrue(reviews_dir.exists())

        # list subdirectories under reviews
        reviews_subdirs = [x for x in reviews_dir.iterdir() if x.is_dir()]
        subdir_names = [x.name for x in reviews_subdirs]
        # test if there are 3 subdirectories
        self.assertEqual(len(reviews_subdirs), 3)
        # test if subdir are named after the review_idx
        for rev in self.reviewed_preprint.review_process.reviews:
            self.assertTrue(rev.review_idx in subdir_names)