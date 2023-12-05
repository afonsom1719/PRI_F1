import io
import mimetypes
import time
import logging
from openai import OpenAI
from datetime import datetime
from utils.macros import (
    API_KEY,
    API_TYPE,
    API_VERSION,
    AZURE_OPENAI_SERVICE,
    AZURE_OPENAI_GPT_DEPLOYMENT,
    AZURE_OPENAI_GPT_FUNCTIONS_DEPLOYMENT,
    AZURE_OPENAI_CHATGPT_DEPLOYMENT,
    AZURE_SEARCH_SERVICE,
    AZURE_SEARCH_INDEX,
    AZURE_STORAGE_ACCOUNT,
    AZURE_STORAGE_CONTAINER,
    KB_FIELDS_CONTENT,
    KB_FIELDS_SOURCEPAGE,
    AZURE_INDEXER_CONTAINER
)

# import requests
from flask import Flask, request, jsonify, send_file, abort
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from approaches.retrievethenread import RetrieveThenReadApproach
from approaches.readretrieveread import ReadRetrieveReadApproach
from approaches.readdecomposeask import ReadDecomposeAsk
from approaches.chatreadretrieveread import ChatReadRetrieveReadApproach
import approaches.fileupload as FileUpload
from azure.storage.blob import BlobServiceClient


# Configure basic logging
logging.basicConfig(
    filename=f"logs/chat_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - line %(lineno)d - %(message)s",
)

# Create a logger
logger = logging.getLogger("globalLogger")

# Set the log level to DEBUG
logger.setLevel(logging.DEBUG)


# Use the current user identity to authenticate with Azure OpenAI, Cognitive Search and Blob Storage (no secrets needed,
# just use 'az login' locally, and managed identity when deployed on Azure). If you need to use keys, use separate AzureKeyCredential instances with the
# keys for each service
# If you encounter a blocking error during a DefaultAzureCredntial resolution, you can exclude the problematic credential by using a parameter (ex. exclude_shared_token_cache_credential=True)
# azure_credential = DefaultAzureCredential()


# # Used by the OpenAI SDK
# openai.api_type = API_TYPE
# openai.api_base = f"https://{AZURE_OPENAI_SERVICE}.openai.azure.com"
# openai.api_version = API_VERSION

# # Comment these two lines out if using keys, set your API key in the OPENAI_API_KEY environment variable instead
# # openai_token = azure_credential.get_token(
# #     "https://cognitiveservices.azure.com/.default"
# # )
# # openai.api_key = openai_token.token

# openai.api_key = API_KEY

# # Set up clients for Cognitive Search and Storage
# search_client = SearchClient(
#     endpoint=f"https://{AZURE_SEARCH_SERVICE}.search.windows.net",
#     index_name=AZURE_SEARCH_INDEX,
#     credential=azure_credential,
# )
# blob_client = BlobServiceClient(
#     account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
#     credential=azure_credential,
# )
# blob_container = blob_client.get_container_client(AZURE_STORAGE_CONTAINER)


# Various approaches to integrate GPT and external knowledge, most applications will use a single one of these patterns
# or some derivative, here we include several for exploration purposes
# ask_approaches = {
#     "rtr": RetrieveThenReadApproach(
#         search_client,
#         AZURE_OPENAI_GPT_DEPLOYMENT,
#         KB_FIELDS_SOURCEPAGE,
#         KB_FIELDS_CONTENT,
#     ),
#     "rrr": ReadRetrieveReadApproach(
#         search_client,
#         AZURE_OPENAI_GPT_DEPLOYMENT,
#         KB_FIELDS_SOURCEPAGE,
#         KB_FIELDS_CONTENT,
#     ),
#     "rda": ReadDecomposeAsk(
#         search_client,
#         AZURE_OPENAI_GPT_DEPLOYMENT,
#         KB_FIELDS_SOURCEPAGE,
#         KB_FIELDS_CONTENT,
#     ),
# }

chat_approaches = {
    "rrr": ChatReadRetrieveReadApproach(
        AZURE_OPENAI_CHATGPT_DEPLOYMENT,
        AZURE_OPENAI_GPT_DEPLOYMENT,
        AZURE_OPENAI_GPT_FUNCTIONS_DEPLOYMENT,
        KB_FIELDS_SOURCEPAGE,
        KB_FIELDS_CONTENT,
    )
}


app = Flask(__name__)


@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def static_file(path):
    return app.send_static_file(path)


