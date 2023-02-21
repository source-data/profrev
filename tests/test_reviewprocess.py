import unittest

from src.review_process import ReviewProcess

# Test case for testing the methods of the ReviewProcess class

# https://eeb.embo.org/api/v1/doi/10.1101/2021.05.12.443743


class TestReviewProcess(unittest.TestCase):
    # setup method
    @classmethod
    def setUpClass(cls):
        cls.reviewprocess = ReviewProcess('10.1101/2021.05.12.443743')
        cls.review_excerpt = {
            "1": "performed RNA-seq together with the ribosome profiling experiment, it might be interesting",
            "2": "the PACE reporter validated, the authors can interrogate the system to gain mechanistic insights",
            "3": "Page 13, second paragraph: More out of interest, but it is quite intriguing that GCG turned into a destabilizing codon",
        }

    # test referee reports method
    def test_reviews(self):
        reviews = self.reviewprocess.reviews
        self.assertEqual(len(reviews), 3)
        for rev in reviews:
            idx = rev.review_idx
            content = rev.text
            # test if test_content in the referee reporrt
            self.assertTrue(self.review_excerpt[idx] in content)
