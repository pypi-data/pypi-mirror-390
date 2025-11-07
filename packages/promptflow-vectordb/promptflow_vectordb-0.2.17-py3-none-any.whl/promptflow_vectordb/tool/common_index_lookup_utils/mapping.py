import os
import tempfile
from io import StringIO
from typing import Any, Dict

from azureml.rag.embeddings import EmbeddingsContainer
from azureml.rag.mlindex import MLIndex
from promptflow.runtime.utils._utils import get_resource_management_scope
from ruamel.yaml import YAML

from ..utils.callback import CallbackContext, tool_ui_callback
from .constants import APIVersion, EmbeddingTypes, IndexTypes
from .embeddings import _resolve_serverless_connection, _resolve_serverless_deployment
from .mlindex_client import MLIndexClient
from .validators.cosmosdb_for_nosql_validators import CosmosDBForNoSQLValidators

yaml = YAML()


@tool_ui_callback
def forward_mapping(
    context: CallbackContext,
    index_type: str,
    mlindex_asset_id: str = None,
    mlindex_path: str = None,
    acs_index_connection: str = None,
    acs_index_name: str = None,
    acs_content_field: str = None,
    acs_embedding_field: str = None,
    acs_metadata_field: str = None,
    semantic_configuration: str = None,
    faiss_index_path: str = None,
    pinecone_index_connection: str = None,
    pinecone_index_name: str = None,
    pinecone_index_namespace: str = None,
    pinecone_content_field: str = None,
    pinecone_metadata_field: str = None,
    es_index_connection: str = None,
    es_index_name: str = None,
    es_content_field: str = None,
    es_metadata_field: str = None,
    es_embedding_field: str = None,
    qdrant_index_connection: str = None,
    qdrant_index_name: str = None,
    qdrant_content_field: str = None,
    qdrant_embedding_field: str = None,
    mongodb_connection: str = None,
    mongodb_database: str = None,
    mongodb_collection: str = None,
    mongodb_index_name: str = None,
    mongodb_search_index: str = None,
    mongodb_content_field: str = None,
    mongodb_embedding_field: str = None,
    weaviate_connection: str = None,
    weaviate_collection: str = None,
    weaviate_content_field: str = None,
    weaviate_embedding_field: str = None,
    postgres_connection: str = None,
    postgres_table_name: str = None,
    postgres_search_type: str = None,
    postgres_content_field: str = None,
    postgres_embedding_field: str = None,
    cosmosdb_nosql_connection: str = None,
    cosmosdb_nosql_database_name: str = None,
    cosmosdb_nosql_container_name: str = None,
    cosmosdb_nosql_content_field: str = None,
    cosmosdb_nosql_embedding_field: str = None,
    embedding_type: str = None,
    aoai_embedding_connection: str = None,
    oai_embedding_connection: str = None,
    embedding_model: str = None,
    embedding_deployment: str = None,
    serverless_embedding_connection: str = None
) -> str:
    if index_type in {IndexTypes.MLIndexAsset, IndexTypes.MLIndexPath}:
        mlindex_client = MLIndexClient(context)
        if index_type == IndexTypes.MLIndexAsset:

            asset_id_parts = mlindex_asset_id.split('/')
            asset_name = asset_id_parts[7]
            asset_version = asset_id_parts[9]

            data_asset_obj = context.ml_client.data.get(asset_name, asset_version)
            mlindex_content = mlindex_client.get_mlindex_content(data_asset_obj.path, mlindex_asset_id)
            mlindex_path = data_asset_obj.path

        if index_type == IndexTypes.MLIndexPath:
            mlindex_content = mlindex_client.get_mlindex_content(mlindex_path)

        try:
            mlindex_config = yaml.load(mlindex_content)
            if (
                mlindex_config.get("index", {}).get("kind") == "faiss"
                and mlindex_config.get("index", {}).get("path") is None
            ):
                mlindex_config["index"]["path"] = mlindex_path
                with StringIO() as stream:
                    yaml.dump(mlindex_config, stream)
                    mlindex_content = stream.getvalue()
        except Exception as e:
            raise ValueError(f'Failed to process mlindex content with exception: { e }')

        return mlindex_content

    elif index_type in {
            IndexTypes.AzureCognitiveSearch,
            IndexTypes.AzureCosmosDBforMongoDBvCore,
            IndexTypes.AzureCosmosDBforPostgreSQL,
            IndexTypes.AzureCosmosDBforNoSQL,
            IndexTypes.FAISS,
            IndexTypes.Pinecone,
            IndexTypes.Elasticsearch,
            IndexTypes.Weaviate,
            IndexTypes.Qdrant,
            IndexTypes.MongoDB}:
        mlindex_config = {
            "index": _get_index_config(
                context,
                index_type,
                acs_index_connection,
                acs_index_name,
                acs_content_field,
                acs_embedding_field,
                acs_metadata_field,
                semantic_configuration,
                faiss_index_path,
                pinecone_index_connection,
                pinecone_index_name,
                pinecone_index_namespace,
                pinecone_content_field,
                pinecone_metadata_field,
                es_index_connection,
                es_index_name,
                es_content_field,
                es_metadata_field,
                es_embedding_field,
                qdrant_index_connection,
                qdrant_index_name,
                qdrant_content_field,
                qdrant_embedding_field,
                mongodb_connection,
                mongodb_database,
                mongodb_collection,
                mongodb_index_name,
                mongodb_search_index,
                mongodb_content_field,
                mongodb_embedding_field,
                weaviate_connection,
                weaviate_collection,
                weaviate_content_field,
                weaviate_embedding_field,
                postgres_connection,
                postgres_table_name,
                postgres_search_type,
                postgres_content_field,
                postgres_embedding_field,
                cosmosdb_nosql_connection,
                cosmosdb_nosql_database_name,
                cosmosdb_nosql_container_name,
                cosmosdb_nosql_content_field,
                cosmosdb_nosql_embedding_field,

            ),
            "embeddings": get_embeddings_config(
                context,
                embedding_type,
                aoai_embedding_connection,
                oai_embedding_connection,
                embedding_model,
                embedding_deployment,
                serverless_embedding_connection,
            ),
        }

        mlindex = MLIndex(mlindex_config=mlindex_config)
        with tempfile.TemporaryDirectory() as staging_dir:
            mlindex.save(staging_dir, just_config=True)
            with open(os.path.join(staging_dir, 'MLIndex'), 'r', encoding='utf-8') as src:
                return src.read()

    else:
        raise ValueError(f'Unexpected index type: {index_type}')


