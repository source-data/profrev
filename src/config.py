from dataclasses import dataclass


"""Application-wide preferences"""


@dataclass
class Config:
    """Application-wide preferences.

    Fields:
        embedding_model: The model to use for the embedding.
    """
    embedding_model: str


config = Config(
    embedding_model="text-similarity-babbage-001"
)
