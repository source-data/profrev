from dataclasses import dataclass
from typing import Dict

"""Application-wide preferences"""


@dataclass
class Config:
    """Application-wide preferences.

    Fields:
        embedding_model: The model to use for the embedding.
    """
    min_length: int
    embedding_model: Dict[str, str]
    # embedding_ctx_length: int
    # embedding_encoding: str
    sections: str


config = Config(
    min_length=70,
    embedding_model={
        # https://platform.openai.com/docs/models/gpt-3
        "openai": "text-embedding-ada-002",  # "text-embedding-ada-002", "text-similarity-curie-001", "text-similarity-babbage-001", "text-similarity-davinci-001", 
        # https://www.sbert.net/docs/pretrained_models.html
        "sbert": "all-mpnet-base-v2",  #"all-MiniLM-L6-v2", "all-mpnet-base-v2", "multi-qa-mpnet-base-dot-v1","text-embedding-ada-002"
        "barlow": "/pretrained/twin-no-lm-diag-diag", # "/app/pretrained/twin-no-lm-checkpoint-32000", "/app/pretrained/twin-lm-checkpoint-32000"
    },
    # embedding_ctx_length=8191,
    # embedding_encoding="cl100k_base",
    sections="introduction+results+discussion+methods",
)
