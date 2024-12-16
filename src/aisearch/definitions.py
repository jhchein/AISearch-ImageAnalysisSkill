import uuid
from config import (
    USECASE_NAME,
    STORAGE_ACCOUNT_CONTAINER,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
    AZURE_OPENAI_API_KEY,
    AI_MULTIACCOUT_KEY,
    SUBSCRIPTION_ID,
    RESOURCE_GROUP_NAME,
    STORAGE_ACCOUNT_NAME,
    FUNCTION_ENDPOINT,
    APP_ID,
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
            "name": "caption",  # New field for image captions
            "type": "Edm.String",
            "searchable": True,
            "filterable": False,
            "retrievable": True,
            "stored": True,
            "sortable": False,
            "facetable": False,
            "key": False,
        },
    ],
}

skillset_definition = {
    "name": skillset_name,
    "description": "A skillset for structure-aware chunking and vectorization with a index projection around markdown section",
    "skills": [
        {
            "@odata.type": "#Microsoft.Skills.Custom.WebApiSkill",
            "description": "A custom skill that can identify positions of different phrases in the source text",
            "uri": f"{FUNCTION_ENDPOINT}/api/aivisionapiv4",  # Removed the function key
            "authResourceId": f"api://{APP_ID}",  #  This property takes an application (client) ID or app's registration in Microsoft Entra ID, in any of these formats: api://<appId>, <appId>/.default, api://<appId>/.default
            "httpMethod": "POST",
            "batchSize": 4,
            "degreeOfParallelism": 5,  # (Optional) When specified, indicates the number of calls the indexer makes in parallel to the endpoint you provide. You can decrease this value if your endpoint is failing under pressure, or raise it if your endpoint can handle the load. If not set, a default value of 5 is used. The degreeOfParallelism can be set to a maximum of 10 and a minimum of 1.
            "context": "/document/normalized_images/*",
            "inputs": [
                {"name": "image", "source": "/document/normalized_images/*/data"}
            ],
            "outputs": [
                {"name": "image_text", "targetName": "image_text"},
                {"name": "caption", "targetName": "caption"},
            ],
        },
        {
            "@odata.type": "#Microsoft.Skills.Text.MergeSkill",
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
            "name": "my_markdown_section_split_skill",
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
                        "name": "caption",
                        "source": "/document/normalized_images/*/caption",
                    },
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
    ],
    "outputFieldMappings": [],
}