# Serve content files from blob storage from within the app to keep the example self-contained.
# *** NOTE *** this assumes that the content files are public, or at least that all users of the app
# can access all the files. This is also slow and memory hungry.
@app.route("/content/<path>")
def content_file(path):
    if "pdf" in path.lower():
        blob = blob_container.get_blob_client(path).download_blob()
    else:
        blob_indexer_container = blob_client.get_container_client(AZURE_INDEXER_CONTAINER)
        blob = blob_indexer_container.get_blob_client(path).download_blob()
    if not blob.properties or not blob.properties.has_key("content_settings"):
        abort(404)
    mime_type = blob.properties["content_settings"]["content_type"]
    if mime_type == "application/octet-stream":
        mime_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
    blob_file = io.BytesIO()
    blob.readinto(blob_file)
    blob_file.seek(0)
    return send_file(
        blob_file, mimetype=mime_type, as_attachment=False, download_name=path
    )


@app.route("/ask", methods=["POST"])
def ask():
    # ensure_openai_token()
    if not request.json:
        return jsonify({"error": "request must be json"}), 400
    approach = request.json["approach"]
    try:
        impl = ask_approaches.get(approach)
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["question"], request.json.get("overrides") or {})
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /ask")
        return jsonify({"error": str(e)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    # ensure_openai_token()
    logger.debug("Running chat endpoint")

    print("Entered chat")
    if (
        not request.is_json
    ):  # it was request.json but that calls the get_json() method which is not what we want
        return jsonify({"error": "request must be json"}), 400
    approach = request.json["approach"]
    try:
        impl = chat_approaches.get(approach)
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["history"], request.json.get("overrides") or {}, request.json.get("language") or "English")
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /chat")
        return jsonify({"error": str(e)}), 500


@app.route("/file/upload", methods=["POST"])
def fileUpload():
    """
    Handle the file upload request and process the uploaded file using the specified approach.

    This endpoint expects a file to be uploaded along with additional data in the form of a JSON payload.
    The JSON payload should include the chat history, overrides (if applicable), and the chosen approach.

    Returns:
        dict: A dictionary containing the result of the processing. The specific keys and structure of the dictionary
            depend on the chosen approach and the processing results.

    Example JSON Payload (request.form["request"]):
        {
            "history": [
                {"user": "Hello!", "response": "Hi there! How can I assist you today?"},
                {"user": "I want to extract data from this file.", "response": "Sure! Please upload the file."},
                ...
            ],
            "overrides": {
                "some_parameter": "value",
                "another_parameter": 42
            },
            "approach": "some_approach"
        }

    Example Response:
        {
            "data_points": ["example.pdf"],
            "thoughts": "Searched for:<br>example.pdf<br>Found:<br>{'field1': 'value1', 'field2': 'value2', ...}<br>",
            "some_key": "some_value",
            ...
        }
    """
    print("Entered fileUpload endpoint")
    logger.debug("Running fileUpload endpoint")
    # ensure_openai_token()
    files = request.files.to_dict()
    file = files["file"]

    if files == {}:
        return jsonify({"error": "request must be file"}), 400
    try:
        messages = []
        data = FileUpload.run(file)

        file_upload_prompt = """You are a chat bot that reads a JSON file with data about an invoice and returns the information in a conversational format.
            The JSON properties can vary and you must fit the answer according to the properties name and data.
            Use simple language.Do not greet the user. If it is empty, tell the user you could not find the data."""
        data_prompt = f"{data.get('answer')}"
        messages.append({"role": "system", "content": f"{file_upload_prompt}"})
        messages.append({"role": "user", "content": f"{data_prompt}"})

        file_upload_completion = openai.ChatCompletion.create(
            deployment_id=AZURE_OPENAI_CHATGPT_DEPLOYMENT,
            messages=messages,
            temperature=0.5,
            max_tokens=200,
            n=1,
            stop=["\n"],
        )

        file_upload_completion_response = file_upload_completion.choices[
            0
        ].message.content
        response = {}
        response["answer"] = file_upload_completion_response
        response["data_points"] = [data.get("data_points")]
        response["thoughts"] = data.get("thoughts")
        logger.debug(f"Data: {data}")
        return jsonify(response)

    except Exception as e:
        logging.exception("Exception in /fileUpload")
        return jsonify({"error": str(e)}), 500


def ensure_openai_token():
    global openai_token
    if openai_token.expires_on < int(time.time()) - 60:
        openai_token = azure_credential.get_token(
            "https://cognitiveservices.azure.com/.default"
        )
        openai.api_key = openai_token.token


if __name__ == "__main__":
    app.run(use_reloader=True, debug=True)
