from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
openapi_api_key = os.getenv('OPENAPI_API_KEY')
openapi_org_key = os.getenv('OPENAPI_ORG_KEY')
