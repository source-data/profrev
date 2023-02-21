from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
OPENAPI_API_KEY = os.getenv('OPENAPI_API_KEY')
OPENAPI_ORG_KEY = os.getenv('OPENAPI_ORG_KEY')
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")