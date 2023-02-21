import pinecone

from .config import config
from . import PINECONE_API_KEY, PINECONE_INDEX_NAME


# a class to index a corpus of reviewed preprints in Pinecone
class PineconeIndexer:
    """A class to index a corpus of reviewed preprints in Pinecone."""
    def __init__(self, corpus_dir: str) -> None:
        # initialize connection to pinecone (get API key at app.pinecone.io)
        pinecone.init(
            api_key=PINECONE_API_KEY,
            environment="us-west1-gcp"
        )
        # check if 'PINECONE_INDEX_NAME already exists (only create index if not)
        if PINECONE_INDEX_NAME not in pinecone.list_indexes():
            pinecone.create_index(PINECONE_INDEX_NAME, dimension=config["embedding_dim"])
        # connect to index
        self.index = pinecone.Index(PINECONE_INDEX_NAME)
        self.corpus_dir = corpus_dir

    def index(self, index_name: str) -> None:
        """Index the corpus in Pinecone.
        Args:
            index_name: The name of the index.
        """
        index = pinecone.Index(index_name)
        index.create()
        index.index_documents(self.corpus_dir)
