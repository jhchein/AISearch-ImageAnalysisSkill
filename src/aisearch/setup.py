from azure_search_client import create_resource
from config import (
    AI_SEARCH_ADMIN_KEY,
    AI_SEARCH_ENDPOINT,
    AI_SEARCH_SEARCH_API_VERSION,
    AI_SEARCH_SKILLSET_API_VERSION,
)
from definitions import (
    data_source_name,
    datasource_definition,
    index_definition,
    index_name,
    indexer_definition,
    indexer_name,
    skillset_definition,
    skillset_name,
    x_ms_client_request_id,
)
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

headers = {
    "x-ms-client-request-id": x_ms_client_request_id,
    "api-key": AI_SEARCH_ADMIN_KEY,
}


def main():
    resource_urls = {
        "datasource": f"{AI_SEARCH_ENDPOINT}/datasources/{data_source_name}?api-version={AI_SEARCH_SEARCH_API_VERSION}",
        "index": f"{AI_SEARCH_ENDPOINT}/indexes/{index_name}?api-version={AI_SEARCH_SEARCH_API_VERSION}",
        "skillset": f"{AI_SEARCH_ENDPOINT}/skillsets/{skillset_name}?api-version={AI_SEARCH_SKILLSET_API_VERSION}",
        "indexer": f"{AI_SEARCH_ENDPOINT}/indexers/{indexer_name}?api-version={AI_SEARCH_SEARCH_API_VERSION}",
    }

    create_resource(
        resource_urls["datasource"], headers, datasource_definition, "Data Source"
    )
    create_resource(resource_urls["index"], headers, index_definition, "Index")
    create_resource(resource_urls["skillset"], headers, skillset_definition, "Skillset")
    create_resource(resource_urls["indexer"], headers, indexer_definition, "Indexer")


if __name__ == "__main__":
    main()
