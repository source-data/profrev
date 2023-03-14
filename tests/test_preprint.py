import unittest
from shutil import rmtree
from pathlib import Path

from src.preprint import Preprint
from src.utils import stringify_doi

# Test case for testing the methods of the Preprint class

""""""
class TestPreprint(unittest.TestCase):
    # setup class method
    @classmethod
    def setUpClass(cls):
        # Comprehensive mapping of mutations to the SARS-CoV-2 receptor-binding domain that affect recognition by polyclonal human serum antibodies
        # https://www.biorxiv.org/content/10.1101/2020.12.31.425021v1
        # https://api.biorxiv.org/details/biorxiv/10.1101/2020.12.31.425021
        # https://www.biorxiv.org/content/early/2021/01/04/2020.12.31.425021.source.xml
        cls.preprint = Preprint('10.1101/2020.12.31.425021')
        cls.intro_start = "Neutralizing antibodies against the SARS-CoV-2 spike are associated with protection against infection in both humans"
        cls.intro_end = "human antibody immunity can inform surveillance of ongoing viral evolution."
        cls.results_start = "We characterized the serum antibodies from 35 plasma samples"
        cls.results_end = "are also worth monitoring, since they also have antigenic impacts."
        cls.result_headings_start = "RBD-targeting antibodies dominate the neutralizing activity of most convalescent sera"
        cls.result_headings_end = "RBD mutations that reduce serum binding and neutralization in circulating SARS-CoV-2 isolates"
        cls.figures_start = "RBD-binding antibodies are responsible for most of the neutralizing activity of human polyclonal sera"
        cls.fig_titles_start = "RBD-binding antibodies are responsible for most of the neutralizing activity of human polyclonal sera."
        cls.fig_titles_end = "Full curves for all assays testing how RBD mutations affected viral neutralization, related to Figure 4."
        cls.figures_end = "The numerical IC50s from all curves in both panels are available at https://github.com/jbloomlab/SARS-CoV-2-RBD_MAP_HAARVI_sera/blob/main/experimental_validations/results/mutant_neuts_results/mutants_foldchange_ic50.csv."
        cls.methods_start = "We provide data and code in the following ways"
        cls.methods_end = "scanning measurements of how mutations affect ACE2 binding or RBD expression as described above."
        cls.discussion_start = "We comprehensively mapped how mutations to the SARS-CoV-2 RBD"
        cls.discussion_end = "using this knowledge to design vaccines that are robust to viral antigenic evolution."
        cls.meta = {
            "doi": "10.1101/2020.12.31.425021",
            "title": "Comprehensive mapping of mutations to the SARS-CoV-2 receptor-binding domain that affect recognition by polyclonal human serum antibodies",
            "authors": "Greaney, A. J.; Loes, A. N.; Crawford, K. H.; Starr, T. N.; Malone, K. D.; Chu, H. Y.; Bloom, J. D.",
            "author_corresponding": "Jesse D Bloom",
            "author_corresponding_institution": "Fred Hutchinson Cancer Research Center",
            "date": "2021-01-04",
            "version": "1",
            "type": "new results",
            "license": "cc_by",
            "category": "microbiology",
            # jatsxml: "https://www.biorxiv.org/content/early/2021/01/04/2020.12.31.425021.source.xml",
            "abstract": "The evolution of SARS-CoV-2 could impair recognition of the virus by human antibody-mediated immunity. To facilitate prospective surveillance for such evolution, we map how convalescent serum antibodies are impacted by all mutations to the spikes receptor-binding domain (RBD), the main target of serum neutralizing activity. Binding by polyclonal serum antibodies is affected by mutations in three main epitopes in the RBD, but there is substantial variation in the impact of mutations both among individuals and within the same individual over time. Despite this inter- and intra-person heterogeneity, the mutations that most reduce antibody binding usually occur at just a few sites in the RBDs receptor binding motif. The most important site is E484, where neutralization by some sera is reduced >10-fold by several mutations, including one in emerging viral lineages in South Africa and Brazil. Going forward, these serum escape maps can inform surveillance of SARS-CoV-2 evolution.",
            "published": "10.1016/j.chom.2021.02.003",
            "server": "biorxiv"
        }

        if cls.preprint.doi is not None:
            cls.basedir = Path("/tmp/test_preprint") / stringify_doi(cls.preprint.doi)
        else:
            raise ValueError("DOI is None")
        print(f"Creating {cls.basedir} ...")
        cls.basedir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        # delete the directories created
        print(f"Cleaning up {cls.basedir} ...")
        rmtree(cls.basedir)

    # test the introduction method
    def test_save(self):
        self.preprint.save(self.basedir)
        restored_preprint = Preprint().from_dir(self.basedir)
        self.assertEqual(restored_preprint.doi, self.preprint.doi)
        self.assertEqual(restored_preprint.introduction, self.preprint.introduction)
        self.assertEqual(restored_preprint.results, self.preprint.results)
        self.assertEqual(restored_preprint.methods, self.preprint.methods)
        self.assertEqual(restored_preprint.discussion, self.preprint.discussion)
        self.assertEqual(restored_preprint.biorxiv_meta, self.preprint.biorxiv_meta)

    # test the introduction method
    def test_introduction(self):
        intro = self.preprint.introduction
        self.assertTrue(intro.startswith(self.intro_start))
        self.assertTrue(intro.endswith(self.intro_end))

    # test the results method
    def test_results(self):
        results = self.preprint.results
        self.assertTrue(results.startswith(self.results_start))
        self.assertTrue(results.endswith(self.results_end))

    
    # test the results method
    def test_result_headings(self):
        result_headings = self.preprint.result_headings
        self.assertTrue(result_headings.startswith(self.result_headings_start))
        self.assertTrue(result_headings.endswith(self.result_headings_end))

    # test the figures method
    def test_figures(self):
        figures = self.preprint.figures
        self.assertTrue(figures.startswith(self.figures_start))
        self.assertTrue(figures.endswith(self.figures_end))

     # test the figures method
    def test_fig_titles(self):
        fig_titles = self.preprint.fig_titles
        self.assertTrue(fig_titles.startswith(self.fig_titles_start))
        self.assertTrue(fig_titles.endswith(self.fig_titles_end))

    # test the methods method
    def test_methods(self):
        methods = self.preprint.methods
        self.assertTrue(methods.startswith(self.methods_start))
        self.assertTrue(methods.endswith(self.methods_end))

    # test the discussion method
    def test_discussion(self):
        discussion = self.preprint.discussion
        self.assertTrue(discussion.startswith(self.discussion_start))
        self.assertTrue(discussion.endswith(self.discussion_end))

    def test_biorxiv_meta(self):
        meta = self.preprint.biorxiv_meta  # this is a dataclass
        self.assertEqual(meta.asdict(), self.meta)  # type: ignore[reportOptionalMemberAccess]
