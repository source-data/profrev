import unittest

from ..src.review_process import ReviewProcess

# Test case for testing the methods of the ReviewProcess class

class TestReviewProcess(unittest.TestCase):
    # setup method
    def setUp(self):
        self.reviewprocess = ReviewProcess('10.1101/2020.12.31.425021')

    # test referee reports method
    def test_referee_reports(self):
        first_ref_report = self.reviewprocess.referee_reports()[0]
        test_content = """In the article entitled 'Unique functions of two overlapping PAX6 retinal enhancers'"""
        # test if test_content in the first referee reporrt
        self.assertTrue(test_content in first_ref_report)
