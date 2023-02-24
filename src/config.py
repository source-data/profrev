from dataclasses import dataclass
from typing import Dict

"""Application-wide preferences"""


@dataclass
class Config:
    """Application-wide preferences.

    Fields:
        embedding_model: The model to use for the embedding.
    """
    embedding_model: Dict[str, str]
    # embedding_ctx_length: int
    # embedding_encoding: str
    section: str


config = Config(
    embedding_model={
        "openai": "text-similarity-babbage-001",
        "sbert": "paraphrase-MiniLM-L6-v2",
    },
    # embedding_ctx_length=8191,
    # embedding_encoding="cl100k_base",
    section="results",
)
