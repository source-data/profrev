import torch
from typing import List

from src.biorxiv import Preprint
from src.review_process import Review
from src.embed import Embedder


class EmbeddingComparator:

    def __init__(self, embedder: Embedder):
        self.embedder = embedder

    def compare(self, para_1: List[str], para_2: List[str]) -> torch.Tensor:
        """Compare the paragraphs of a preprint section to the pargraphs of a review to compute a similarity matrix.
        Args:
            para_1: The paragraphs of a preprint section.
            para_2: The paragraphs of a review.

        Returns:
            A similarity matrix.
        """
        A, _ = self.embedder.get_embedding(para_1)
        B, _ = self.embedder.get_embedding(para_2)
        A = torch.tensor(list(A))
        B = torch.tensor(list(B))
        similarity_matrix = torch.mm(A, B.T)
        return similarity_matrix
