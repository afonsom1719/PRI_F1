from typing import Any
from werkzeug.datastructures import FileStorage
from utils.bloboperations import upload_files_to_blob_storage
from utils.formrecognizer import extract_data_from_form_recognizer
from utils.indexer import start_indexer_and_return
import logging
from utils.macros import SAS_TOKEN, CONNECTION_STRING, FILE_UPLOAD_CONTAINER

# Set up logging
logger = logging.getLogger("globalLogger")


def run(file: FileStorage) -> Any:
    """
    Process the provided file using Form Recognizer to extract data points.

    Parameters:
        file (FileStorage): The file to be processed. It should be a file uploaded by the user using a form.

    Returns:
        dict[str, Any]: A dictionary containing the extracted data points and other relevant information.
            - 'data_points': The name of the uploaded file.
            - 'answer': The results obtained by extracting data from the uploaded file using Form Recognizer.
            - 'thoughts': A formatted string summarizing the actions performed by the function:
                "Searched for:<br>[file name]<br>Found:<br>[results]<br>"
                where [file name] is the name of the uploaded file and [results] are the extracted data points.

    Example:
        file = <FileStorage object>  # The uploaded file

        result = run(file)
        print(result)
        # Output:
        # {
        #     "data_points": link_to_file,
        #     "answer": {
        #         "field1": "value1",
        #         "field2": "value2",
        #         ...
        #     },
        #     "thoughts": "Searched for:<br>example.pdf<br>Found:<br>{'field1': 'value1', 'field2': 'value2', ...}<br>"
        # }
    """
    logger.debug(f"Running {__file__} approach")

    # Upload the file to the blob storage
    # delete_files_from_blob_storage()
    blob_link = upload_files_to_blob_storage(
        file,
        container_name=FILE_UPLOAD_CONTAINER,
        connection_string=CONNECTION_STRING,
    )
    # Send the link to form recognizer to extract the data

    start_indexer_and_return(file.filename)
    logger.info("Indexer exit")
    # The flag AzureSearch_Skip is used to skip the file from being indexed again
    # And is used instead of deleting the file from the blob storage because we need it to display the file in the chat

    results = extract_data_from_form_recognizer(blob_link)
    # Delete the file from the blob storage

    # save_documents_uploaded(file.name, results)

    return {
        "data_points": f"{blob_link}{SAS_TOKEN}",
        "answer": results,
        "thoughts": f"Searched for:<br>{file.name}<br>Found:<br>{results}<br>",
    }
