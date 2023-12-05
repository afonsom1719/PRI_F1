import logging
from werkzeug.datastructures import FileStorage
from azure.storage.blob import BlobServiceClient
from utils.macros import CONNECTION_STRING, FILE_UPLOAD_CONTAINER

logger = logging.getLogger("globalLogger")


def get_blob_service_client(connection_string: str) -> BlobServiceClient:
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    return blob_service_client


def create_container(connection_string: str, container_name: str) -> BlobServiceClient:
    blob_service_client = get_blob_service_client(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()

    return container_client


def upload_files_to_blob_storage(
    file: FileStorage, container_name: str, connection_string: str
) -> str:
    """
    Upload a file to Azure Blob Storage container.

    Parameters:
        file (FileStorage): The file to be uploaded. It should be a file uploaded by the user using a form.

    Returns:
        str: The URL link to the uploaded file in the Azure Blob Storage container.

    Example:
        file = <FileStorage object>  # The uploaded file

        result = upload_files_to_blob_storage(file)
        print(result)
        # Output: "https://your-blob-storage-url.com/files/example.pdf"
    """
    # Create a blob client using the local file name as the name for the blob

    container_name = FILE_UPLOAD_CONTAINER
    connection_string = CONNECTION_STRING
    container_client = create_container(
        container_name=container_name, connection_string=connection_string
    )
    blob_client = container_client.get_blob_client(file.filename)

    with file.stream as stream:
        blob_client.upload_blob(stream, overwrite=True)

    return container_client.get_blob_client(file.filename).url


def delete_files_from_blob_storage() -> None:
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    blob_service_client.delete_container(FILE_UPLOAD_CONTAINER)
    create_container(
        CONNECTION_STRING,
        FILE_UPLOAD_CONTAINER,
    )
