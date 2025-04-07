# Azure AI Search - AI Vision Image Analysis v4.0 - Custom Web Skill

This repository provides an example of a **Custom Web Skill** for Azure AI Search that leverages **Azure AI Vision Image Analysis v4.0** to perform Optical Character Recognition (OCR) on images. By integrating this custom skill into your search indexing pipeline, you can extract text and captions from images stored in Azure Blob Storage and make them searchable.

## Overview

The project demonstrates how to:

- **Implement an Azure Function App** that acts as a web API, calling Azure AI Vision services to analyze images.
- **Define a Custom Web Skill** in Azure AI Search that invokes the Azure Function App during indexing.
- **Set up Azure AI Search resources**, including data source, index, skillset, and indexer.

## Key Components

- **Azure Function App** (`src/function`):
  - Handles HTTP requests from the Azure AI Search indexer.
  - Uses Managed Identity to authenticate with Azure AI Vision services.
  - Processes images to extract text (`image_text`) and captions (`caption`).

- **Custom Web Skill Definition** (`definitions.py`):
  - Configures the skillset to include the Custom Web Skill.
  - Specifies inputs (image data) and outputs (extracted text and captions).

- **Azure AI Search Scripts** (`src/aisearch`):
  - `setup.py`: Creates or updates the data source, index, skillset, and indexer.
  - `helpers.py`: Provides utility functions to manage the indexer (run, check status, delete resources).

## Getting Started

### Prerequisites

- **Azure Subscription** with permissions to create resources and a Service Principal.
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
- Update `.env` with your Azure resource details and credentials. See `.env.sample` for required variables.

3. **Deploy the Azure Function App**

- Navigate to `src/function`.
- Deploy the Function App to Azure (e.g., using Azure Functions Core Tools or VS Code).
- Ensure the Function App's Managed Identity has the `AI Developer` role on your Azure AI Vision resource.
- Update `FUNCTION_ENDPOINT` in your `.env` file after deployment.

4. **Configure Managed Identity Authentication**

- Follow the steps in [Configure Azure AI Search to Authenticate with the Function App Using Managed Identity](#configure-azure-ai-search-to-authenticate-with-the-function-app-using-managed-identity).

5. **Set Up Azure AI Search Resources**

- Navigate to `src/aisearch`.
- Install dependencies: `pip install -r requirements.txt`.
- Run `setup.py` to create or update the data source, index, skillset, and indexer.

### Custom Web Skill Definition Example

Here's an example of the **Custom Web Skill** definition configured to use the Function Key:

```json
{
  "@odata.type": "#Microsoft.Skills.Custom.WebApiSkill",
  "description": "Extracts text and captions from images using Azure AI Vision Image Analysis v4.0",
  "uri": "https://<your-function-app-name>.azurewebsites.net/api/aivisionapiv4?code=<your-function-key>",
  "authResourceId": "api://<appId>/.default",
  "httpMethod": "POST",
  "batchSize": 4,
  "degreeOfParallelism": 5,
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

Replace `<your-function-app-name>` and `<your-function-key>` with your Azure Function App's details.

## Configure Azure AI Search to Authenticate with the Function App Using Managed Identity

> **Note:** You must have permissions to create a Service Principal in Microsoft Entra ID.

Follow these steps to configure Azure AI Search to authenticate securely with your Azure Function App using Managed Identity:

### 1. Enable Managed Identity for Azure AI Search Service

- In the Azure Portal, navigate to your Azure AI Search Service.
- Under `Settings` > `Identity`, enable the **System Assigned Identity** toggle.
- Copy the `Object (principal) ID`.

### 2. Retrieve the Azure AI Search Service Application ID

- Navigate to `Microsoft Entra ID` in the Azure Portal.
- Select `Enterprise applications` from the left menu.
- Enter the copied `Object (principal) ID` into the search field.
- Click on the matching Azure AI Search Service application and copy the `Application ID`.

### 3. Create an App Registration for the Azure Function App

- In `Microsoft Entra ID`, navigate to `App registrations`.
- Click `+ New Registration`.
- Provide a suitable name, select the appropriate account type (usually Single Tenant), and click `Register`.
- After registration, select `Expose an API` and click `Add` next to "Application ID URI".
- Copy the generated `Application ID URI`.

### 4. Configure Authentication (Easy Auth) in the Azure Function App

- In the Azure Portal, navigate to your Azure Function App.
- Under `Authentication`, add the Microsoft identity provider.
- Enter the `Application (client) ID` and `client secret` from the App Registration you created.
- Under `Client application requirement`, select `Allow requests from specific client applications` and add:
  - The `Application (client) ID` of the App Registration you created.
  - The `Application ID` of your Azure AI Search Service.
- Under `Unauthenticated requests`, select `HTTP 401 Unauthorized`.
- Save your changes.

### 5. Update Skillset Configuration for Managed Identity Authentication

- Add the Service Principal's `client ID` (from the App Registration) as `FUNCTION_APP_CLIENT_ID` in your `.env` file.

## Troubleshooting

- **401 Unauthorized Errors:** Ensure the Managed Identity configuration is correct, and the Application IDs are correctly set in your `.env` file and skill definitions.
- **Indexer Errors:** Use `helpers.py` to check the indexer status and logs for detailed error messages.

## Notes

- **Authentication:**
  - The Azure Function App uses its **system-assigned Managed Identity** to authenticate with Azure AI Vision services.

- **Environment Variables:**
  - Ensure all required variables are set in your `.env` file and Azure Function App settings.

- **Data Source:**
  - The data source should point to your Azure Blob Storage container containing the images to be indexed.

## Additional Information

- **Testing the Azure Function App:**
  - A test script is available in `src/test/function/call_function.py` to validate the Azure Function App independently.

- **Managing the Indexer:**
  - Use `helpers.py` to run or check the status of the indexer, and to delete resources if needed.

## To-Do Items

- [x] Implement Azure Function App using Managed Identity to call Azure AI Vision.
- [x] Create scripts for Azure AI Search resource setup.
- [x] Test and adjust the skillset and index schema.
- [x] Remove API keys from the Azure Function App environment variables.
- [x] Enable Managed Identity for Azure AI Search to call the Azure Function App (planned future enhancement).

## Additional Information

- **Testing the Azure Function App:**
  - A test script is available in `src/test/function/call_function.py` to validate the Azure Function App independently.

- **Secure App Authentication:**
  - For more details, see [Secure App Authentication in Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/scenario-secure-app-authentication-app-service?tabs=workforce-configuration).
