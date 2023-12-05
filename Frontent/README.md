# ChatGPT data with Azure OpenAI and Cognitive Search

[![Open in GitHub Codespaces](https://img.shields.io/static/v1?style=for-the-badge&label=GitHub+Codespaces&message=Open&color=brightgreen&logo=github)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=599293758&machine=standardLinux32gb&devcontainer_path=.devcontainer%2Fdevcontainer.json&location=WestUs2)
[![Open in Remote - Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Remote%20-%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/azure-samples/azure-search-openai-demo)

This sample demonstrates a few approaches for creating ChatGPT-like experiences over your own data using the Retrieval Augmented Generation pattern. It uses Azure OpenAI Service to access the ChatGPT model (gpt-35-turbo), and Azure Cognitive Search for data indexing and retrieval.

The repo includes sample data so it's ready to try end to end. In this sample application we use a fictitious company called Contoso Electronics, and the experience allows its employees to ask questions about the benefits, internal policies, as well as job descriptions and roles.

This app provides a user-friendly platform for interacting with a state-of-the-art AI model. Users can seamlessly chat, ask questions, and evaluate responses for trustworthiness. The app orchestrates data preparation, prompt construction, and AI-retriever interactions. Users can upload documents to expand the AI's knowledge and utilize the speech-to-text feature.

![Chat screen](docs/chatexample.png)

## Features

* **Chat and Q&A Interfaces:**
Access information through intuitive chat and question-and-answer interfaces.

* **Trustworthiness Evaluation:**
Evaluate responses with citations, source tracking, and more to ensure reliability.

* **Data Preparation and Orchestration:**
Effortlessly manage data, construct prompts, and coordinate model-retriever interactions for accurate responses.

* **Image Creation Using Dall-E**:
Prompt the model to create an image according to a provided description.

* **Knowledge Expansion:**
Upload new documents to enhance the AI model's knowledge base over time.

* **Speech-to-Text Integration:**
Interact using spoken language through the speech-to-text option.

![Dall-E Example](docs/Dall-E.png)

## Flow Explanation

The flow starts with the user sending a message to our service and if the message is an uploaded file, then the frontend sends a POST request to the /fileupload endpoint, represented in blue in the flowchart. In that case the file is uploaded to a blob storage container to allow further functions to read the file, either to index it or display to the user in the chat. Then the indexer runs and detects recent changes to the blob storage container set as the indexer data source. If new files were added then it will re-index every file that does not contain the following metadata: `"AzureSearch_Skip": "true"`. However, indexers might have skills gathered in a skillset that run before the indexing occurs. In this situation we have only one skill that handles the extraction of data from the invoices uploaded by the user, represented by the "Run Extraction Service" node in the flowchart. Subsequently, the extracted data is mapped to the according fields and stored in the index defined in the indexer. While still following the blue path in the flow, we then take the data retrieved from the document and send it the chat completion model from AzureOpenAI in order to compose a more sensible answer to send to the user.
On the other hand, if the green path of the flow is pursued, then the first step is to use the _gpt-35-turbo-0613_ model to check if any function call should be made in order to provide more accurate results to the user. If, for example, the user's message presents an intent to create an image using _Dall-E_ then the function call will be made to the _Dall-E_ model and the image will be returned to the user. If not but there is still an intention to run an available function, then that function is run and the result is returned to the user. In case, none of those are true, then the message is sent to the completion model to query the index and return the most relevant results to the user. The results are then sent to the frontend to be displayed to the user. Although, if none of the previous possibilies are met, then the model tries to answer the question based on the chat history, otherwise it will warn the user that it does not have enough information to answer the question.

![RAG Architecture](docs/flowchart.drawio.png)

## Getting Started

> **IMPORTANT:** In order to deploy and run this example, you'll need an **Azure subscription with access enabled for the Azure OpenAI service**. You can request access [here](https://aka.ms/oaiapply). You can also visit [here](https://azure.microsoft.com/free/cognitive-search/) to get some free Azure credits to get you started.

> **AZURE RESOURCE COSTS** by default this sample will create Azure App Service and Azure Cognitive Search resources that have a monthly cost, as well as Form Recognizer resource that has cost per document page. You can switch them to free versions of each of them if you want to avoid this cost by changing the parameters file under the infra folder (though there are some limits to consider; for example, you can have up to 1 free Cognitive Search resource per subscription, and the free Form Recognizer resource only analyzes the first 2 pages of each document.)

### Prerequisites

#### To Run Locally

* [Azure Developer CLI](https://aka.ms/azure-dev/install)

* [Python 3+](https://www.python.org/downloads/)
  * **Important**: Python and the pip package manager must be in the path in Windows for the setup scripts to work.
  * **Important**: Ensure you can run `python --version` from console. On Ubuntu, you might need to run `sudo apt install python-is-python3` to link `python` to `python3`.
* [Node.js](https://nodejs.org/en/download/)
* [Git](https://git-scm.com/downloads)
* [Powershell 7+ (pwsh)](https://github.com/powershell/powershell) - For Windows users only.
  * **Important**: Ensure you can run `pwsh.exe` from a PowerShell command. If this fails, you likely need to upgrade PowerShell.

>NOTE: Your Azure Account must have `Microsoft.Authorization/roleAssignments/write` permissions, such as [User Access Administrator](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#user-access-administrator) or [Owner](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#owner).  

#### To Run in GitHub Codespaces or VS Code Remote Containers

You can run this repo virtually by using GitHub Codespaces or VS Code Remote Containers.  Click on one of the buttons below to open this repo in one of those options.

[![Open in GitHub Codespaces](https://img.shields.io/static/v1?style=for-the-badge&label=GitHub+Codespaces&message=Open&color=brightgreen&logo=github)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=599293758&machine=standardLinux32gb&devcontainer_path=.devcontainer%2Fdevcontainer.json&location=WestUs2)
[![Open in Remote - Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Remote%20-%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/azure-samples/azure-search-openai-demo)

### Installation

#### Project Initialization

1. Create a new folder and switch to it in the terminal
1. Run `azd auth login`
1. Run `azd init -t azure-search-openai-demo`
    * note that this command will initialize a git repository and you do not need to clone this repository

#### Starting from scratch

Execute the following command, if you don't have any pre-existing Azure services and want to start from a fresh deployment.

1. Run `azd up` - This will provision Azure resources and deploy this sample to those resources, including building the search index based on the files found in the `./data` folder.
    * For the target location, the regions that currently support the models used in this sample are **East US** or **South Central US**. For an up-to-date list of regions and models, check [here](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/concepts/models)
1. After the application has been successfully deployed you will see a URL printed to the console.  Click that URL to interact with the application in your browser.  

It will look like the following:

!['Output from running azd up'](assets/endpoint.png)

> NOTE: It may take a minute for the application to be fully deployed. If you see a "Python Developer" welcome screen, then wait a minute and refresh the page.

#### Use existing resources

1. Run `azd env set AZURE_OPENAI_SERVICE {Name of existing OpenAI service}`
1. Run `azd env set AZURE_OPENAI_RESOURCE_GROUP {Name of existing resource group that OpenAI service is provisioned to}`
1. Run `azd env set AZURE_OPENAI_CHATGPT_DEPLOYMENT {Name of existing ChatGPT deployment}`. Only needed if your ChatGPT deployment is not the default 'chat'.
1. Run `azd env set AZURE_OPENAI_GPT_DEPLOYMENT {Name of existing GPT deployment}`. Only needed if your ChatGPT deployment is not the default 'davinci'.
1. Run `azd up`

> NOTE: You can also use existing Search and Storage Accounts.  See `./infra/main.parameters.json` for list of environment variables to pass to `azd env set` to configure those existing resources.

#### Deploying or re-deploying a local clone of the repo

* Simply run `azd up`

#### Running locally

1. Run `azd login`
2. Change dir to `app`
3. Run `./start.ps1` or `./start.sh` or run the "VS Code Task: Start App" to start the project locally.

> **IMPORTANT:** In the current version, the build of the frontend is turned off inside start.ps1 to avoid restarting the frontend everytime there's a change in the backend. Therefore, you also need to `cd frontend` and then `npm run watch`. (For quality of life reasons you might want to do this step in a different terminal.)

#### Sharing Environments

Run the following if you want to give someone else access to completely deployed and existing environment.

1. Install the [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
1. Run `azd init -t azure-search-openai-demo`
1. Run `azd env refresh -e {environment name}` - Note that they will need the azd environment name, subscription Id, and location to run this command - you can find those values in your `./azure/{env name}/.env` file.  This will populate their azd environment's .env file with all the settings needed to run the app locally.
1. Run `pwsh ./scripts/roles.ps1` - This will assign all of the necessary roles to the user so they can run the app locally.  If they do not have the necessary permission to create roles in the subscription, then you may need to run this script for them. Just be sure to set the `AZURE_PRINCIPAL_ID` environment variable in the azd .env file or in the active shell to their Azure Id, which they can get with `az account show`.

### Quickstart

* In Azure: navigate to the Azure WebApp deployed by azd. The URL is printed out when azd completes (as "Endpoint"), or you can find it in the Azure portal.
* Running locally: navigate to 127.0.0.1:5000

Once in the web app:

* Try different topics in chat or Q&A context. For chat, try follow up questions, clarifications, ask to simplify or elaborate on answer, etc.
* Explore citations and sources
* Click on "settings" to try different options, tweak prompts, etc.

## Resources

* [Revolutionize your Enterprise Data with ChatGPT: Next-gen Apps w/ Azure OpenAI and Cognitive Search](https://aka.ms/entgptsearchblog)
* [Azure Cognitive Search](https://learn.microsoft.com/azure/search/search-what-is-azure-search)
* [Azure OpenAI Service](https://learn.microsoft.com/azure/cognitive-services/openai/overview)

### Note
>
>Note: The PDF documents used in this demo contain information generated using a language model (Azure OpenAI Service). The information contained in these documents is only for demonstration purposes and does not reflect the opinions or beliefs of Microsoft. Microsoft makes no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability or availability with respect to the information contained in this document. All rights reserved to Microsoft.

### FAQ

***Question 1***: Why do we need to break up the PDFs into chunks when Azure Cognitive Search supports searching large documents?

***Answer***: Chunking allows us to limit the amount of information we send to OpenAI due to token limits. By breaking up the content, it allows us to easily find potential chunks of text that we can inject into OpenAI. The method of chunking we use leverages a sliding window of text such that sentences that end one chunk will start the next. This allows us to reduce the chance of losing the context of the text.

***Question 2***: How does the file upload process work in the application?

***Answer***:  When a user uploads a file through the frontend, the file is sent as a POST request to the /fileupload endpoint. The uploaded file is stored in a blob storage container. The indexer detects changes in this container and re-indexes files without the metadata "AzureSearch_Skip": "true". Extraction skills from a skillset might be applied before indexing.

***Question 2***: What is the purpose of the "Run Extraction Service" node in the flowchart?

***Answer***:  The "Run Extraction Service" node represents a skill that extracts data from user-uploaded invoices. This data is then mapped to appropriate fields and stored in the index defined in the indexer.

***Question 3***: How are responses composed for user queries after data extraction?

***Answer***:  Extracted data is sent to the chat completion model (AzureOpenAI) to create meaningful answers. The composed answers are returned to the user through the frontend.

***Question 4***: How are function calls and intents handled in the application?

***Answer***:  The _gpt-3.5-turbo-0613_ model is used to identify function call intentions. If a user intends to perform an action, like creating an image using DALL-E, the corresponding function is called and the result is returned. If no such intent exists, the model queries the index for relevant results.

***Question 5***: How does the application respond to queries without specific intents?

***Answer***:  If a user query lacks specific intent, the model attempts to answer based on indexed data or chat history. If it can't find relevant information, it informs the user of its limitations.

***Question 6***: How can the model access the indexed and extracted data in the application?

***Answer***:  The indexed and extracted data is stored in the index, which it can query to retrieve relevant information.

***Question 7***: What happens if a file contains the "AzureSearch_Skip": "true" metadata?

***Answer***:  Files with this metadata will not be re-indexed by the indexer. This can be useful to exclude certain files from the re-indexing process.

### Troubleshooting

If you see this error while running `azd deploy`: `read /tmp/azd1992237260/backend_env/lib64: is a directory`, then delete the `./app/backend/backend_env folder` and re-run the `azd deploy` command.  This issue is being tracked here: <https://github.com/Azure/azure-dev/issues/1237>

If the web app fails to deploy and you receive a '404 Not Found' message in your browser, run 'azd deploy'.
