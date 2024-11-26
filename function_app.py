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

# Initialize credentials based on the availability of AI_VISION_KEY
if AI_VISION_KEY:
    credential = AzureKeyCredential(AI_VISION_KEY)
    logging.info("Using API key for authentication.")
else:
    credential = DefaultAzureCredential()
    logging.info("Using Managed Identity for authentication.")

# Initialize the AI Vision client with the selected credentials
ai_vision_client = ImageAnalysisClient(
    endpoint=AI_VISION_ENDPOINT,
    credential=credential,
)


@app.route(route="aivisionapiv4", auth_level=func.AuthLevel.FUNCTION)
def aivisionapiv4(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Function 'aivisionapiv4' invoked.")

    try:
        req_body = req.get_json()
        logging.debug(f"Request body: {req_body}")
    except ValueError as e:
        logging.error(f"Invalid JSON in request: {e}")
        return func.HttpResponse(
            body=json.dumps({"error": "Invalid JSON in request."}),
            status_code=400,
            mimetype="application/json",
        )

    response = {"values": []}

    for record in req_body.get("values", []):
        record_id = record.get("recordId")
        logging.debug(f"Processing record ID: {record_id}")
        data = record.get("data", {})
        pages = data.get("pages", [])
        outputs = []

        for idx, base64_encoded_image in enumerate(pages):
            logging.debug(f"Processing page {idx+1} for record ID: {record_id}")
            try:
                # Decode the base64 string to bytes
                image_bytes = base64.b64decode(base64_encoded_image)

                result = ai_vision_client.analyze(
                    image_data=image_bytes,
                    visual_features=[
                        VisualFeatures.READ,
                        # VisualFeatures.CAPTION, # not supported in Sweden
                    ],
                    language="en",
                    # gender_neutral_caption=False,
                )

                # Access the 'read' attribute to get the read results
                read_results = result.read

                # Check if 'read_results' is not None
                if read_results is None:
                    logging.warning(
                        f"No read results for page {idx+1} of record ID {record_id}."
                    )
                    document_content = ""
                else:
                    # Concatenate all extracted text lines
                    document_contents = [
                        line.text
                        for block in read_results.blocks
                        for line in block.lines
                    ]
                    document_content = (
                        " ".join(document_contents) if document_contents else ""
                    )

                outputs.append(
                    {
                        "content": document_content,
                        # "caption": caption_text,
                        # "caption_confidence": caption_confidence,
                    }
                )
                logging.debug(
                    f"Successfully processed page {idx+1} for record ID: {record_id}"
                )

            except AzureError as e:
                logging.error(
                    f"Azure Error processing page {idx+1} for record ID {record_id}: {e}"
                )
                outputs.append(
                    {"error": f"Azure Error processing page {idx+1}: {str(e)}"}
                )
            except Exception as e:
                logging.error(
                    f"Unexpected error processing page {idx+1} for record ID {record_id}: {e}"
                )
                outputs.append(
                    {"error": f"Unexpected error processing page {idx+1}: {str(e)}"}
                )

        response["values"].append({"recordId": record_id, "data": {"outputs": outputs}})

    return func.HttpResponse(
        body=json.dumps(response), status_code=200, mimetype="application/json"
    )
