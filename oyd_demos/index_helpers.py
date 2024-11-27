import logging
import os
import json
import requests
from dotenv import load_dotenv
import oyd_demos.utils as U
import time
import certifi

load_dotenv()
log = U.get_logger(__name__)

headers = {'Content-Type': 'application/json', 'api-key': os.environ['AZURE_SEARCH_KEY']}
params = {'api-version': os.environ['AZURE_SEARCH_API_VERSION']}


def create_object(object_name, object_type, payload, suppress_errors=False):
    """
    Create an object in Azure Search
    :param object_name: The name of the object to create
    :param object_type: The type of object to create
    :param payload: The payload to send to the API
    """
    assert (object_type in ['datasource', 'index', 'skillset', 'indexer'])
    log.info(f"Creating {object_type} {object_name}")
    plural = {'datasource': 'datasources', 'index': 'indexes', 'skillset': 'skillsets', 'indexer': 'indexers'}
    # Setup the Payloads header

    r = requests.put(os.environ['AZURE_SEARCH_ENDPOINT'] + f"/{plural[object_type]}/" + object_name,
                     data=json.dumps(payload), headers=headers, params=params, verify=certifi.where())
    logging.debug(r.text)
    if r.ok:
        log.info(f"{object_type} created successfully")
    else:
        log.error(f"Error creating {object_type}")
        log.error(r.text)
        if not suppress_errors: raise Exception(f"Error creating {object_type}")


def delete_object(object_name, object_type, suppress_errors=True):
    """
    Delete an object in Azure Search
    :param object_name: The name of the object to delete
    :param object_type: The type of object to delete, must be one of: datasource, index, skillset, indexer
    """
    assert (object_type in ['datasource', 'index', 'skillset', 'indexer'])
    log.info(f"Creating {object_type} {object_name}")
    plural = {'datasource': 'datasources', 'index': 'indexes', 'skillset': 'skillsets', 'indexer': 'indexers'}
    # Setup the Payloads header

    r = requests.delete(os.environ['AZURE_SEARCH_ENDPOINT'] + f"/{plural[object_type]}/" + object_name,
                        headers=headers, params=params, verify=certifi.where())
    logging.debug(r.text)
    if r.ok:
        log.info(f"{object_type} deleted successfully")
    else:
        log.error(f"Error deleted {object_type}")
        log.error(r.text)
        if not suppress_errors: raise Exception(f"Error creating {object_type}")


def create_all_objects(names, payloads):
    """
    Create all objects in Azure Search
    :param names: The names of the objects to create, in this order: datasource, index, skillset, indexer
    :param payloads: The payloads to send to the API, in this order: datasource, index, skillset, indexer
    """
    assert (len(names) == 4)
    log.info("Creating all objects")
    for i, typ in enumerate(['datasource', 'index', 'skillset', 'indexer']):
        create_object(names[i], typ, payloads[i])


def run_indexer(indexer_name):
    """
    Run the indexer in Azure Search
    """
    log.info("Running indexer")
    r = requests.post(os.environ['AZURE_SEARCH_ENDPOINT']
                      + f"/indexers/{indexer_name}/run",
                      headers=headers, params=params, verify=certifi.where())
    log.debug(r.text)
    if not r.ok or "error" in r:
        raise Exception(r.text)
    return r



def get_indexer_status(indexer_name):
    """
    Get the status of the indexer in Azure Search
    """
    log.info(f"Getting indexer status for: {indexer_name}")
    r = requests.get(os.environ['AZURE_SEARCH_ENDPOINT']
                     + f"/indexers/{indexer_name}/status",
                     headers=headers, params=params, verify=certifi.where())
    log.debug(r.text)
    if not r.ok or "error" in r:
        raise Exception(r.text)
    return r.json().get('lastResult')

# def wait_for_indexer(indexer_name, status='success'):
#     """
#     Wait for the indexer to reach a certain status
#     """
#     log.info(f"Waiting for indexer to reach status {status}")
#     while True:
#         r = get_indexer_status(indexer_name)
#         log.debug("indexer status: " + str(r))
#         if r['lastResult']['status'] == status:
#             break
#         time.sleep(5)
#     log.info(f"Indexer reached status {status}")


def delete_all_objects(names):
    """
    Delete all objects in Azure Search
    :param names: The names of the objects to delete, in this order: datasource, index, skillset, indexer
    """
    assert (len(names) == 4)
    log.info("Deleting all objects")
    for i, typ in enumerate(['datasource', 'index', 'skillset', 'indexer']):
        delete_object(names[i], typ)


def add_filter_to_extra_body(extra_body, fltr):
    eb = extra_body.copy()
    eb["data_sources"][0]["parameters"]["filter"] = fltr
    return eb

def put_document(index_name, payload):
    r = requests.post(os.environ['AZURE_SEARCH_ENDPOINT'] + f"/indexes/{index_name}/docs/index",
                      data=json.dumps(payload), headers=headers, params=params, verify=certifi.where())
    log.debug(r.text)
    if not r.ok:
        log.error(f"Error adding document to index")
        log.error(r.text)
        raise Exception(f"Error adding document to index")
    log.info(f"Document added to index")

def search(index_name, payload):
    r = requests.post(os.environ['AZURE_SEARCH_ENDPOINT'] + f"/indexes/{index_name}/docs/search",
                      data=json.dumps(payload), headers=headers, params=params, verify=certifi.where())
    search_results = r.json()
    log.debug(r.text)
    log.info("Results Found: {}, Results Returned: {}".format(search_results['@odata.count'], len(search_results['value'])))
    if not r.ok:
        log.error(f"Error searching index")
        log.error(r.text)
        raise Exception(f"Error searching index")
    log.info(f"Search successful")
    return r.json()