import os
from dotenv import load_dotenv
import oyd_demos.utils as U
import oyd_demos.index_helpers as IH

load_dotenv()
log = U.get_logger(__name__)

# Name of the container in your Blob Storage Datasource ( in credentials.env)
BLOB_CONTAINER_NAME = "zakonodaja"

DATASOURCE_NAME = "zakon-files" + "-" + os.environ['ENVIRONMENT']
INDEX_NAME = "zakon-index" + "-" + os.environ['ENVIRONMENT']
SKILLSET_NAME = "zakon-skillset" + "-" + os.environ['ENVIRONMENT']
INDEXER_NAME = "zakon-indexer" + "-" + os.environ['ENVIRONMENT']

datasource_payload = {
    "name": DATASOURCE_NAME,
    "description": "Demo files to demonstrate cognitive search capabilities.",
    "type": "azureblob",
    "credentials": {
        "connectionString": os.environ['BLOB_CONNECTION_STRING']
    },
    "dataDeletionDetectionPolicy" : {
        "@odata.type" :"#Microsoft.Azure.Search.NativeBlobSoftDeleteDeletionDetectionPolicy" # this makes sure that if the item is deleted from the source, it will be deleted from the index
    },
    "container": {
        "name": BLOB_CONTAINER_NAME
    }
}

index_payload = {
    "name": INDEX_NAME,
    "vectorSearch": {
        "algorithms": [
            {
                "name": "myalgo",
                "kind": "hnsw"
            }
        ],
        "vectorizers": [
            {
                "name": "openai",
                "kind": "azureOpenAI",
                "azureOpenAIParameters":
                    {
                        "resourceUri": os.environ['AZURE_OPENAI_ENDPOINT'],
                        "apiKey": os.environ['AZURE_OPENAI_API_KEY'],
                        "deploymentId": os.environ['EMBEDDING_DEPLOYMENT_NAME'],
                        "modelName": os.environ['EMBEDDING_DEPLOYMENT_NAME'],

                    }
            }
        ],
        "profiles": [
            {
                "name": "myprofile",
                "algorithm": "myalgo",
                "vectorizer": "openai"
            }
        ]
    },
    "semantic": {
        "configurations": [
            {
                "name": "my-semantic-config",
                "prioritizedFields": {
                    "titleField": {
                        "fieldName": "title"
                    },
                    "prioritizedContentFields": [
                        {
                            "fieldName": "chunk"
                        }
                    ],
                    "prioritizedKeywordsFields": []
                }
            }
        ]
    },
    "fields": [
        {"name": "id", "type": "Edm.String", "key": "true", "analyzer": "keyword", "searchable": "true",
         "retrievable": "true", "sortable": "false", "filterable": "false", "facetable": "false"},
        {"name": "ParentKey", "type": "Edm.String", "searchable": "true", "retrievable": "true",
         "facetable": "false", "filterable": "true", "sortable": "false"},
        {"name": "title", "type": "Edm.String", "searchable": "true", "retrievable": "true", "facetable": "false",
         "filterable": "true", "sortable": "false"},
        {"name": "name", "type": "Edm.String", "searchable": "true", "retrievable": "true", "sortable": "false",
         "filterable": "false", "facetable": "false"},
        {"name": "location", "type": "Edm.String", "searchable": "true", "retrievable": "true", "sortable": "false",
         "filterable": "false", "facetable": "false"},
        {"name": "chunk", "type": "Edm.String", "searchable": "true", "retrievable": "true", "sortable": "false",
         "filterable": "false", "facetable": "false"},

        {
            "name": "chunkVector",
            "type": "Collection(Edm.Single)",
            "dimensions": int(os.environ['EMBEDDING_DIMENSIONS']),  # IMPORTANT: Make sure these dimmensions match your embedding model name
            "vectorSearchProfile": "myprofile",
            "searchable": "true",
            "retrievable": "true",
            "filterable": "false",
            "sortable": "false",
            "facetable": "false"
        }
    ]
}