@tool_ui_callback
def reverse_mapping(context: CallbackContext, mlindex_content: str) -> Dict[str, Any]:
    with StringIO(mlindex_content) as stream:
        mlindex_config = yaml.load(stream)

    mlindex = MLIndex(mlindex_config=mlindex_config)

    index_kind = mlindex.index_config.get("kind", "none")
    if index_kind == "acs":
        mapped_index_args = {
            "index_type": IndexTypes.AzureCognitiveSearch,
            "acs_index_connection": mlindex.index_config.get("connection", {})
            .get("id", "")
            .split("/")[-1],
            "acs_index_name": mlindex.index_config.get("index"),
            "acs_content_field": mlindex.index_config.get("field_mapping", {}).get(
                "content"
            ),
            "acs_embedding_field": mlindex.index_config.get("field_mapping", {}).get(
                "embedding"
            ),
            "acs_metadata_field": mlindex.index_config.get("field_mapping", {}).get(
                "metadata"
            ),
            "semantic_configuration": mlindex.index_config.get(
                "semantic_configuration_name"
            ),
        }
    elif index_kind == "faiss":
        mapped_index_args = {
            "index_type": IndexTypes.FAISS,
            "faiss_index_path": mlindex.index_config.get("path"),
        }
    elif index_kind == "pinecone":
        mapped_index_args = {
            "index_type": IndexTypes.Pinecone,
            "pinecone_index_connection": mlindex.index_config.get("connection", {})
            .get("id", "")
            .split("/")[-1],
            "pinecone_index_name": mlindex.index_config.get("index"),
            "pinecone_content_field": mlindex.index_config.get("field_mapping", {}).get(
                "content"
            ),
            "pinecone_metadata_field": mlindex.index_config.get(
                "field_mapping", {}
            ).get("metadata"),
        }
    elif index_kind == "elasticsearch":
        mapped_index_args = {
            "index_type": IndexTypes.Elasticsearch,
            "es_index_connection": mlindex.index_config.get("connection", {})
            .get("id", "")
            .split("/")[-1],
            "es_index_name": mlindex.index_config.get("index"),
            "es_content_field": mlindex.index_config.get("field_mapping", {}).get(
                "content"
            ),
            "es_metadata_field": mlindex.index_config.get(
                "field_mapping",
            ).get("metadata"),
            "es_embedding_field": mlindex.index_config.get("field_mapping", {}).get(
                "embedding"
            ),
        }
    elif index_kind == "azure_cosmos_mongo_vcore":
        mapped_index_args = {
            "index_type": IndexTypes.AzureCosmosDBforMongoDBvCore,
            "mongodb_connection": mlindex.index_config.get("connection", {})
            .get("id", "")
            .split("/")[-1],
            "mongodb_database": mlindex.index_config.get("database"),
            "mongodb_collection": mlindex.index_config.get("collection"),
            "mongodb_index_name": mlindex.index_config.get("index"),
            "mongodb_content_field": mlindex.index_config.get("field_mapping", {}).get(
                "content"
            ),
            "mongodb_embedding_field": mlindex.index_config.get("field_mapping", {}).get(
                "embedding"
            ),
        }
    elif index_kind == "mongodb":
        mapped_index_args = {
            "index_type": IndexTypes.MongoDB,
            "mongodb_connection": mlindex.index_config.get("connection", {})
            .get("id", "")
            .split("/")[-1],
            "mongodb_database": mlindex.index_config.get("database"),
            "mongodb_collection": mlindex.index_config.get("collection"),
            "mongodb_search_index": mlindex.index_config.get("search_index"),
            "mongodb_content_field": mlindex.index_config.get("field_mapping", {}).get(
                "content"
            ),
            "mongodb_embedding_field": mlindex.index_config.get("field_mapping", {}).get(
                "embedding"
            ),
        }
    elif index_kind == "weaviate":
        mapped_index_args = {
            "index_type": IndexTypes.Weaviate,
            "weaviate_connection": mlindex.index_config.get("connection", {})
            .get("id", "")
            .split("/")[-1],
            "weaviate_collection": mlindex.index_config.get("collection"),
            "weaviate_content_field": mlindex.index_config.get("field_mapping", {}).get(
                "content"
            ),
            "weaviate_embedding_field": mlindex.index_config.get("field_mapping", {}).get(
                "embedding"
            )
        }
    elif index_kind == "qdrant":
        mapped_index_args = {
            "index_type": IndexTypes.Qdrant,
            "qdrant_index_connection": mlindex.index_config.get("connection", {})
            .get("id", "")
            .split("/")[-1],
            "qdrant_index_name": mlindex.index_config.get("index"),
            "qdrant_content_field": mlindex.index_config.get("field_mapping", {}).get(
                "content"
            ),
            "qdrant_embedding_field": mlindex.index_config.get("field_mapping", {}).get(
                "embedding"
            ),
        }
    elif index_kind == "azure_cosmos_postgresql":
        mapped_index_args = {
            "index_type": IndexTypes.AzureCosmosDBforPostgreSQL,
            "postgres_connection": mlindex.index_config.get("connection", {})
            .get("id", "")
            .split("/")[-1],
            "postgres_table_name": mlindex.index_config.get("table"),
            "postgres_search_type": mlindex.index_config.get("search_type"),
            "postgres_content_field": mlindex.index_config.get("field_mapping", {}).get(
                "content"
            ),
            "postgres_embedding_field": mlindex.index_config.get("field_mapping", {}).get(
                "embedding"
            ),
        }
    elif index_kind == "azure_cosmos_nosql":
        content = mlindex.index_config.get("field_mapping", {}).get("content")
        embedding = mlindex.index_config.get("field_mapping", {}).get("embedding")
        CosmosDBForNoSQLValidators.validate_property_paths([content, embedding])

        mapped_index_args = {
            "index_type": IndexTypes.AzureCosmosDBforNoSQL,
            "cosmosdb_nosql_connection": mlindex.index_config.get("connection", {})
            .get("id", "")
            .split("/")[-1],
            "cosmosdb_nosql_index_name": mlindex.index_config.get("index"),
            "cosmosdb_nosql_database_name": mlindex.index_config.get("database"),
            "cosmosdb_nosql_container_name": mlindex.index_config.get("container"),
            "cosmosdb_nosql_content_field": content,
            "cosmosdb_nosql_embedding_field": embedding,
        }
    else:
        raise NotImplementedError(f'"{index_kind}" is not a supported index kind.')

    embedding_kind = mlindex.embeddings_config.get("kind")
    embedding_api_type = mlindex.embeddings_config.get("api_type")
    if embedding_kind == "none":
        mapped_embedding_args = {
            "embedding_type": EmbeddingTypes.NoEmbedding,
        }
    elif embedding_kind == "open_ai":
        if embedding_api_type == "azure":
            mapped_embedding_args = {
                "embedding_type": EmbeddingTypes.AzureOpenAI,
                "aoai_embedding_connection": mlindex.embeddings_config.get(
                    "connection", {}
                )
                .get("id", "")
                .split("/")[-1],
                "embedding_deployment": mlindex.embeddings_config.get("deployment"),
            }
        else:
            raise NotImplementedError(
                '"azure" is the only supported value for embedding api_type.'
            )
    elif embedding_kind == "serverless_endpoint":
        if "connection" in mlindex.embeddings_config:
            mapped_embedding_args = {
                "embedding_type": EmbeddingTypes.ServerlessDeployment,
                "serverless_embedding_connection": "connection:"
                + mlindex.embeddings_config
                .get("connection", {})
                .get("id", "")
                .split("/")[-1],
            }
        elif "endpoint" in mlindex_config.embeddings_config:
            mapped_embedding_args = {
                "embedding_type": EmbeddingTypes.ServerlessDeployment,
                "serverless_embedding_connection": "deployment:"
                + mlindex.embeddings_config
                .get("endpoint", {})
                .get("id", "")
                .split("/")[-1],
            }

    elif embedding_kind == "hugging_face":
        mapped_embedding_args = {
            "embedding_type": EmbeddingTypes.HuggingFace,
            "embedding_model": mlindex.embedding_configs.get("model"),
        }
    else:
        raise NotImplementedError(
            f'"{embedding_kind}" embedding kind is not currently supported'
        )

    return {**mapped_index_args, **mapped_embedding_args}


