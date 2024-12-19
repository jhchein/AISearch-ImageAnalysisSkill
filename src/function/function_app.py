import json
import logging
import os
import base64

import azure.functions as func
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.exceptions import AzureError
from azure.identity import ManagedIdentityCredential

app = func.FunctionApp()

AI_VISION_ENDPOINT = os.getenv("AI_VISION_ENDPOINT")

# Initialize credentials
credential = ManagedIdentityCredential()

auth_method = "Managed Identity"
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
    except ValueError as ve:
        logging.error("Invalid JSON in request.", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON in request."}),
            status_code=400,
            mimetype="application/json",
        )

    use_caption = req.params.get("use_caption", "false").lower() == "true"

    response = {"values": []}
    document_caption = ""  # Initialize document-level caption
    document_content = ""  # Initialize document_content

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

            visual_features = [VisualFeatures.READ]
            if use_caption:
                visual_features.append(VisualFeatures.CAPTION)

            result = ai_vision_client.analyze(
                image_data=image_bytes,
                visual_features=visual_features,
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

            if use_caption and result.caption:
                caption = result.caption.text
                logging.info(f"Caption: {caption}")
                # Assign caption to document-level variable
                document_caption = caption
            else:
                if use_caption:
                    logging.warning(f"No caption results for record ID: {record_id}.")
                caption = ""

            data = {"image_text": document_content}
            if use_caption:
                data["caption"] = caption

            response["values"].append(
                {
                    "recordId": record_id,
                    "data": data,
                }
            )

        except AzureError as e:
            error_msg = f"Azure Error processing record ID {record_id}: {e}"
            logging.error(error_msg, exc_info=True)
            response["values"].append(
                {
                    "recordId": record_id,
                    "errors": [{"message": error_msg}],
                }
            )

        except Exception as e:
            error_msg = f"Unexpected error processing record ID {record_id}: {e}"
            logging.error(error_msg, exc_info=True)
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
