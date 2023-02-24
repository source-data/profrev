import unittest
import openai

from src.corpus import Corpus
from src.embed import OpenAIEmbedder, SBERTEmbedder
from src.config import config

"""Test cases for testing the methods of the Bipartite class"""

class TestEmbedder(unittest.TestCase):

    # class setup method
    @classmethod
    def setUpClass(cls):
        cls.samples = [
            "This is a sample text",
            "This is another sample text",
            "Something different",
            "We designed an artificial codon-tag sequence to analyze the codon effects on mRNA stability in a defined sequence context (Figure 1A). This sequence contains a codon to be tested (e.g., a codon for Leu) 20 times, each separated by a codon encoding one of the 20 amino acids. The sequence was inserted at the 3’ end of the superfolder GFP (sfGFP) ORF by taking the positional effect of codon-mediated decay into account (Mishima and Tomari, 2016). We then compared the CUG and CUA Leu codon tags, whose differential effects on deadenylation were reported previously in zebrafish embryos (Mishima and Tomari, 2016). In vitro synthesized, capped and polyadenylated reporter mRNAs were injected into 1-cell stage zebrafish embryos and analyzed at two hours post fertilization (hpf) (before the maternal-to-zygotic transition [MZT]) and 6 hpf (after the MZT). Analysis of the poly(A) tail lengths by PAT assays revealed that the CUA codon-tag promoted deadenylation compared to the CUG codon-tag (Figure 1B and 1C). Consistent with the poly(A) tail status, qRT-PCR showed that the CUA codon-tag reporter was less stable than the CUG codon-tag reporter (Figure 1D). The observed difference in mRNA stability was a cotranslational effect because inhibition of translation initiation by an antisense morpholino oligonucleotide (MO) specific to the GFP ORF abolished the destabilizing effect of the CUA codon (Figure 1E). Hence, our codon-tag reporters recapitulated the translation-dependent effect of codons on mRNA deadenylation and degradation in zebrafish embryos.",
        ]
        cls.openai_embedder = OpenAIEmbedder()
        cls.sbert_embedder = SBERTEmbedder()

    def test_openai_auth(self):
        # test successful authentication to openai
        list = openai.Engine.list()
        self.assertTrue(list is not None)

    def test_openai_embedder(self):
        embeddings, metadata = self.openai_embedder.get_embedding(self.samples)
        self.assertEqual(len(embeddings), len(self.samples))
        self.assertEqual(len(embeddings[0]), 2048)
        self.assertEqual(metadata['model'].replace(':', '-'), config.embedding_model['openai'])

    def test_sbert_embedder(self):
        embeddings, _ = self.sbert_embedder.get_embedding(self.samples)
        self.assertEqual(len(embeddings), len(self.samples))
        self.assertEqual(len(embeddings[0]), 384)
        