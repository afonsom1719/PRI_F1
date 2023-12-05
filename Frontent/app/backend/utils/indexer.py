import logging
from azure.identity import AzureDeveloperCliCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from utils.bloboperations import create_container
import time
# import subprocess
from utils.macros import (
    TENANT_ID,
    SEARCH_SERVICE,
    STORAGE_KEY,
    SEARCH_KEY,
    SEARCH_INDEXER,
    CONNECTION_STRING,
    FILE_UPLOAD_CONTAINER,
)

logger = logging.getLogger("globalLogger")


# Initialize Azure credentials
azd_credential = (
    AzureDeveloperCliCredential()
    if TENANT_ID is None
    else AzureDeveloperCliCredential(tenant_id=TENANT_ID)
)
default_creds = azd_credential if SEARCH_KEY is None or STORAGE_KEY is None else None
search_creds = default_creds if SEARCH_KEY is None else AzureKeyCredential(SEARCH_KEY)


# def run_indexer() -> bool:
#     logger.info("Running indexer")
#     logger.debug("Search credentials: %s", search_creds)
#     logger.debug("Tenant ID: %s", TENANT_ID)
#     logger.debug("Search service: %s", SEARCH_SERVICE)
#     logger.debug("Storage key: %s", STORAGE_KEY)
#     logger.debug("Search index: %s", SEARCH_INDEX)

#     search_client = SearchIndexerClient(
#         endpoint=f"https://{SEARCH_SERVICE}.search.windows.net/",
#         credential=search_creds,
#     )
#     search_client.run_indexer(name=SEARCH_INDEXER)
#     logger.info("Indexer started")
#     indexer_status = search_client.get_indexer_status(name=SEARCH_INDEXER)
#     # logger.info("Indexer status: %s", indexer_status)
#     # logger.debug("Indexer last run: %s", indexer_status.last_result)
#     # in_progress = "inProgress"
#     running = "running"
#     # success = "success"
#     # is_indexer_running = (indexer_status.status == in_progress) or (
#     #     indexer_status.status == running
#     # )
#     logger.info("Waiting for indexer to start...")

#     # Wait for the indexer to start
#     for i in range(0, 2):
#         logger.debug("Iteration: %s", i)
#         logger.debug("Indexer status: %s", indexer_status.status)
#         logger.debug("Item count: %s", indexer_status.last_result.item_count)
#         if indexer_status.status == running:
#             logger.info("Indexer started")
#             break
#         logger.info("Indexer might have not processed any files yet...")
#         time.sleep(2)
#         indexer_status = search_client.get_indexer_status(name=SEARCH_INDEXER)

#     # Wait to make sure the indexer has processed at least one file
#     logger.info("Waiting for indexer to process at least one file...")
#     time.sleep(1)
#     # Check if it is not the case where it ends in less than 1 second and processes no files
#     indexer_status = search_client.get_indexer_status(name=SEARCH_INDEXER)
#     logger.debug("Indexer status after 1 sec: %s", indexer_status.status)

#     # If the indexer has not processed any files, we can skip setting metadata
#     logger.debug("Item count: %s", indexer_status.last_result.item_count)
#     logger.debug("Indexer status: %s", indexer_status)
#     if indexer_status.last_result.item_count == 0 and not indexer_status.status == running:
#         logger.info("No files were processed")
#         return False
#     logger.info("Indexer started so we can set metadata")
#     return True


def set_file_metadata(file_name: str, metadata: dict) -> None:
    container_client = create_container(
        connection_string=CONNECTION_STRING,
        container_name=FILE_UPLOAD_CONTAINER,
    )
    blob_client = container_client.get_blob_client(file_name)
    blob_client.set_blob_metadata(metadata)


def wait_and_set_metadata(file_name: str) -> None:
    # This function waits for the indexer to stop running and sets the metadata of the file
    search_client = SearchIndexerClient(
        endpoint=f"https://{SEARCH_SERVICE}.search.windows.net/",
        credential=search_creds,
    )
    indexer_status = search_client.get_indexer_status(name=SEARCH_INDEXER)
    running = "running"
    logger.info("Waiting for indexer to stop...")
    # Wait for the indexer to stop running
    while indexer_status.status == running:
        time.sleep(2)
        indexer_status = search_client.get_indexer_status(name=SEARCH_INDEXER)
    logger.info("Indexer stopped")
    # Set the metadata of the file
    metadata = {
        "AzureSearch_Skip": "true",
    }
    set_file_metadata(file_name, metadata)
    logger.info("Metadata set")


def start_indexer_and_return(file_name: str) -> bool:
    # This function starts the indexer and returns immediately
    search_client = SearchIndexerClient(
        endpoint=f"https://{SEARCH_SERVICE}.search.windows.net/",
        credential=search_creds,
    )
    search_client.run_indexer(name=SEARCH_INDEXER)
    logger.info("Indexer started")
    # # Create and start a subprocess that runs the wait_and_set_metadata.py script
    # # Pass the file name and metadata as arguments to the script
    # p = subprocess.Popen(
    #     ["python", "wait_and_set_metadata.py", file_name],
    #     stdin=subprocess.PIPE,
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE,
    # )
    # # Check if the subprocess is still running
    # logger.info("Subprocess started")
    # while p.poll() is None:
    #     print("The subprocess is still running")
    # Return from the main function
    return True
