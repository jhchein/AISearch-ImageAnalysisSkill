import json
import logging
import argparse

import requests
from config import (
    AI_SEARCH_ENDPOINT,
    AI_SEARCH_SEARCH_API_VERSION,
    AI_SEARCH_ADMIN_KEY,
)
from definitions import (
    index_name,
    indexer_name,
    skillset_name,
    data_source_name,
    x_ms_client_request_id,
)

logging.basicConfig(level=logging.INFO)


def check_indexer_status(indexer_name, ai_search_endpoint, api_key, api_version):
    """
    Checks the status of the specified indexer and logs the result.

    :param indexer_name: Name of the indexer to check.
    :param ai_search_endpoint: Azure AI Search endpoint URL.
    :param api_key: Azure AI Search API key.
    :param api_version: API version to use.
    :return: JSON response of the last result or raises an HTTP error if the request fails.
    """

    headers = {
        "x-ms-client-request-id": x_ms_client_request_id,
        "api-key": api_key,
    }
    indexer_status_url = f"{ai_search_endpoint}/indexers/{indexer_name}/search.status?api-version={api_version}"
    logging.info(f"Checking status of indexer {indexer_name}")

    response = requests.get(indexer_status_url, headers=headers)
    if response.status_code == 200:
        status = response.json().get("status", "Unknown")
        logging.info(f"Indexer status: {status}")
        last_result = response.json().get("lastResult", {})
        logging.info(f"Last result: {json.dumps(last_result, indent=2)}")
        return last_result
    else:
        logging.error(f"Status code: {response.status_code}")
        logging.error(f"Failed to get indexer status: {response.text}")
        response.raise_for_status()


def run_indexer(indexer_name, ai_search_endpoint, api_key, api_version):
    """
    Triggers the specified indexer to run and logs the result.

    :param indexer_name: Name of the indexer to run.
    :param ai_search_endpoint: Azure AI Search endpoint URL.
    :param api_key: Azure AI Search API key.
    :param api_version: API version to use.
    :return: JSON response of the run result or raises an HTTP error if the request fails.
    """

    headers = {
        "x-ms-client-request-id": x_ms_client_request_id,
        "api-key": api_key,
    }
    indexer_run_url = f"{ai_search_endpoint}/indexers('{indexer_name}')/search.run?api-version={api_version}"
    logging.info(f"Running indexer {indexer_name}")

    response = requests.post(indexer_run_url, headers=headers)
    if response.status_code == 202:
        try:
            result = response.json()
            logging.info(f"Indexer run result: {json.dumps(result, indent=2)}")
            return result
        except json.JSONDecodeError:
            logging.error("Failed to parse JSON response")
            raise ValueError("Invalid JSON response")
    elif response.status_code == 409:
        logging.info("Indexer is already running")
    else:
        logging.error(f"Status code: {response.status_code}")
        logging.error(f"Failed to run indexer: {response.text}")
        response.raise_for_status()


def delete_resource(resource_url, headers, resource_type):
    """
    Deletes the specified resource.

    :param resource_url: The URL of the resource to delete.
    :param headers: The headers to include in the request.
    :param resource_type: The type of resource being deleted (for logging).
    """
    response = requests.delete(resource_url, headers=headers)
    if response.status_code == 204:
        logging.info(f"{resource_type} deleted successfully.")
    elif response.status_code == 404:
        logging.warning(f"{resource_type} not found.")
    else:
        logging.error(
            f"Failed to delete {resource_type}. Status code: {response.status_code}"
        )
        logging.error(f"Response: {response.text}")


def delete_index():
    headers = {
        "x-ms-client-request-id": x_ms_client_request_id,
        "api-key": AI_SEARCH_ADMIN_KEY,
    }
    index_url = f"{AI_SEARCH_ENDPOINT}/indexes/{index_name}?api-version={AI_SEARCH_SEARCH_API_VERSION}"
    delete_resource(index_url, headers, "Index")


def delete_indexer():
    headers = {
        "x-ms-client-request-id": x_ms_client_request_id,
        "api-key": AI_SEARCH_ADMIN_KEY,
    }
    indexer_url = f"{AI_SEARCH_ENDPOINT}/indexers/{indexer_name}?api-version={AI_SEARCH_SEARCH_API_VERSION}"
    delete_resource(indexer_url, headers, "Indexer")


def delete_skillset():
    headers = {
        "x-ms-client-request-id": x_ms_client_request_id,
        "api-key": AI_SEARCH_ADMIN_KEY,
    }
    skillset_url = f"{AI_SEARCH_ENDPOINT}/skillsets/{skillset_name}?api-version={AI_SEARCH_SEARCH_API_VERSION}"
    delete_resource(skillset_url, headers, "Skillset")


def delete_datasource():
    headers = {
        "x-ms-client-request-id": x_ms_client_request_id,
        "api-key": AI_SEARCH_ADMIN_KEY,
    }
    datasource_url = f"{AI_SEARCH_ENDPOINT}/datasources/{data_source_name}?api-version={AI_SEARCH_SEARCH_API_VERSION}"
    delete_resource(datasource_url, headers, "Data Source")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Manage Azure Cognitive Search resources"
    )
    parser.add_argument(
        "--status", action="store_true", help="Check the status of the indexer"
    )
    parser.add_argument("--run", action="store_true", help="Trigger the indexer to run")
    parser.add_argument("--delete-index", action="store_true", help="Delete the index")
    parser.add_argument(
        "--delete-indexer", action="store_true", help="Delete the indexer"
    )
    parser.add_argument(
        "--delete-skillset", action="store_true", help="Delete the skillset"
    )
    parser.add_argument(
        "--delete-datasource", action="store_true", help="Delete the data source"
    )
    parser.add_argument("--wipe-all", action="store_true", help="Delete all resources")

    args = parser.parse_args()

    try:
        if args.status:
            check_indexer_status(
                indexer_name=indexer_name,
                ai_search_endpoint=AI_SEARCH_ENDPOINT,
                api_key=AI_SEARCH_ADMIN_KEY,
                api_version=AI_SEARCH_SEARCH_API_VERSION,
            )
        if args.run:
            run_indexer(
                indexer_name=indexer_name,
                ai_search_endpoint=AI_SEARCH_ENDPOINT,
                api_key=AI_SEARCH_ADMIN_KEY,
                api_version=AI_SEARCH_SEARCH_API_VERSION,
            )
        if args.delete_index:
            delete_index()
        if args.delete_indexer:
            delete_indexer()
        if args.delete_skillset:
            delete_skillset()
        if args.delete_datasource:
            delete_datasource()
        if args.wipe_all:
            delete_indexer()
            delete_skillset()
            delete_datasource()
            delete_index()
        if not any(vars(args).values()):
            print("No action specified. Use --help for available options.")
    except Exception as e:
        print(f"An error occurred: {e}")
