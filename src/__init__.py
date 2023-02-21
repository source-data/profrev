from dotenv import load_dotenv
import os
import openai

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_ORG_KEY = os.getenv('OPENAI_ORG_KEY')
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

#register to openai API
openai.api_key = OPENAI_API_KEY
openai.organization = OPENAI_ORG_KEY