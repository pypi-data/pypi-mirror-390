from typing import Dict, List

from azure.cosmos import CosmosClient
from promptflow.runtime.utils._utils import get_resource_management_scope

from ..utils.callback import CallbackContext, tool_ui_callback


@tool_ui_callback
def list_cosmosdb_nosql_connections(context: CallbackContext) -> List[Dict[str, str]]:
    connections = context.ml_client.connections._operation.list(
        workspace_name=context.workspace_name,
        cls=lambda objs: objs,
        category="CustomKeys",
        **context.ml_client.connections._scope_kwargs,
    )

    options = []
    for conn in connections:
        if (
            conn.properties.metadata.get("connection_type") == "vectorindex"
            and conn.properties.metadata.get("index_type")
            == "azurecosmosdbfornosql"
        ):
            options.append({"value": conn.name, "display_value": conn.name})

    return options


@tool_ui_callback
def list_cosmosdb_databases(
    context: CallbackContext, cosmosdb_nosql_connection: str
) -> List[Dict[str, str]]:
    client = _get_cosmosdb_client(context, cosmosdb_nosql_connection)
    options = []

    databases = list(client.list_databases())

    for db in databases:
        options.append({"value": db['id'], "display_value": db['id']})

    return options


@tool_ui_callback
def list_cosmosdb_containers(
    context: CallbackContext, cosmosdb_nosql_connection: str, cosmosdb_nosql_database_name: str
) -> List[Dict[str, str]]:
    client = _get_cosmosdb_client(context, cosmosdb_nosql_connection)
    options = []

    db_client = client.get_database_client(database=cosmosdb_nosql_database_name)
    containers = list(db_client.list_containers())

    for container in containers:
        options.append({"value": container['id'], "display_value": container['id']})

    return options


@tool_ui_callback
def list_cosmosdb_nosql_content_fields(
    context: CallbackContext,
    cosmosdb_nosql_connection: str,
    cosmosdb_nosql_database_name: str,
    cosmosdb_nosql_container_name: str,
) -> List[Dict[str, str]]:
    client = _get_cosmosdb_client(context, cosmosdb_nosql_connection)
    db_client = client.get_database_client(database=cosmosdb_nosql_database_name)
    container_client = db_client.get_container_client(container=cosmosdb_nosql_container_name)

    # Query a sample of documents
    query = "SELECT TOP 3 * FROM c"
    items = list(container_client.query_items(
        query=query,
        enable_cross_partition_query=True,
    ))

    property_types = {}

    options = []
    for item in items:
        for key, value in item.items():
            if not key.startswith('_') and not key.startswith('@'):
                property_types[key] = type(value).__name__

    for key in property_types.keys():
        if property_types[key] == "str" or property_types[key] == "dict":
            option = "/" + key
            options.append({"value": option, "display_value": option})

    return options


@tool_ui_callback
def list_cosmosdb_nosql_embedding_fields(
    context: CallbackContext,
    cosmosdb_nosql_connection: str,
    cosmosdb_nosql_database_name: str,
    cosmosdb_nosql_container_name: str,
) -> List[Dict[str, str]]:
    client = _get_cosmosdb_client(context, cosmosdb_nosql_connection)
    db_client = client.get_database_client(database=cosmosdb_nosql_database_name)
    container_client = db_client.get_container_client(container=cosmosdb_nosql_container_name)

    # Query index policies
    options = []
    try:
        properties = container_client.read()
        vector_embeddings = properties['vectorEmbeddingPolicy']['vectorEmbeddings']
        for vector_embedding in vector_embeddings:
            embedding_key = vector_embedding['path']
            options.append({"value": embedding_key, "display_value": embedding_key})
    except Exception as e:
        raise ValueError(f"Failed to list embedding keys, please check container policies, {e}")

    return options


def _get_cosmosdb_client(
    context: CallbackContext, cosmosdb_nosql_connection: str
) -> CosmosClient:
    selected_connection = context.ml_client.connections._operation.get(
        workspace_name=context.workspace_name,
        connection_name=cosmosdb_nosql_connection,
        **context.ml_client.connections._scope_kwargs,
    )

    url = f"https://management.azure.com{selected_connection.id}/listSecrets?api-version=2022-01-01-preview"
    auth_header = f'Bearer {context.credential.get_token(get_resource_management_scope()).token}'

    secrets_response = context.http.post(
        url, headers={"Authorization": auth_header}
    ).json()
    cosmosdb_nosql_connection_string = (
        secrets_response.get("properties", {})
        .get("credentials", {})
        .get("keys", {})
        .get("connection_string")
    )

    return CosmosClient.from_connection_string(conn_str=cosmosdb_nosql_connection_string)