def get_embeddings_config(
    context: CallbackContext,
    embedding_type: str = None,
    aoai_embedding_connection: str = None,
    oai_embedding_connection: str = None,
    embedding_model: str = None,
    embedding_deployment: str = None,
    serverless_embedding_connection: str = None,
) -> Dict[str, Any]:
    if not embedding_type or embedding_type == EmbeddingTypes.NoEmbedding:
        return {
            "kind": "none",
            "schema_version": "2",
        }

    elif embedding_type == EmbeddingTypes.AzureOpenAI:
        selected_connection = context.ml_client.connections._operation.get(
            workspace_name=context.workspace_name,
            connection_name=aoai_embedding_connection,
            **context.ml_client.connections._scope_kwargs,
        )

        resolved_embedding_model = _get_embedding_model(
            context, selected_connection, embedding_deployment
        )
        embeddings_config = {
            "kind": "open_ai",
            "api_type": "azure",
            "api_base": selected_connection.properties.target,
            "api_version": selected_connection.properties.metadata.get(
                "ApiVersion", "2023-03-15-preview"
            ),
            "batch_size": "1",
            "connection": {
                "id": selected_connection.id,
            },
            "connection_type": "workspace_connection",
            "deployment": embedding_deployment,
            "model": resolved_embedding_model,
            "schema_version": "2",
        }

    elif embedding_type == EmbeddingTypes.OpenAI:
        raise NotImplementedError()

    elif embedding_type in {EmbeddingTypes.ServerlessEndpoint, EmbeddingTypes.ServerlessDeployment}:
        id_type, name = serverless_embedding_connection.split(':')
        if id_type == "connection":
            selected_connection = context.ml_client.connections._operation.get(
                workspace_name=context.workspace_name,
                connection_name=name,
                **context.ml_client.connections._scope_kwargs,
            )

            (api_base, info) = _resolve_serverless_connection(context, selected_connection)
            embeddings_config = {
                "kind": "serverless_endpoint",
                "api_type": "serverless",
                "api_base": api_base,
                "model": info.get("model_name", "generic_embed"),
                "batch_size": "1",
                "connection": {
                    "id": selected_connection.id,
                },
                "connection_type": "workspace_connection",
                "schema_version": "2",
            }
        elif id_type == "deployment":
            auth_header = f'Bearer {context.credential.get_token(get_resource_management_scope()).token}'
            selected_deployment = context.http.get(
                f'https://management.azure.com{context.arm_id}'
                f'/serverlessEndpoints/{name}?api-version=2024-01-01-preview',
                headers={'Authorization': auth_header}).json()

            (api_base, info) = _resolve_serverless_deployment(context, selected_deployment)

            embeddings_config = {
                "kind": "serverless_endpoint",
                "api_type": "serverless",
                "api_base": api_base,
                "model": info.get("model_name", "generic_embed"),
                "batch_size": "1",
                "endpoint": {
                    "id": selected_deployment.get("id"),
                },
                "schema_version": "2",
            }
        else:
            raise ValueError(f"Unexpected serverless identifier: {id_type}")

    elif embedding_type == EmbeddingTypes.HuggingFace:
        embeddings_config = {
            "kind": "hugging_face",
            "model": embedding_model,
            "schema_version": "2",
        }

    else:
        raise ValueError(f"Unexpected embedding type: {embedding_type}")

    embedder = EmbeddingsContainer.from_metadata(embeddings_config.copy()).get_query_embed_fn()
    embeddings_config["dimension"] = len(embedder("hello world!"))
    return embeddings_config


