import unittest

from src.biorxiv import Preprint

# Test case for testing the methods of the Preprint class

""""""
class TestPreprint(unittest.TestCase):
    # setup class method
    @classmethod
    def setUpClass(cls):
        # Comprehensive mapping of mutations to the SARS-CoV-2 receptor-binding domain that affect recognition by polyclonal human serum antibodies
        # https://www.biorxiv.org/content/10.1101/2020.12.31.425021v1
        cls.preprint = Preprint('10.1101/2020.12.31.425021')
        cls.intro_start = "Neutralizing antibodies against the SARS-CoV-2 spike are associated with protection against infection in both humans"
        cls.methods_start = "Data and code availability We provide data and code in the following ways"
        cls.results_start = "RBD-targeting antibodies dominate the neutralizing activity of most convalescent sera"

    # test the introduction method
    def test_introduction(self):
        intro = self.preprint.introduction()
        self.assertTrue(intro.startswith(self.intro_start))
        print(intro)

    # # test the methods method
    # def test_methods(self):
    #     self.assertTrue(self.preprint.methods().startswith('Data and code availability We provide data and code in the following ways'))
    
    # # test the results method
    # def test_results(self):
    #     self.assertTrue(self.preprint.results().startswith('RBD-targeting antibodies dominate the neutralizing activity of most convalescent sera'))
