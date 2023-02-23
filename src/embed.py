from typing import List, Tuple, Dict
from tenacity import retry, wait_random_exponential, stop_after_attempt
import openai

from .config import config

MODEL = config.embedding_model

class Embedder:
    """A class to get embeddings from OpenAI Embedding API.
    Attributes:
        model: The model to use for the embedding.
    """
    def __init__(self, model: str=MODEL):
        """"""
        self.model = model

    @retry(wait=wait_random_exponential(multiplier=1, max=10), stop=stop_after_attempt(3))
    def get_embedding(self, input: List[str]) -> Tuple[List[List[float]], Dict]:
        """Get embeddings for a list of strings.
        Args:
            input: A list of strings to get embeddings for.
        Returns:
            A list of embeddings, one for each string in the input.
        """
        results = openai.Embedding.create(input=input, model=self.model)
        embeddings = [r['embedding'] for r in results['data']]
        results.pop('data')
        return embeddings, results