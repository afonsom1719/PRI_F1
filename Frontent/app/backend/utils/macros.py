import os
from dotenv import load_dotenv

load_dotenv("./.azure/arada-ai-demo/.env")

print(os.getenv("AZURE_SEARCH_SERVICE"))

FILE_UPLOAD_CONTAINER = os.getenv("AZURE_FILE_UPLOAD_CONTAINER")
CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
SAS_TOKEN = os.getenv("AZURE_BLOB_SAS_TOKEN")
# Configuration constants
TENANT_ID = os.getenv("AZURE_TENANT_ID")
SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE")
STORAGE_KEY = os.getenv("AZURE_STORAGE_KEY")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
SEARCH_INDEXER = os.getenv("AZURE_SEARCH_INDEXER")
# Replace these with your own values, either in environment variables or directly here
AZURE_STORAGE_ACCOUNT = os.environ.get("AZURE_STORAGE_ACCOUNT") or "mystorageaccount"
AZURE_STORAGE_CONTAINER = os.environ.get("AZURE_STORAGE_CONTAINER") or "content"
AZURE_INDEXER_CONTAINER = os.environ.get("AZURE_FILE_UPLOAD_CONTAINER") or "indexer"
AZURE_SEARCH_SERVICE = os.environ.get("AZURE_SEARCH_SERVICE") or "gptkb-ai-demo"
AZURE_SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX") or "gptkbindex"
AZURE_OPENAI_SERVICE = os.environ.get("AZURE_OPENAI_SERVICE") or "openai-demo-arada"
AZURE_OPENAI_GPT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_GPT_DEPLOYMENT") or "text-davinci-003"
AZURE_OPENAI_GPT_FUNCTIONS_DEPLOYMENT = (
    os.environ.get("AZURE_OPENAI_GPT_FUNCTIONS_DEPLOYMENT") or "gpt-35-turbo-0613"
)
AZURE_OPENAI_CHATGPT_DEPLOYMENT = (
    os.environ.get("AZURE_OPENAI_CHATGPT_DEPLOYMENT") or "gpt-35-turbo"
)
API_VERSION = os.environ.get("API_VERSION") or "2023-07-01-preview"

KB_FIELDS_CONTENT = os.environ.get("KB_FIELDS_CONTENT") or "content"
KB_FIELDS_CATEGORY = os.environ.get("KB_FIELDS_CATEGORY") or "category"
KB_FIELDS_SOURCEPAGE = os.environ.get("KB_FIELDS_SOURCEPAGE") or "sourcepage"

API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_LOCATION = "eastus"

API_TYPE = os.environ.get("API_TYPE") or "azure"
TRANSLATION_KEY = os.environ.get("AZURE_TRANSLATION_KEY")
TRANSLATION_ENDPOINT = os.environ.get("AZURE_TRANSLATION_ENDPOINT")
