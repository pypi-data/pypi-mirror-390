from .constants import IndexTypes
from .mlindex_client import MLIndexClient
from ..utils.callback import CallbackContext, tool_ui_callback
from typing import Dict, List


@tool_ui_callback
def list_available_index_types(context: CallbackContext) -> List[Dict[str, str]]:
    connections = context.ml_client.connections._operation.list(
        workspace_name=context.workspace_name,
        cls=lambda objs: objs,
        category=None,
        **context.ml_client.connections._scope_kwargs)

    mlindex_client = MLIndexClient(context)
    registered_indices = mlindex_client.list_indices()

    workspace_contains_acs_connection = False
    workspace_contains_pinecone_connection = False
    workspace_contains_elasticsearch_connection = False
    workspace_contains_cosmosdb_mongodb_connection = False
    workspace_contains_mongodb_connection = False
    workspace_contains_postgresql_connection = False
    workspace_contains_weaviate_connection = False
    workspace_contains_qdrant_connection = False
    workspace_contains_cosmosdb_nosql_connection = False

    for connection in connections:
        if connection.properties.category == "CognitiveSearch":
            workspace_contains_acs_connection = True
        if connection.properties.category == "CustomKeys":
            # TODO: Deprecated connection contract. Will clean up.
            if "environment" in connection.properties.metadata and "project_id" in connection.properties.metadata:
                workspace_contains_pinecone_connection = True

            elif connection.properties.metadata.get("connection_type") == "vectorindex" and \
                    "index_type" in connection.properties.metadata:
                if connection.properties.metadata["index_type"] == "azurecosmosdbformongodbvcore":
                    workspace_contains_cosmosdb_mongodb_connection = True
                if connection.properties.metadata["index_type"] == "mongodb":
                    workspace_contains_mongodb_connection = True
                if connection.properties.metadata["index_type"] == "azurecosmosdbfornosql":
                    workspace_contains_cosmosdb_nosql_connection = True
                elif connection.properties.metadata["index_type"] == "elasticsearch" and \
                        "endpoint" in connection.properties.metadata:
                    workspace_contains_elasticsearch_connection = True
                elif connection.properties.metadata["index_type"] == "pinecone":
                    workspace_contains_pinecone_connection = True
                elif connection.properties.metadata["index_type"] == "azurecosmosdbforpostgresql":
                    workspace_contains_postgresql_connection = True
                elif connection.properties.metadata["index_type"] == "weaviate" and \
                        connection.properties.metadata.get("cluster_url", None):
                    workspace_contains_weaviate_connection = True
                elif connection.properties.metadata["index_type"] == "qdrant" and \
                        "endpoint" in connection.properties.metadata:
                    workspace_contains_qdrant_connection = True

        if workspace_contains_acs_connection and \
                workspace_contains_pinecone_connection and \
                workspace_contains_elasticsearch_connection and \
                workspace_contains_mongodb_connection and \
                workspace_contains_postgresql_connection and \
                workspace_contains_weaviate_connection and \
                workspace_contains_qdrant_connection and \
                workspace_contains_cosmosdb_nosql_connection:
            break

    index_options = []

    if len([index for index in registered_indices if index.status == 'Ready']) > 0:
        index_options.append({
            'value': IndexTypes.MLIndexAsset,
        })

    if workspace_contains_acs_connection:
        index_options.append({
            'value': IndexTypes.AzureCognitiveSearch,
        })

    index_options.append({
        'value': IndexTypes.FAISS,
    })

    if workspace_contains_pinecone_connection:
        index_options.append({
            'value': IndexTypes.Pinecone,
        })

    if workspace_contains_elasticsearch_connection:
        index_options.append({
            'value': IndexTypes.Elasticsearch,
        })

    if workspace_contains_cosmosdb_mongodb_connection:
        index_options.append({
            'value': IndexTypes.AzureCosmosDBforMongoDBvCore
        })

    if workspace_contains_mongodb_connection:
        index_options.append({
            'value': IndexTypes.MongoDB
        })

    if (workspace_contains_qdrant_connection):
        index_options.append({
            'value': IndexTypes.Qdrant
        })

    if workspace_contains_postgresql_connection:
        index_options.append({
            'value': IndexTypes.AzureCosmosDBforPostgreSQL
        })

    index_options.append({
        'value': IndexTypes.MLIndexPath,
    })

    if workspace_contains_weaviate_connection:
        index_options.append({
            'value': IndexTypes.Weaviate
        })

    if workspace_contains_cosmosdb_nosql_connection:
        index_options.append({
            'value': IndexTypes.AzureCosmosDBforNoSQL
        })

    return index_options
