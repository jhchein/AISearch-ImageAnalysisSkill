# Azure AI Search - AI Vision Image Analysis v4.0 - Custom Web Skill

This repository contains an example AI Search Custom Web Skill that calls AI Vision Image Analysis v4.0 (for OCR). This README contains the Skill Definition, the rest of the files are code for the Azure Function Web API.

## Setup

- Create a consumption Azure Function App.

- Create an Azure AI Services Multi-Account if you don't have one already.
  - Ensure it's in a region that supports AI Vision Image Analysis API v4.0 and its features. See [regional availability](https://learn.microsoft.com/azure/ai-services/computer-vision/overview-image-analysis?tabs=4-0#region-availability).

- Deploy this function app code to the Function App.

- Set the environment variables in your `.env` file based on the provided `.env.sample` file. Ensure that `AI_VISION_ENDPOINT` is set as an Azure Function environment variable.

- Add a new skill to your Azure AI Search Skillset, as defined below.
  - Update the `uri` with your function's URL (e.g., `https://<yourfunctionnameandregion>.azurewebsites.net/api/aivisionapiv4?code=<YourFunctionKey>`).

- Assign the `Cognitive Services Contributor` role to the Function App to allow it to call the AI Services Multi-Account.

### Example Skill:

```JSON
{
  "@odata.type": "#Microsoft.Skills.Custom.WebApiSkill",
  "description": "A custom skill that can identify positions of different phrases in the source text",
  "uri": "https://<your-function-name-and-region>.azurewebsites.net/api/aivisionapiv4?code=<YourFunctionKey>", # The Azure Function you deployed.
//   "authResourceId": "<Azure-AD-registered-application-ID>", # authResourceId tells the search service to connect using a managed identity, passing the application ID of the target function or app in the property.
  "httpMethod": "POST",
  "batchSize": 4,
  "degreeOfParallelism": 5, # (Optional) When specified, indicates the number of calls the indexer makes in parallel to the endpoint you provide. You can decrease this value if your endpoint is failing under pressure, or raise it if your endpoint can handle the load. If not set, a default value of 5 is used. The degreeOfParallelism can be set to a maximum of 10 and a minimum of 1.
  "context": "/document",
  "inputs": [
   {
        "name": "pages",
        "source": "/document/normalized_images/*/data"
    }
  ],
  "outputs": [
    {
        "name": "image_text",
        "targetName": "image_text" # The index field that you want to populate.
    }
  ]
}
```

The system-managed identity is used automatically if "apikey" and "authIdentity" are empty, as demonstrated in the following example. The "authIdentity" property is used for user-assigned managed identity only.

For more info see the AI Search Custom Web Skill [documentation](https://learn.microsoft.com/en-us/azure/search/cognitive-search-custom-skill-web-api)

## ToDos

- [x] Implement Function
- [x] Test Skill (the schema might be off)
- [x] Create Scripts for AI Search Datasource, Index, Skillset, and Indexer Setup.
- [ ] use managed identity to call the function (to remove the key from the skillset)
