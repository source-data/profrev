import torch
from typing import List, Tuple

from src.preprint import Preprint
from src.review_process import Review
from src.embed import Embedder


class Comparator:

    def __init__(self, embedder: Embedder):
        self.embedder = embedder

    def get_embeddings(self, para_1: List[str], para_2: List[str]) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get embeddings for a list of strings.
        Args:
            input: A list of strings to get embeddings for.
        Returns:
            A list of embeddings, one for each string in the input.
        """
        embeddings_1, _ = self.embedder.get_embedding(para_1)
        embeddings_2, _ = self.embedder.get_embedding(para_2)
        # get tensors
        embeddings_1 = torch.tensor(list(embeddings_1))
        embeddings_2 = torch.tensor(list(embeddings_2))
        return embeddings_1, embeddings_2

    def compare_dot(self, para_1: List[str], para_2: List[str]) -> torch.Tensor:
        """Compare the paragraphs of a preprint section to the pargraphs of a review to compute a similarity matrix.
        The similarity matrix is computed by taking the dot product of between paragraph embeddings
        Args:
            para_1 (List[str]): The first list of paragraphs
            para_2 (List[str[]): The second list of paragraphs

        Returns:
            A similarity matrix
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
            A similarity matrix.
        """
        A, B = self.get_embeddings(para_1, para_2)
        similarity = torch.mm(A, B.T) / (torch.linalg.norm(A) * torch.linalg.norm(B))
        return similarity
