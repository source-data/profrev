import unittest
from pathlib import Path
from shutil import rmtree

from src.review_process import ReviewProcess

# Test case for testing the methods of the ReviewProcess class

# https://eeb.embo.org/api/v1/doi/10.1101/2021.05.12.443743


class TestReviewProcess(unittest.TestCase):
    # setup method
    @classmethod
    def setUpClass(cls):
        cls.doi = '10.1101/2021.05.12.443743'
        cls.reviewprocess = ReviewProcess(cls.doi)
        cls.review_excerpt = {
            "1": "performed RNA-seq together with the ribosome profiling experiment, it might be interesting",
            "2": "the PACE reporter validated, the authors can interrogate the system to gain mechanistic insights",
            "3": "Page 13, second paragraph: More out of interest, but it is quite intriguing that GCG turned into a destabilizing codon",
        }

        cls.basedir = Path("/tmp/test_review_process/reviews")
        print(f"Creating {cls.basedir} ...")
        cls.basedir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        # delete the directories created
        print(f"Cleaning up {cls.basedir} ...")
        rmtree(cls.basedir)

    def test_save(self):
        self.reviewprocess.save(self.basedir)
        restored_reviewprocess = ReviewProcess().from_dir(self.basedir)
        self.assertEqual(len(self.reviewprocess.reviews), len(restored_reviewprocess.reviews))
        original_rev_dict = {rev.review_idx: rev for rev in self.reviewprocess.reviews}
        restored_rev_dict = {rev.review_idx: rev for rev in restored_reviewprocess.reviews}
        for rev_idx in original_rev_dict:
            self.assertEqual(restored_rev_dict[rev_idx], original_rev_dict[rev_idx])
        self.assertSetEqual(set(restored_rev_dict.keys()), set(original_rev_dict.keys()))

    # test referee reports method
    def test_reviews(self):
        reviews = self.reviewprocess.reviews
        self.assertEqual(len(reviews), 3)
        for rev in reviews:
            idx = rev.review_idx
            content = rev.text
            # test if test_content in the referee reporrt
            self.assertTrue(self.review_excerpt[idx] in content)