skillset_payload = {
    "name": SKILLSET_NAME,
    "description": "e2e Skillset for RAG - Files",
    "skills":
        [
            {
                "@odata.type": "#Microsoft.Skills.Text.SplitSkill",
                "context": "/document",
                "textSplitMode": "pages",  # although it says "pages" it actally means chunks, not actual pages
                "maximumPageLength": 5000,  # 5000 characters is default and a good choice
                "pageOverlapLength": 750,  # 15% overlap among chunks
                "defaultLanguageCode": "en",
                "inputs": [
                    {
                        "name": "text",
                        "source": "/document/content"
                    }
                ],
                "outputs": [
                    {
                        "name": "textItems",
                        "targetName": "chunks"
                    }
                ]
            },
            {
                "@odata.type": "#Microsoft.Skills.Text.AzureOpenAIEmbeddingSkill",
                "description": "Azure OpenAI Embedding Skill",
                "context": "/document/chunks/*",
                "resourceUri": os.environ['AZURE_OPENAI_ENDPOINT'],
                "apiKey": os.environ['AZURE_OPENAI_API_KEY'],
                "deploymentId": os.environ['EMBEDDING_DEPLOYMENT_NAME'],
                "modelName": os.environ['EMBEDDING_DEPLOYMENT_NAME'],
                "inputs": [
                    {
                        "name": "text",
                        "source": "/document/chunks/*"
                    }
                ],
                "outputs": [
                    {
                        "name": "embedding",
                        "targetName": "vector"
                    }
                ]
            }
        ],
    "indexProjections": {
        "selectors": [
            {
                "targetIndexName": INDEX_NAME,
                "parentKeyFieldName": "ParentKey",
                "sourceContext": "/document/chunks/*",
                "mappings": [
                    {
                        "name": "title",
                        "source": "/document/title"
                    },
                    {
                        "name": "name",
                        "source": "/document/name"
                    },
                    {
                        "name": "location",
                        "source": "/document/location"
                    },
                    {
                        "name": "chunk",
                        "source": "/document/chunks/*"
                    },
                    {
                        "name": "chunkVector",
                        "source": "/document/chunks/*/vector"
                    }
                ]
            }
        ],
        "parameters": {
            "projectionMode": "skipIndexingParentDocuments"
        }
    }
}


indexer_payload = {
    "name": INDEXER_NAME,
    "dataSourceName": DATASOURCE_NAME,
    "targetIndexName": INDEX_NAME,
    "skillsetName": SKILLSET_NAME,
    "schedule": {"interval": "PT30M"},  # How often do you want to check for new content in the data source
    "fieldMappings": [
        {
            "sourceFieldName": "metadata_title",
            "targetFieldName": "title"
        },
        {
            "sourceFieldName": "metadata_storage_name",
            "targetFieldName": "name"
        },

        {
            "sourceFieldName": "metadata_storage_path",
            "targetFieldName": "location"
        }
    ],
    "outputFieldMappings": [

    ],
    "parameters":
        {
            "maxFailedItems": -1,
            "maxFailedItemsPerBatch": -1,
            "configuration":
                {
                    "dataToExtract": "contentAndMetadata",
                    "imageAction": "none"
                }
        }
}

extra_body = {
    "data_sources": [
        {
            "type": "azure_search",
            "parameters": {
                "endpoint": os.environ["AZURE_SEARCH_ENDPOINT"],
                "index_name": INDEX_NAME,
                "filter": "",
                "fields_mapping": {
                    "content_fields": ["chunk"],
                    "vector_fields": ["chunkVector"],
                    "filepath_field": "location",
                    "url_field": "location",
                    "title_field": "name"
                },
                "embedding_dependency": {
                    "deployment_name": os.environ['EMBEDDING_DEPLOYMENT_NAME'],
                    "type": "deployment_name",
                    "dimensions": int(os.environ['EMBEDDING_DIMENSIONS'])
                },
                "authentication": {
                    "type": "api_key",
                    "key": os.environ["AZURE_SEARCH_KEY"]
                },
                # "semantic_configuration": "my-semantic-config",
                "query_type": "vector_simple_hybrid",
                "top_n_documents": 5
            }
        }
    ]
}


def recreate_all():
    IH.delete_all_objects([DATASOURCE_NAME, INDEX_NAME, SKILLSET_NAME, INDEXER_NAME])
    IH.create_all_objects([DATASOURCE_NAME, INDEX_NAME, SKILLSET_NAME, INDEXER_NAME],
                          [datasource_payload, index_payload, skillset_payload, indexer_payload])
    log.info("All done")

if __name__ == "__main__":
    recreate_all()