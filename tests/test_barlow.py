import unittest
import torch

from src.models.barlow_embeddings import LatentEmbedding, LatentSentenceEmbedding, LatentParagraphEmbedding

# Test case for testing the barlow twin latent embedding model

""""""
class TestLatentEmbedding(unittest.TestCase):
    # setup class method
    @classmethod
    def setUpClass(cls):
        cls.sentence = "This is a sentence."
        cls.paragraph = "This is a paragraph. This is another paragraph."

    def test_latent_embedding(self):
        # test that the latent embedding model can be loaded
        model = LatentEmbedding()
        self.assertIsInstance(model, LatentEmbedding)

        # test that the model can be used to generate embeddings
        sentence_embedding = model(self.sentence)
        self.assertIsInstance(sentence_embedding, torch.Tensor)

    def test_latent_sentence_embedding(self):
        # test that the latent sentence embedding model can be loaded
        model = LatentSentenceEmbedding()
        self.assertIsInstance(model, LatentSentenceEmbedding)

        # test that the model can be used to generate embeddings
        sentence_embedding = model(self.sentence)
        self.assertIsInstance(sentence_embedding, torch.Tensor)

        paragraph_embedding = model(self.paragraph)
        self.assertIsInstance(paragraph_embedding, torch.Tensor)

    def test_latent_paragraph_embedding(self):
        # test that the latent paragraph embedding model can be loaded
        model = LatentParagraphEmbedding()
        self.assertIsInstance(model, LatentParagraphEmbedding)

        # test that the model can be used to generate embeddings
        sentence_embedding = model(self.sentence)
        self.assertIsInstance(sentence_embedding, torch.Tensor)

        paragraph_embedding = model(self.paragraph)
        self.assertIsInstance(paragraph_embedding, torch.Tensor)
