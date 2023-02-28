from random import choice, sample
from typing import List, Callable

from .corpus import Corpus
from .comparator import Comparator
from .embed import Embedder
from .utils import split_paragraphs
from .config import config


"""A module to sample an empirical null distribution of similarity scores between review and preprint."""

class Sampler:

    def __init__(
            self,
            corpus: Corpus,
            embedder: Embedder,
            chunking_fn: Callable = split_paragraphs
        ):
        self.corpus = corpus
        self.N = len(corpus)
        self.comparator = Comparator(embedder=embedder)
        self.chunking_fn = chunking_fn

    def sample(self, n_sample: int) -> List[float]:
        assert self.N >= 2 * n_sample, f"Number of preprints ({N}) must be greater than twice the number of samples ({n_sample})."
        
        all_indices = list(range(self.N))

        # indices of reviewed preprint that will be used to sample preprints
        sampled_rev_preprint_indices = sample(all_indices, n_sample)

        # similarity scores between cognate reviews and preprints      
        sampled_preprint_chunks: List[List[str]] = []
        sampled_cognate_review_chunks: List[List[str]] = []
        for i in sampled_rev_preprint_indices:
            rev_preprint = self.corpus.reviewed_preprints[i]
            sampled_preprint_chunks.append(rev_preprint.preprint.get_chunks(self.chunking_fn, config.sections))

            reviews = rev_preprint.review_process.reviews
            review = choice(reviews)  # take one random review from the reviews of the preprint
            sampled_cognate_review_chunks.append(review.get_chunks(self.chunking_fn))
        similarities_enriched = self._compare(sampled_preprint_chunks, sampled_cognate_review_chunks)

        # similarity scores between non-cognate reviews and preprints
        # indices of reviewed preprint that will be used to sample non-cognate reviews;
        # they MUST be different from the sampled reviewed preprint above, hence 'non-cognate'
        for x in sampled_rev_preprint_indices:
           all_indices.remove(x)

        samples_non_cognate_indices = sample(all_indices, n_sample)
        sampled_non_cognate_review_chunks: List[List[str]] = []
        for i in samples_non_cognate_indices:
            reviews = self.corpus.reviewed_preprints[i].review_process.reviews
            review = choice(reviews)  # take one random review from the reviews of the preprint
            sampled_non_cognate_review_chunks.append(review.get_chunks(self.chunking_fn)) 
        similarities_null = self._compare(sampled_preprint_chunks, sampled_non_cognate_review_chunks)

        return {
            "null": similarities_null,
            "enriched": similarities_enriched,
        }
    
    def _compare(self, chunk_list_1: List[List[str]], chunk_list_2: List[List[str]]) -> List[float]:
        assert len(chunk_list_1) == len(chunk_list_2), "The number of chunks in the two chunk lists must be the same."
        similarities = []
        for chunks_1, chunks_2 in zip(chunk_list_1, chunk_list_2):
            s = self.comparator.compare_dot(chunks_1, chunks_2)
            similarities += s.view(-1).tolist()  # flatten the similarity matrix
        return similarities
