import sys
from azure.search.documents.indexes import SearchIndexerClient
from azure.core.credentials import AzureKeyCredential
from bloboperations import create_container
import time
from macros import (
    CONNECTION_STRING,
    FILE_UPLOAD_CONTAINER,
    SEARCH_KEY,
    SEARCH_SERVICE,
    SEARCH_INDEXER,
)
import logging

logger = logging.getLogger("globalLogger")


# Get the file name and metadata from the arguments
file_name = sys.argv[1]


# Create the search client
search_creds = AzureKeyCredential(SEARCH_KEY)
search_client = SearchIndexerClient(
    endpoint=f"https://{SEARCH_SERVICE}.search.windows.net/",
    credential=search_creds,
)


# Define the function that sets the metadata of the file
def set_file_metadata(file_name: str, metadata: dict) -> None:
    container_client = create_container(
        connection_string=CONNECTION_STRING,
        container_name=FILE_UPLOAD_CONTAINER,
    )
    blob_client = container_client.get_blob_client(file_name)
    blob_client.set_blob_metadata(metadata)


# Get the indexer status
indexer_status = search_client.get_indexer_status(name=SEARCH_INDEXER)
running = "running"
print("Waiting for indexer to stop...")
# Wait for the indexer to stop running
while indexer_status.status == running:
    logger.debug("Indexer status: %s", indexer_status.status)
    time.sleep(2)
    indexer_status = search_client.get_indexer_status(name=SEARCH_INDEXER)
print("Indexer stopped")
# Set the metadata of the file
metadata = {
    "AzureSearch_Skip": "true",
}
set_file_metadata(file_name, metadata)
print("Metadata set")
