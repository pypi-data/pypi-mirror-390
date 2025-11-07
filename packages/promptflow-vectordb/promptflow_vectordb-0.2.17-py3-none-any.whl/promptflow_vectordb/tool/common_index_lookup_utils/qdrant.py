from typing import Dict, List

from promptflow.runtime.utils._utils import get_resource_management_scope
from qdrant_client import QdrantClient

from ..utils.callback import CallbackContext, tool_ui_callback


def get_qdrant_connection_credentials(context: CallbackContext, qdrant_index_connection: str):
    selected_connection = context.ml_client.connections._operation.get(
        workspace_name=context.workspace_name,
        connection_name=qdrant_index_connection,
        **context.ml_client.connections._scope_kwargs)

    url = f'https://management.azure.com{context.arm_id}' +\
        f'/connections/{selected_connection.name}/listSecrets?api-version=2022-01-01-preview'
    auth_header = f'Bearer {context.credential.get_token(get_resource_management_scope()).token}'

    secrets_response = context.http.post(url, headers={'Authorization': auth_header}).json()
    return secrets_response


@tool_ui_callback
def list_qdrant_connections(context: CallbackContext) -> List[Dict[str, str]]:
    connections = context.ml_client.connections._operation.list(
        workspace_name=context.workspace_name,
        cls=lambda objs: objs,
        category=None,
        **context.ml_client.connections._scope_kwargs)
    options = []
    for connection in connections:
        if connection.properties.category == "CustomKeys" and \
                connection.properties.metadata.get("connection_type") == "vectorindex" and \
                "endpoint" in connection.properties.metadata and \
                connection.properties.metadata.get("index_type") == "qdrant":
            options.append({'value': connection.name, 'display_value': connection.name})

    return options


@tool_ui_callback
def list_qdrant_fields_by_type(
        context: CallbackContext,
        qdrant_index_connection: str,
        qdrant_index_name: str,
        type_match: str
) -> List[Dict[str, str]]:
    secrets_response = get_qdrant_connection_credentials(context, qdrant_index_connection)
    qdrant_api_key = secrets_response.get('properties', {}).get('credentials', {}).get('keys', {}).get('api_key')
    qdrant_host = secrets_response.get('properties', {}).get('metadata', {}).get('endpoint').rstrip()

    qdrant_client = QdrantClient(url=qdrant_host, api_key=qdrant_api_key)
    collection_mapping_response = qdrant_client.get_collection(collection_name=qdrant_index_name)
    options = []
    if (type_match == "vector"):
        for vector in collection_mapping_response.config.params.vectors:
            options.append({'value': vector, 'display_value': vector})
    elif (type_match == "content"):
        for schema in collection_mapping_response.payload_schema:
            options.append({'value': schema, 'display_value': schema})
    return options


@tool_ui_callback
def list_qdrant_indices(context: CallbackContext, qdrant_index_connection: str) -> List[Dict[str, str]]:
    secrets_response = get_qdrant_connection_credentials(context, qdrant_index_connection)

    qdrant_api_key = secrets_response.get('properties', {}).get('credentials', {}).get('keys', {}).get('api_key')
    qdrant_host = secrets_response.get('properties', {}).get('metadata', {}).get('endpoint').rstrip()

    qdrant_client = QdrantClient(url=qdrant_host, api_key=qdrant_api_key)
    collections_response = qdrant_client.get_collections()
    return [{"value": index[1][0].name, "display_value": index[1][0].name}
            for index in collections_response]
