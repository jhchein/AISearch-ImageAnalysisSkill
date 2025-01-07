# Azure AI Search - AI Vision Image Analysis v4.0 - Custom Web Skill

This repository provides an example of a **Custom Web Skill** for Azure AI Search that leverages **AI Vision Image Analysis v4.0** to perform Optical Character Recognition (OCR) on images. By integrating this custom skill into your search indexing pipeline, you can extract text and captions from images stored in Azure Blob Storage and make them searchable.

## Overview

The project demonstrates how to:

- **Implement an Azure Function App** that acts as a web API, calling AI Vision services to analyze images.
- **Define a custom skill** in Azure AI Search that invokes the Function App during indexing.
- **Set up Azure AI Search resources** including data source, index, skillset, and indexer.

## Key Components

- **Azure Function App** (`src/function`):
  - Handles HTTP requests from the search indexer.
  - Uses Managed Identity to authenticate with AI Vision services.
  - Processes images to extract text (`image_text`) and captions (`caption`).

- **Custom Web Skill Definition** (`definitions.py`):
  - Configures the skillset to include the custom skill.
  - Specifies inputs (image data) and outputs (extracted text and captions).

- **Azure AI Search Scripts** (`src/aisearch`):
  - `setup.py`: Creates or updates the data source, index, skillset, and indexer.
  - `helpers.py`: Provides utility functions to manage the indexer (run, check status, delete resources).

## Getting Started

### Prerequisites

- **Azure Subscription** with access to create resources.
- **Azure AI Search Service**.
- **Azure AI Vision Service** (Multi-Account).
- **Azure Storage Account** containing your images.
- **Python 3.11+** installed locally.
- Familiarity with Azure services and command-line tools.

### Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/jhchein/customwebskill.git
   cd customwebskill
   ```

2. **Configure Environment Variables**

   - Copy `.env.sample` to `.env`.
   - Update `.env` with your Azure resource details and credentials.

3. **Deploy the Azure Function App**

   - Navigate to `src/function`.
   - Deploy the Function App to Azure (e.g., using Azure Functions Core Tools or VS Code).
   - Ensure the Function App's Managed Identity has the `Cognitive Services User` role on your AI Vision resource.
   - Update `FUNCTION_ENDPOINT` and `FUNCTION_KEY` in your `.env` file after deployment.

4. **Set Up Azure AI Search Resources**

   - Navigate to `src/aisearch`.
   - Install dependencies: `pip install -r requirements.txt`.
   - Run `setup.py` to create or update the data source, index, skillset, and indexer.
   - The `definitions.py` file contains configurations for these resources.

### Skill Definition Example

An example of the **Custom Web Skill** definition:

```json
{
  "@odata.type": "#Microsoft.Skills.Custom.WebApiSkill",
  "description": "Extracts text and captions from images using AI Vision Image Analysis v4.0",
  "uri": "https://<your-function-app-name>.azurewebsites.net/api/aivisionapiv4?code=<FunctionKey>",
  "httpMethod": "POST",
  "batchSize": 4,
  "context": "/document/normalized_images/*",
  "inputs": [
    { "name": "image", "source": "/document/normalized_images/*/data" }
  ],
  "outputs": [
    { "name": "image_text", "targetName": "image_text" },
    { "name": "caption", "targetName": "caption" }
  ]
}
```

Replace `<your-function-app-name>` and `<FunctionKey>` with your Function App's details.

## Notes

- **Authentication:**
  - The Function App uses its **system-assigned Managed Identity** to authenticate with AI Vision services.
  - The search indexer currently authenticates to the Function App via the function key. Implementing Managed Identity for this interaction is a future enhancement.

- **Environment Variables:**
  - Ensure all required variables are set in your `.env` file and Azure Function App settings.

- **Data Source:**
  - The data source should point to your Azure Blob Storage container containing the images to be indexed.

## Additional Information

- **Testing the Function App:**
  - A test script is available in `src/test/function/call_function.py` to validate the Function App independently.

- **Managing the Indexer:**
  - Use `helpers.py` to run or check the status of the indexer, and to delete resources if needed.

## To-Do Items

- [x] Implement Function App using Managed Identity to call AI Vision.
- [x] Create scripts for Azure AI Search resource setup.
- [x] Test and adjust the skillset and index schema.
- [x] Remove API keys from the Function App environment variables.
- [ ] **Enhancement:** Enable Managed Identity for Azure AI Search to call the Function App (remove function key from the skill definition).

## Contributing

Contributions are welcome. Feel free to open issues or submit pull requests to enhance the functionality or fix any problems.

````
