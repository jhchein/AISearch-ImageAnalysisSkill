import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Azure credentials and settings
SUBSCRIPTION_ID = os.getenv("SUBSCRIPTION_ID")
RESOURCE_GROUP_NAME = os.getenv("RESOURCE_GROUP_NAME")

USECASE_NAME = os.getenv("USECASE_NAME")
AI_SEARCH_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT")
AI_SEARCH_ADMIN_KEY = os.getenv("AI_SEARCH_ADMIN_KEY")
AI_SEARCH_SEARCH_API_VERSION = os.getenv("AI_SEARCH_API_VERSION")
AI_SEARCH_SKILLSET_API_VERSION = os.getenv("AI_SEARCH_SKILLSET_API_VERSION")
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
# storage_account_connection_string = os.getenv("STORAGE_ACCOUNT_CONNECTION_STRING")
STORAGE_ACCOUNT_CONTAINER = os.getenv("STORAGE_ACCOUNT_CONTAINER")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.getenv(
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"
)
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AI_MULTIACCOUT_KEY = os.getenv("AI_MULTIACCOUT_KEY")

FUNCTION_KEY = os.getenv("FUNCTION_KEY")
FUNCTION_ENDPOINT = os.getenv("FUNCTION_ENDPOINT")

FUNCTION_APP_CLIENT_ID = os.getenv("FUNCTION_APP_CLIENT_ID")
