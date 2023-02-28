import unittest

from src.utils import split_paragraphs, split_sentences, stringify_doi, filtering


"""Test cases to test the functions of the utils module"""

class TestUtils(unittest.TestCase):

    def test_stringify_doi(self):
        doi = '10.12345/abs.0132913'
        expected = '10_12345-abs_0132913'
        doi_str = stringify_doi(doi)
        self.assertEqual(doi_str, expected)

    def test_split_paragraphs(self):
        text = """
Learn more at [Review Commons](https://reviewcommons.org)


-----


### Referee \#1

#### Evidence, reproducibility and clarity

 **Summary:** 

In the article entitled 'Unique functions of two overlapping PAX6 retinal enhancers', Uttley and coworkers characterize in detail the activity of two conserved human enhancers (i.e. NRE and HS5) previously reported to drive Pax6 expression to the neural retina. By integrating these enhancers in a PhiC31 landing site using a dual enhancer-reporter cassette, they generated a zebrafish stable line in which their activity can be followed by the expression of GFP (NRE) and mCherry (HS5). The authors show that although the enhancers have a partially overlapping activity at early stages (24hpf), later on (48 and 72hpf) they activity domains segregate: to stem cells and differentiated amacrine cells for NRE, and to proliferating progenitors and differentiated M&#x00FC;ller glia cells for HS5. To this end they used two different approaches: a scRNA-seq analysis of sorted cells from the transgenic line and a immunofluorescent analysis employing cell specific markers. The authors conclude that their analysis allowed the identification of unique cell type-specific functions. 

**Major comments:** 

In general terms, the article is technically sound (please, see section B for an assessment of the significance of the findings). The methodology used and the data analysis are accurate. The work is well presented, the figures are clear, and the previous literature properly cited. My main concerns are the following:

1. A general concern on the main conclusion of the work 'the identification of unique cell type-specific functions for these enhancers'. This is in my opinion only partially addressed by the study, as the conclusions are limited due to the absence of genetic experiments: such as deleting the enhancers in their native genomic context (either in human organoids or the homologous sequence in animal models), or at least assessing the effect of mutating their sequence in transgenesis assays in zebrafish. I understand that these functional assays may be out of the scope of the current work, but then the text should be toned down (the word 'function' is extensively used) to make clear that the authors mean just expression. I would suggest substituting the word by 'activity' in many instances. 
The absence of further genetic experiments also limits the significance of the study (see section B).
2. Whereas the work in general is technically correct (particularly transgenic lines and scRNA-seq data are well described and presented), the co-expression analyses using cell-specific markers (figure 5) need to be improved. There are several issues here. First, the magnification shown is too low to appreciate the colocalization details in the figure. The panels should be replaced by others with higher magnification/resolution (see also minor comment on color-blind compatible images)
In addition, the selection of the markers leis suboptimal. Although PCNA is a good general marker of the entire CMZ, it would be advisable to repeat the experiments using more specific markers of the stem cell niche (e.g. rx1, vsx2; Raymond et al 2006; BMC dev Biol) to better define the enhancers expression domain. In addition, HuC/D labels both RGCs and amacrines, and the colocalization could also be refined using amacrine specific markers (e.g. ptf1a : Jusuf & Harris 2009, Neural Dev).

"""

        # split the text into paragraphs
        paragraphs = split_paragraphs(text)
        expected = [
            "In the article entitled 'Unique functions of two overlapping PAX6 retinal enhancers', Uttley and coworkers characterize in detail the activity of two conserved human enhancers (i.e. NRE and HS5) previously reported to drive Pax6 expression to the neural retina. By integrating these enhancers in a PhiC31 landing site using a dual enhancer-reporter cassette, they generated a zebrafish stable line in which their activity can be followed by the expression of GFP (NRE) and mCherry (HS5). The authors show that although the enhancers have a partially overlapping activity at early stages (24hpf), later on (48 and 72hpf) they activity domains segregate: to stem cells and differentiated amacrine cells for NRE, and to proliferating progenitors and differentiated M&#x00FC;ller glia cells for HS5. To this end they used two different approaches: a scRNA-seq analysis of sorted cells from the transgenic line and a immunofluorescent analysis employing cell specific markers. The authors conclude that their analysis allowed the identification of unique cell type-specific functions.",
            "In general terms, the article is technically sound (please, see section B for an assessment of the significance of the findings). The methodology used and the data analysis are accurate. The work is well presented, the figures are clear, and the previous literature properly cited. My main concerns are the following:",
            "1. A general concern on the main conclusion of the work 'the identification of unique cell type-specific functions for these enhancers'. This is in my opinion only partially addressed by the study, as the conclusions are limited due to the absence of genetic experiments: such as deleting the enhancers in their native genomic context (either in human organoids or the homologous sequence in animal models), or at least assessing the effect of mutating their sequence in transgenesis assays in zebrafish. I understand that these functional assays may be out of the scope of the current work, but then the text should be toned down (the word 'function' is extensively used) to make clear that the authors mean just expression. I would suggest substituting the word by 'activity' in many instances.",
            "The absence of further genetic experiments also limits the significance of the study (see section B).",
            "2. Whereas the work in general is technically correct (particularly transgenic lines and scRNA-seq data are well described and presented), the co-expression analyses using cell-specific markers (figure 5) need to be improved. There are several issues here. First, the magnification shown is too low to appreciate the colocalization details in the figure. The panels should be replaced by others with higher magnification/resolution (see also minor comment on color-blind compatible images)",
            "In addition, the selection of the markers leis suboptimal. Although PCNA is a good general marker of the entire CMZ, it would be advisable to repeat the experiments using more specific markers of the stem cell niche (e.g. rx1, vsx2; Raymond et al 2006; BMC dev Biol) to better define the enhancers expression domain. In addition, HuC/D labels both RGCs and amacrines, and the colocalization could also be refined using amacrine specific markers (e.g. ptf1a : Jusuf & Harris 2009, Neural Dev).",
        ]
        # compare the expected and actual list of paragraphs
        self.assertEqual(paragraphs, expected)

    def test_split_sentences(self):
        text = "1. A general concern on the main conclusion of the work 'the identification of unique cell type-specific functions for these enhancers'. This is in my opinion only partially addressed by the study, as the conclusions are limited due to the absence of genetic experiments: such as deleting the enhancers in their native genomic context (either in human organoids or the homologous sequence in animal models), or at least assessing the effect of mutating their sequence in transgenesis assays in zebrafish. I understand that these functional assays may be out of the scope of the current work, but then the text should be toned down (the word 'function' is extensively used) to make clear that the authors mean just expression. I would suggest substituting the word by 'activity' in many instances."

        expected = [
            # "1.",
            "A general concern on the main conclusion of the work 'the identification of unique cell type-specific functions for these enhancers'.",
            "This is in my opinion only partially addressed by the study, as the conclusions are limited due to the absence of genetic experiments: such as deleting the enhancers in their native genomic context (either in human organoids or the homologous sequence in animal models), or at least assessing the effect of mutating their sequence in transgenesis assays in zebrafish.",
            "I understand that these functional assays may be out of the scope of the current work, but then the text should be toned down (the word 'function' is extensively used) to make clear that the authors mean just expression.",
            "I would suggest substituting the word by 'activity' in many instances.",
        ]
        sentences = split_sentences(text)
        self.assertEqual(sentences, expected)

    def test_filter(self):
        docs =[
            "n of the work 'the identification of unique cell t",
            "A general concern on the main conclusion of the work 'the identification of unique cell type-specific functions for these enhancers'. This is in my opinion only partially addressed by the study, as the conclusions are limited due to the absence of genetic experiments: such as deleting the enhancers in their native genomic context (either in human organoids or the homologous sequence in animal models), or at least assessing the effect of mutating their sequence in transgenesis assays in zebrafish. I understand that these functional assays may be out of the scope of the current work, but then the text should be toned down (the word 'function' is extensively used) to make clear that the authors mean just expression. I would suggest substituting the word by 'activity' in many instances.",
            "**Note:** This preprint has been reviewed by subject experts for *Review Commons*. Content has not been altered except for formatting."
        ]
        filtered = filtering(docs)
        self.assertEqual(filtered[0], docs[1])
