# test_fileupload.py

import os
import pytest
from werkzeug.datastructures import FileStorage
from utils.bloboperations import (
    get_blob_service_client,
    create_container,
    upload_files_to_blob_storage,
)
from utils.macros import FILE_UPLOAD_CONTAINER, CONNECTION_STRING


@pytest.fixture(scope="module")
def blob_service_client():
    # Create a blob service client for the test module
    return get_blob_service_client(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))


@pytest.fixture(scope="module")
def container_client(blob_service_client):
    # Create a container client for the test module
    return create_container(
        os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
        os.getenv("AZURE_FILE_UPLOAD_CONTAINER"),
    )


@pytest.fixture(scope="function")
def file():
    # Create a mock file object for the test function
    return FileStorage(
        stream=open("tests/test_files/InvoiceAEStyle.png", "rb"),
        filename="InvoiceAEStyle.png",
        content_type="image/png",
    )


def test_upload_files_to_blob_storage(file, container_client):
    # Test the upload_files_to_blob_storage function
    url = upload_files_to_blob_storage(file, CONNECTION_STRING, FILE_UPLOAD_CONTAINER)
    assert url.startswith("https://")
    assert url.endswith(file.filename)
    assert container_client.get_blob_client(file.filename).exists()


# def test_delete_files_from_blob_storage(blob_service_client, container_client):
#     # Test the delete_files_from_blob_storage function
#     delete_files_from_blob_storage()
#     assert not container_client.exists()
#     assert blob_service_client.get_container_client(FILE_UPLOAD_CONTAINER).exists()
