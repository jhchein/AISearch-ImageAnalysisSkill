import uuid

from config import (
    AI_MULTIACCOUT_KEY,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
    AZURE_OPENAI_ENDPOINT,
    FUNCTION_APP_CLIENT_ID,
    FUNCTION_ENDPOINT,
    FUNCTION_KEY,
    RESOURCE_GROUP_NAME,
    STORAGE_ACCOUNT_CONTAINER,
    STORAGE_ACCOUNT_NAME,
    SUBSCRIPTION_ID,
    USECASE_NAME,
)

# Names
index_name = f"{USECASE_NAME}-index"
indexer_name = f"{USECASE_NAME}-indexer"
data_source_name = f"{USECASE_NAME}-datasource"
skillset_name = f"{USECASE_NAME}-skillset"
x_ms_client_request_id = str(uuid.uuid4())


# Connection string for managed identity
storage_account_connection_string = f"ResourceId=/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.Storage/storageAccounts/{STORAGE_ACCOUNT_NAME};"

datasource_definition = {
    "name": data_source_name,
    "description": "Azure Blob Storage data source",
    "type": "azureblob",
    "credentials": {"connectionString": storage_account_connection_string},
    "container": {"name": STORAGE_ACCOUNT_CONTAINER},
}

index_definition = {
    "name": index_name,
    "vectorSearch": {
        "profiles": [{"name": "profile", "algorithm": "algorithm"}],
        "algorithms": [{"name": "algorithm", "kind": "hnsw"}],
    },
    "fields": [
        {
            "name": "chunk_id",
            "type": "Edm.String",
            "searchable": True,
            "filterable": False,
            "retrievable": True,
            "stored": True,
            "sortable": True,
            "facetable": False,
            "key": True,
            "analyzer": "keyword",
        },
        {
            "name": "text_parent_id",
            "type": "Edm.String",
            "searchable": False,
            "filterable": True,
            "retrievable": True,
            "stored": True,
            "sortable": False,
            "facetable": False,
            "key": False,
        },
        {
            "name": "chunk",
            "type": "Edm.String",
            "searchable": True,
            "filterable": False,
            "retrievable": True,
            "stored": True,
            "sortable": False,
            "facetable": False,
            "key": False,
        },
        {
            "name": "title",
            "type": "Edm.String",
            "searchable": True,
            "filterable": False,
            "retrievable": True,
            "stored": True,
            "sortable": False,
            "facetable": False,
            "key": False,
        },
        {
            "name": "text_vector",
            "type": "Collection(Edm.Single)",
            "searchable": True,
            "filterable": False,
            "retrievable": True,
            "stored": True,
            "sortable": False,
            "facetable": False,
            "key": False,
            "dimensions": 1536,
            "vectorSearchProfile": "profile",
        },
        {
            "name": "image_text",
            "type": "Edm.String",
            "searchable": True,
            "filterable": False,
            "retrievable": True,
            "stored": True,
            "sortable": False,
            "facetable": False,
            "key": False,
        },
        {
            "name": "caption",
            "type": "Edm.String",
            "searchable": True,
            "filterable": False,
            "retrievable": True,
            "stored": True,
            "sortable": False,
            "facetable": False,
            "key": False,
        },
        {
            "name": "language_code",
            "type": "Edm.String",
            "searchable": False,
            "filterable": True,
            "retrievable": True,
            "stored": True,
            "sortable": True,  # Maybe sortable if useful
            "facetable": True,  # Facetable makes sense for language
            "key": False,
        },
    ],
}

