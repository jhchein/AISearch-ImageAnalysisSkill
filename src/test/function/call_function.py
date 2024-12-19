import base64
import requests
import os
import logging
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
FUNCTION_ENDPOINT = os.getenv("FUNCTION_ENDPOINT")
FUNCTION_APP_CLIENT_ID = os.getenv("FUNCTION_APP_CLIENT_ID")
FUNCTION_KEY = os.getenv("FUNCTION_KEY")

if FUNCTION_KEY is None:
    logger.info("No function key provided. Using managed identity.")
    credential = DefaultAzureCredential()
    try:
        token = credential.get_token("api://{FUNCTION_APP_CLIENT_ID}/.default").token
        headers["Authorization"] = f"Bearer {token}"
        logger.info("Access token obtained and added to headers.")
    except Exception as e:
        logger.error(f"Error obtaining access token: {e}")
        raise
else:
    logger.info("Function key provided. Using API key.")

uri = f"{FUNCTION_ENDPOINT}/api/aivisionapiv4"

params = {}
if FUNCTION_KEY is not None:
    params["code"] = FUNCTION_KEY
params["use_caption"] = "false"

image_file = "thrive35.png"

# Convert to base64
try:
    with open(image_file, "rb") as image:
        image_base64 = base64.b64encode(image.read()).decode("utf-8")
    logger.info("Image converted to base64 successfully.")
except Exception as e:
    logger.error(f"Error converting image to base64: {e}")
    raise

data = {
    "values": [
        {
            "recordId": "1",
            "data": {
                "image": image_base64,
            },
        }
    ]
}

headers = {"Content-Type": "application/json"}

try:
    response = requests.post(uri, json=data, headers=headers, params=params)
    response.raise_for_status()
    logger.info("Request sent successfully.")
    logger.info(f"Response: {response.json()}")
except requests.exceptions.RequestException as e:
    logger.error(f"Error sending request: {e}")
    raise
