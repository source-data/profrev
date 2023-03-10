import torch
from typing import List, Tuple, Dict
from tenacity import retry, wait_random_exponential, stop_after_attempt
import openai
from sentence_transformers import SentenceTransformer, util

from .models.barlow_embeddings import LatentEmbedding, LatentParagraphEmbedding, LatentSentenceEmbedding

from .config import config

OPENAI_MODEL = config.embedding_model['openai']
SBERT_MODEL = config.embedding_model['sbert']
BARLOW_MODEL = config.embedding_model['barlow']


class Embedder:
    """A abstract class to get embeddings from OpenAI Embedding API.
    Attributes:
        model: The model to use for the embedding.
    """
    def __init__(self, model: str = ""):
        self.model = model

    @retry(wait=wait_random_exponential(multiplier=1, max=10), stop=stop_after_attempt(3))
    def get_embedding(self, inputs: List[str]) ->  torch.Tensor:
        raise NotImplementedError


class OpenAIEmbedder(Embedder):
    """A class to get open ai GPT embeddings.
    Attributes:
        model: The model to use for the embedding.
    """
    def __init__(self, model: str = OPENAI_MODEL):
        super().__init__(model)

    @retry(wait=wait_random_exponential(multiplier=1, max=10), stop=stop_after_attempt(3))
    def get_embedding(self, inputs: List[str]) -> torch.Tensor:
        """Get embeddings for a list of strings.
        Args:
            input: A list of strings to get embeddings for.
        Returns:
            A tensor with embeddings as rows, one for each string in the input.
        """
        results = openai.Embedding.create(input=inputs, model=self.model)
        embeddings: List[List[float]] = [r['embedding'] for r in results['data']]
        # results.pop('data')  # some metadata, not used for now
        embeddings = torch.Tensor(embeddings)
        return embeddings  # num_examples x embedding_dim


class SBERTEmbedder(Embedder):
    """A class to get embeddings from sentence transfomer SBERT.
    Attributes:
        model: The model to use for the embedding.
    """
    def __init__(self, model: str = SBERT_MODEL):
        super().__init__(model)
        self.transformer = SentenceTransformer(model)
        self.transformer.max_seq_length = 512

    @retry(wait=wait_random_exponential(multiplier=1, max=10), stop=stop_after_attempt(3))
    def get_embedding(self, inputs: List[str]) -> torch.Tensor:
        """Get embeddings for a list of strings.
        Args:
            input: A list of strings to get embeddings for.
        Returns:
            A tensor with embeddings as rows, one for each string in the input.
        """
        embeddings = self.transformer.encode(inputs, normalize_embeddings=True, convert_to_tensor=True)
        return embeddings  # num_examples x embedding_dim
    
class BarlowEmbedder(Embedder):
    """A class to get embeddings from Barlow Twins embeddings.
    """
    def __init__(self, model: str = BARLOW_MODEL, mode: str = 'paragraph'):
        super().__init__(model)
        self.latent_encoder = LatentEmbedding(model, mode)

    def get_embedding(self, inputs: List[str]) -> torch.Tensor:
        """Get embeddings for a list of strings.
        Args:
            input: A list of strings to get embeddings for.
        Returns:

        """
        embeddings = self.latent_encoder(inputs)
        return embeddings  # num_examples x embedding_dim
    
class BarlowSentenceEmbedder(BarlowEmbedder):
    """A class to get embeddings from Barlow Twins sentence embeddings.
    """
    def __init__(self, model: str = BARLOW_MODEL):
        super().__init__(model, mode='sentence')

class BarlowParagraphEmbedder(BarlowEmbedder):
    """A class to get embeddings from Barlow Twins paragraph embeddings.
    """
    def __init__(self, model: str = BARLOW_MODEL):
        super().__init__(model, mode='paragraph')   