skillset_definition = {
    "name": skillset_name,
    "description": "A skillset for structure-aware chunking and vectorization with a index projection around markdown section",
    "skills": [
        {
            "@odata.type": "#Microsoft.Skills.Text.LanguageDetectionSkill",
            "name": "language_detection_skill",
            "description": "Detects the language of the document content",
            "context": "/document",
            "inputs": [
                {
                    "name": "text",
                    "source": "/document/content",
                }
            ],
            "outputs": [
                {
                    "name": "languageCode",
                    "targetName": "languageCode",
                }
            ],
            "defaultLanguageCode": "en",
        },
        {
            "@odata.type": "#Microsoft.Skills.Custom.WebApiSkill",
            "name": "image_analysis_skill",
            "description": "Extracts text and captions from images using Azure AI Vision Image Analysis v4.0",
            "uri": f"{FUNCTION_ENDPOINT}/api/aivisionapiv4?code={FUNCTION_KEY}&use_caption=true",
            "authResourceId": f"api://{FUNCTION_APP_CLIENT_ID}/.default",  #  This property takes an application (client) ID or app's registration in Microsoft Entra ID, in any of these formats: api://<appId>, <appId>/.default, api://<appId>/.default
            "httpMethod": "POST",
            "batchSize": 4,
            "degreeOfParallelism": 5,  # (Optional) When specified, indicates the number of calls the indexer makes in parallel to the endpoint you provide. You can decrease this value if your endpoint is failing under pressure, or raise it if your endpoint can handle the load. If not set, a default value of 5 is used. The degreeOfParallelism can be set to a maximum of 10 and a minimum of 1.
            "context": "/document/normalized_images/*",
            "inputs": [
                {"name": "image", "source": "/document/normalized_images/*/data"},
                {
                    "name": "languageCode",
                    "source": "/document/languageCode",
                },
            ],
            "outputs": [
                {"name": "image_text", "targetName": "image_text"},
                {"name": "caption", "targetName": "caption"},
            ],
        },
        {
            "@odata.type": "#Microsoft.Skills.Text.MergeSkill",
            "name": "merge_skill",
            "description": "Create mergedText with all textual representations.",
            "context": "/document",
            "insertPreTag": " ",
            "insertPostTag": " ",
            "inputs": [
                {"name": "text", "source": "/document/content"},
                {
                    "name": "itemsToInsert",
                    "source": "/document/normalized_images/*/image_text",
                },
                {
                    "name": "offsets",
                    "source": "/document/normalized_images/*/contentOffset",
                },
            ],
            "outputs": [{"name": "mergedText", "targetName": "mergedText"}],
        },
        {
            "@odata.type": "#Microsoft.Skills.Text.SplitSkill",
            "name": "markdown_section_split_skill",
            "description": "A skill that splits text into chunks",
            "context": "/document",  # Updated context
            "inputs": [
                {
                    "name": "text",
                    "source": "/document/mergedText",
                }
            ],
            "outputs": [{"name": "textItems", "targetName": "pages"}],
            "defaultLanguageCode": "en",
            "textSplitMode": "pages",
            "maximumPageLength": 2000,
            "pageOverlapLength": 500,
            "unit": "characters",
        },
        {
            "@odata.type": "#Microsoft.Skills.Text.AzureOpenAIEmbeddingSkill",
            "name": "my_azure_openai_embedding_skill",
            "context": "/document/pages/*",
            "inputs": [
                {
                    "name": "text",
                    "source": "/document/pages/*",
                    "inputs": [],
                }
            ],
            "outputs": [{"name": "embedding", "targetName": "text_vector"}],
            "resourceUri": AZURE_OPENAI_ENDPOINT,
            "deploymentId": AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
            "apiKey": AZURE_OPENAI_API_KEY,
            "modelName": AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
        },
    ],
    "cognitiveServices": {
        "@odata.type": "#Microsoft.Azure.Search.CognitiveServicesByKey",
        "key": AI_MULTIACCOUT_KEY,
    },
    "indexProjections": {
        "selectors": [
            {
                "targetIndexName": index_name,
                "parentKeyFieldName": "text_parent_id",
                "sourceContext": "/document/pages/*",
                "mappings": [
                    {
                        "name": "text_vector",
                        "source": "/document/pages/*/text_vector",
                    },
                    {"name": "chunk", "source": "/document/pages/*"},
                    {"name": "title", "source": "/document/title"},
                    {
                        "name": "language_code",
                        "source": "/document/languageCode",
                    },
                    {
                        "name": "caption",
                        "source": "/document/normalized_images/*/caption",
                    },
                    # NOTE: This mapping might put the *same* caption on *every* chunk from a document.
                    # Consider if this is desired or if caption should be stored differently.
                ],
            }
        ],
        "parameters": {"projectionMode": "skipIndexingParentDocuments"},
    },
}

indexer_definition = {
    "name": indexer_name,
    "dataSourceName": data_source_name,
    "targetIndexName": index_name,
    "skillsetName": skillset_name,
    "parameters": {
        "batchSize": 1,
        "configuration": {
            "dataToExtract": "contentAndMetadata",
            "imageAction": "generateNormalizedImages",
            "parsingMode": "default",
            "allowSkillsetToReadFileData": True,
        },
    },
    "fieldMappings": [
        {"sourceFieldName": "metadata_storage_path", "targetFieldName": "title"}
        # Add mapping for language if you added the field to the index and want the raw detected code stored
        # Note: The projection already maps /document/languageCode to the index field "language_code"
        # So, no explicit fieldMapping is needed here *if* the indexProjection handles it.
    ],
    "outputFieldMappings": [
        # Maps outputs from the enrichment tree directly to index fields *if not handled by indexProjections*
        # We added language_code to index projections, so it's handled there.
        # If you wanted image_text or caption directly in the index (not just per chunk via projection),
        # you might add mappings here, but context needs careful consideration.
        # Example (if NOT using projection for caption):
        # {
        #    "sourceFieldName": "/document/normalized_images/*/caption", # Might need aggregation/selection logic
        #    "targetFieldName": "caption"
        # }
    ],
}
