import json
import logging
import os
import base64

import azure.functions as func
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError
from azure.identity import DefaultAzureCredential

app = func.FunctionApp()

AI_VISION_ENDPOINT = os.getenv("AI_VISION_ENDPOINT")
AI_VISION_KEY = os.getenv("AI_VISION_KEY")

# Initialize credentials
credential = (
    AzureKeyCredential(AI_VISION_KEY) if AI_VISION_KEY else DefaultAzureCredential()
)
auth_method = "API key" if AI_VISION_KEY else "Managed Identity"
logging.info(f"Using {auth_method} for authentication.")

# Initialize the AI Vision client
ai_vision_client = ImageAnalysisClient(
    endpoint=AI_VISION_ENDPOINT,
    credential=credential,
)


@app.route(route="aivisionapiv4", auth_level=func.AuthLevel.FUNCTION)
def aivisionapiv4(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Function 'aivisionapiv4' invoked.")

    try:
        req_body = req.get_json()
    except ValueError:
        logging.error("Invalid JSON in request.")
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON in request."}),
            status_code=400,
            mimetype="application/json",
        )

    response = {"values": []}
    document_caption = ""  # Initialize document-level caption

    for record in req_body.get("values", []):
        record_id = record.get("recordId")
        logging.debug(f"Processing record ID: {record_id}")

        image_base64 = record.get("data", {}).get("image")
        if not image_base64:
            error_msg = "No image data provided."
            logging.error(error_msg)
            response["values"].append(
                {
                    "recordId": record_id,
                    "errors": [{"message": error_msg}],
                }
            )
            continue

        try:
            image_bytes = base64.b64decode(image_base64)

            result = ai_vision_client.analyze(
                image_data=image_bytes,
                visual_features=[VisualFeatures.READ, VisualFeatures.CAPTION],
                language="en",
            )

            if result.read and result.read.blocks:
                document_contents = [
                    line.text for block in result.read.blocks for line in block.lines
                ]
                document_content = " ".join(document_contents)
            else:
                logging.warning(f"No read results for record ID: {record_id}.")
                document_content = ""

            if result.caption:
                caption = result.caption.text
                logging.info(f"Caption: {caption}")
                # Assign caption to document-level variable
                document_caption = caption
            else:
                logging.warning(f"No caption results for record ID: {record_id}.")
                caption = ""

            response["values"].append(
                {
                    "recordId": record_id,
                    "data": {"image_text": document_content, "caption": caption},
                }
            )

        except AzureError as e:
            error_msg = f"Azure Error processing record ID {record_id}: {e}"
            logging.error(error_msg)
            response["values"].append(
                {
                    "recordId": record_id,
                    "errors": [{"message": error_msg}],
                }
            )

        except Exception as e:
            error_msg = f"Unexpected error processing record ID {record_id}: {e}"
            logging.error(error_msg)
            response["values"].append(
                {
                    "recordId": record_id,
                    "errors": [{"message": error_msg}],
                }
            )

    # Build the response with the document-level caption
    response = {
        "values": [
            {
                "recordId": record.get("recordId"),
                "data": {
                    "image_text": document_content,
                    "caption": document_caption,  # Provide caption at document level
                },
            }
        ]
    }
    return func.HttpResponse(
        json.dumps(response),
        status_code=200,
        mimetype="application/json",
    )
