# PyData Ljubljana November 2024 Meetup

This repository contains the code used for demos at the PyData Ljubljana November 2024 Meetup.

## Code

- `notebooks/001_gradio_quick_demo.ipynb`: Gradio quick demo
- `oyd_demos/data_generator.py`: Simple data generator for clinical records in Slovenian, demonstrating Gradio Chat interface and usage of the SDK
- `oyd_demos/oyd_chat.py`: Simple chatbot that incorporates knowledge of Slovenian Legislation
- `oyd_demos/index_helpers.py`: Index helpers
- `oyd_demos/zakon_index.py`: Index configuration and "On Your Data" configuration (extra_body)

## Setting up the environment

1. Create Azure OpenAI and Azure Search services
1. Setup Python interpreter and install the requirements
    ```
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    ```
1. Create the .env file with the following content:

```
LOG_LEVEL="DEBUG"
ENVIRONMENT="dev"
# Don't mess with this unless you really know what you are doing
AZURE_SEARCH_API_VERSION="2024-05-01-preview"
AZURE_OPENAI_API_VERSION="2024-10-01-preview"

# Demo Data (edit with your own if you want to use your own data)

BLOB_CONNECTION_STRING="BlobEndpoint=https://REMOVED.blob.core.windows.net/;QueueEndpoint=https://REMOVED.queue.core.windows.net/;FileEndpoint=https://REMOVED.file.core.windows.net/;TableEndpoint=https://REMOVED.table.core.windows.net/;SharedAccessSignature=REMOVED"
BLOB_SAS_TOKEN="REMOVED"

# Edit with your own azure services values

AZURE_SEARCH_ENDPOINT="REMOVED"
AZURE_SEARCH_KEY="REMOVED"


AZURE_OPENAI_ENDPOINT="https://REMOVED.openai.azure.com/"
AZURE_OPENAI_API_KEY="REMOVED"
GPT4_DEPLOYMENT_NAME="gpt-4o"
#GPT35_DEPLOYMENT_NAME="ENTER YOUR VALUE"
EMBEDDING_DEPLOYMENT_NAME="text-embedding-3-large"
EMBEDDING_DIMENSIONS="3072"

```