def _get_index_config(
    context: CallbackContext,
    index_type: str,
    acs_index_connection: str = None,
    acs_index_name: str = None,
    acs_content_field: str = None,
    acs_embedding_field: str = None,
    acs_metadata_field: str = None,
    semantic_configuration: str = None,
    faiss_index_path: str = None,
    pinecone_index_connection: str = None,
    pinecone_index_name: str = None,
    pinecone_index_namespace: str = None,
    pinecone_content_field: str = None,
    pinecone_metadata_field: str = None,
    es_index_connection: str = None,
    es_index_name: str = None,
    es_content_field: str = None,
    es_metadata_field: str = None,
    es_embedding_field: str = None,
    qdrant_index_connection: str = None,
    qdrant_index_name: str = None,
    qdrant_content_field: str = None,
    qdrant_embedding_field: str = None,
    mongodb_connection: str = None,
    mongodb_database: str = None,
    mongodb_collection: str = None,
    mongodb_index_name: str = None,
    mongodb_search_index: str = None,
    mongodb_content_field: str = None,
    mongodb_embeddings_field: str = None,
    weaviate_connection: str = None,
    weaviate_collection: str = None,
    weaviate_content_field: str = None,
    weaviate_embedding_field: str = None,
    postgres_connection: str = None,
    postgres_table_name: str = None,
    postgres_search_type: str = None,
    postgres_content_field: str = None,
    postgres_embedding_field: str = None,
    cosmosdb_nosql_connection: str = None,
    cosmosdb_nosql_database_name: str = None,
    cosmosdb_nosql_container_name: str = None,
    cosmosdb_nosql_content_field: str = None,
    cosmosdb_nosql_embedding_field: str = None,
) -> Dict[str, Any]:
    if index_type == IndexTypes.AzureCognitiveSearch:
        selected_connection = context.ml_client.connections._operation.get(
            workspace_name=context.workspace_name,
            connection_name=acs_index_connection,
            **context.ml_client.connections._scope_kwargs,
        )

        return {
            "kind": "acs",
            "connection": {
                "id": selected_connection.id,
            },
            "connection_type": "workspace_connection",
            "endpoint": selected_connection.properties.target,
            "api_version": selected_connection.properties.metadata.get(
                "ApiVersion", APIVersion.ACSApiVersion
            ),
            "engine": "azure-sdk",
            "field_mapping": {
                "content": acs_content_field,
                "embedding": acs_embedding_field,
                "metadata": acs_metadata_field,
            },
            "index": acs_index_name,
            "semantic_configuration_name": semantic_configuration,
        }

    if index_type == IndexTypes.FAISS:
        return {
            "kind": "faiss",
            "engine": "langchain.vectorstores.FAISS",
            "method": "flatL2",
            "path": faiss_index_path,
        }

    if index_type == IndexTypes.Pinecone:
        selected_connection = context.ml_client.connections._operation.get(
            workspace_name=context.workspace_name,
            connection_name=pinecone_index_connection,
            **context.ml_client.connections._scope_kwargs,
        )

        return {
            "kind": "pinecone",
            "connection": {
                "id": selected_connection.id,
            },
            "connection_type": "workspace_connection",
            "engine": "azure-sdk",
            "index": pinecone_index_name,
            "namespace": pinecone_index_namespace,
            "field_mapping": {
                "content": pinecone_content_field,
                "metadata": pinecone_metadata_field,
            },
        }

    if index_type == IndexTypes.Elasticsearch:
        selected_connection = context.ml_client.connections._operation.get(
            workspace_name=context.workspace_name,
            connection_name=es_index_connection,
            **context.ml_client.connections._scope_kwargs,
        )
        es_endpoint = selected_connection.properties.metadata["endpoint"]
        return {
            "kind": "elasticsearch",
            "connection": {
                "id": selected_connection.id,
            },
            "connection_type": "workspace_connection",
            "engine": "azure-sdk",
            "index": es_index_name,
            "field_mapping": {
                "content": es_content_field,
                "metadata": es_metadata_field,
                "embedding": es_embedding_field
            },
            "endpoint": es_endpoint
        }

    if index_type == IndexTypes.AzureCosmosDBforMongoDBvCore:
        selected_connection = context.ml_client.connections._operation.get(
            workspace_name=context.workspace_name,
            connection_name=mongodb_connection,
            **context.ml_client.connections._scope_kwargs,
        )

        return {
            "kind": "azure_cosmos_mongo_vcore",
            "connection": {
                "id": selected_connection.id,
            },
            "connection_type": "workspace_connection",
            "engine": "pymongo-sdk",
            "database": mongodb_database,
            "collection": mongodb_collection,
            "index": mongodb_index_name,
            "field_mapping": {
                "content": mongodb_content_field,
                "embedding": mongodb_embeddings_field,
            },
        }

    if index_type == IndexTypes.MongoDB:
        selected_connection = context.ml_client.connections._operation.get(
            workspace_name=context.workspace_name,
            connection_name=mongodb_connection,
            **context.ml_client.connections._scope_kwargs,
        )

        return {
            "kind": "mongodb",
            "connection": {
                "id": selected_connection.id,
            },
            "connection_type": "workspace_connection",
            "engine": "pymongo-sdk",
            "database": mongodb_database,
            "collection": mongodb_collection,
            "search_index": mongodb_search_index,
            "field_mapping": {
                "content": mongodb_content_field,
                "embedding": mongodb_embeddings_field,
            },
        }

    if index_type == IndexTypes.Weaviate:
        selected_connection = context.ml_client.connections._operation.get(
            workspace_name=context.workspace_name,
            connection_name=weaviate_connection,
            **context.ml_client.connections._scope_kwargs,
        )

        return {
            "kind": "weaviate",
            "connection": {
                "id": selected_connection.id,
            },
            "cluster_url": selected_connection.properties.metadata.get("cluster_url"),
            "connection_type": "workspace_connection",
            "engine": "azure-sdk",
            "collection": weaviate_collection,
            "field_mapping": {
                "content": weaviate_content_field,
                "embedding": weaviate_embedding_field,
            },
        }

    if index_type == IndexTypes.Qdrant:
        selected_connection = context.ml_client.connections._operation.get(
            workspace_name=context.workspace_name,
            connection_name=qdrant_index_connection,
            **context.ml_client.connections._scope_kwargs,
        )
        qdrant_endpoint = selected_connection.properties.metadata["endpoint"]
        return {
            "kind": "qdrant",
            "connection": {
                "id": selected_connection.id,
            },
            "connection_type": "workspace_connection",
            "engine": "azure-sdk",
            "index": qdrant_index_name,
            "field_mapping": {
                "content": qdrant_content_field,
                "embedding": qdrant_embedding_field
            },
            "endpoint": qdrant_endpoint
        }

    if index_type == IndexTypes.AzureCosmosDBforPostgreSQL:
        selected_connection = context.ml_client.connections._operation.get(
            workspace_name=context.workspace_name,
            connection_name=postgres_connection,
            **context.ml_client.connections._scope_kwargs,
        )

        return {
            "kind": "azure_cosmos_postgresql",
            "connection": {
                "id": selected_connection.id,
            },
            "connection_type": "workspace_connection",
            "table": postgres_table_name,
            "search_type": postgres_search_type,
            "field_mapping": {
                "content": postgres_content_field,
                "embedding": postgres_embedding_field,
            },
        }

    if index_type == IndexTypes.AzureCosmosDBforNoSQL:
        CosmosDBForNoSQLValidators.validate_property_paths([cosmosdb_nosql_content_field])

        selected_connection = context.ml_client.connections._operation.get(
            workspace_name=context.workspace_name,
            connection_name=cosmosdb_nosql_connection,
            **context.ml_client.connections._scope_kwargs,
        )

        return {
            "kind": "azure_cosmos_nosql",
            "connection": {
                "id": selected_connection.id,
            },
            "connection_type": "workspace_connection",
            "database": cosmosdb_nosql_database_name,
            "container": cosmosdb_nosql_container_name,
            "field_mapping": {
                "content": cosmosdb_nosql_content_field,
                "embedding": cosmosdb_nosql_embedding_field,
            },
        }

    raise ValueError(f"Unexpected index type: {index_type}")


def _get_embedding_model(
    context: CallbackContext, selected_connection, deployment_name: str
) -> str:
    deployment_url = (
        f'https://management.azure.com{selected_connection.properties.metadata.get("ResourceId")}'
        + f"/deployments/{deployment_name}?api-version=2023-05-01"
    )
    auth_header = f'Bearer {context.credential.get_token(get_resource_management_scope()).token}'
    deployment = context.http.get(
        deployment_url, headers={"Authorization": auth_header}
    ).json()

    return deployment.get("properties", {}).get("model", {}).get("name")
