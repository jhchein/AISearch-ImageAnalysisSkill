import logging
import requests


logging.basicConfig(level=logging.INFO)


def create_resource(resource_url, headers, definition, resource_name):
    logging.info(f"Creating {resource_name}")
    response = requests.put(resource_url, headers=headers, json=definition)
    if response.status_code == 200:
        logging.info(f"{resource_name} created successfully")
    elif response.status_code == 201:
        logging.info(f"{resource_name} updated successfully")
    elif response.status_code in [202, 204]:
        # no change
        logging.info(f"{resource_name} already exists, no change")
    else:
        logging.error(
            f"{resource_name} creation failed with status code {response.status_code}"
        )
        logging.info(response.json())
    return response
