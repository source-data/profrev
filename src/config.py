from dataclasses import dataclass


"""Application-wide preferences"""


@dataclass
class Config:
    """Application-wide preferences.

    Fields:
        embedding_model: The model to use for the embedding.
    """
    embedding_model: str
    embedding_size: int
    # embedding_ctx_length: int
    # embedding_encoding: str


config = Config(
    embedding_model="text-similarity-babbage-001",
    # embedding_ctx_length=8191,
    # embedding_encoding="cl100k_base",
    embedding_size=2048
)
