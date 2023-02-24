from random import choice, sample
from typing import List, Callable

from .corpus import Corpus
from .comparator import Comparator
from .embed import Embedder
from .utils import split_paragraphs
from .config import config

MODEL = config.embedding_model

"""A module to sample an empirical null distribution of similarity scores between review and preprint."""

class Sampler:

    def __init__(
            self,
            corpus: Corpus,
            n_sample: int,
            embedder: Embedder,
            chunking_fn: Callable = split_paragraphs
        ):
        self.corpus = corpus
        self.n_sample = n_sample
        N = len(corpus)
        assert N >= 2 * n_sample, f"Number of preprints ({N}) must be greater than twice the number of samples ({n_sample})."
        all_indices = list(range(N))
        # indices of reviewed preprint that will be used to sample preprint
        self.sampled_rev_preprint_indices = sample(all_indices, n_sample)
        # indices of reviewed preprint that will be used to sample reviews; the MUST be different from the sampled reviewed preprint above
        for x in self.sampled_rev_preprint_indices:
           all_indices.remove(x)  # to make sure that the sampled reviews are not from the sampled preprints
        self.samples_reviews_indices = sample(all_indices, n_sample)
        self.comparator = Comparator(embedder=embedder)
        self.chunking_fn = chunking_fn

    def sample(self) -> List[float]:
        """Sample a corpus of reviewed preprints."""
        sampled_preprint_content = [
            self.corpus.reviewed_preprints[i].preprint
            for i in self.sampled_rev_preprint_indices
        ]

        sampled_review = []
        for i in self.samples_reviews_indices:
            reviews = self.corpus.reviewed_preprints[i].review_process.reviews
            sampled_review.append(choice(reviews))  # take one random review from the reviews of the preprint

        similarities = []
        for preprint, review in zip(sampled_preprint_content, sampled_review):
            chunks_preprint = preprint.get_chunks(self.chunking_fn, config.section)
            chunks_review = review.get_chunks(self.chunking_fn)
            similarity = self.comparator.compare_dot(chunks_preprint, chunks_review)
            similarities += similarity.view(-1).tolist()  # flatten the similarity matrix
        return similarities
