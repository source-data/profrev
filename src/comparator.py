import torch
from typing import List, Tuple

from src.embed import Embedder


class Comparator:
    """Compare two lists of strings using a list of embedders. The first embedder is used to embed the first list of strings
    and the second embedder is used to embed the second list of strings. If a single embedder is provided, it is used for
    both lists of strings.
        Args:
            embedder: A list of embedders to use for the comparison.

        Attributes:
            embedder: A list of embedders to use for the comparison.

    """
    def __init__(self, embedder: List[Embedder]):
        if not isinstance(embedder, list):
            embedder = [embedder, embedder]
        self.embedder = embedder

    def get_embeddings(self, para_1: List[str], para_2: List[str]) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get embeddings for a list of strings.
        Args:
            input: A list of strings to get embeddings for.
        Returns:
            A list of embeddings, one for each string in the input.
        """
        embeddings_1 = self.embedder[0].get_embedding(para_1)  # num_examples x embedding_dim
        embeddings_2 = self.embedder[1].get_embedding(para_2)  # num_examples x embedding_dim
        return embeddings_1, embeddings_2

    def compare_dot(self, para_1: List[str], para_2: List[str]) -> torch.Tensor:
        """Compare the paragraphs of a preprint section to the pargraphs of a review to compute a similarity matrix.
        The similarity matrix is computed by taking the dot product of between paragraph embeddings
        Args:
            para_1 (List[str]): The first list of paragraphs
            para_2 (List[str[]): The second list of paragraphs

        Returns:
            A similarity matrix as a torch.Tensor
        """
        A, B = self.get_embeddings(para_1, para_2)
        similarity = torch.mm(A, B.T)
        return similarity
    
    def compare_cosine(self, para_1: List[str], para_2: List[str]) -> torch.Tensor:
        """Compare the paragraphs of a preprint section to the pargraphs of a review to compute a similarity matrix.
        The similarit matrix is computed using cosine similarity.
        Args:
            para_1: The paragraphs of a preprint section.
            para_2: The paragraphs of a review.

        Returns:
            A similarity matrix as a torch.Tensor
        """
        A, B = self.get_embeddings(para_1, para_2)
        similarity = torch.mm(A, B.T) / (torch.linalg.norm(A) * torch.linalg.norm(B))
        return similarity
