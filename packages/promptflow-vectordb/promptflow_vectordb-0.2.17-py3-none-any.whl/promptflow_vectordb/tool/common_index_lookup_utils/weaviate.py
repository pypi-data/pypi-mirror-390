from typing import Dict, List

import weaviate
from promptflow.runtime.utils._utils import get_resource_management_scope

from ..utils.callback import CallbackContext, tool_ui_callback


def _get_weaviate_client(context: CallbackContext, weaviate_connection: str):
    selected_connection = context.ml_client.connections._operation.get(
        workspace_name=context.workspace_name,
        connection_name=weaviate_connection,
        **context.ml_client.connections._scope_kwargs)

    url = f'https://management.azure.com{selected_connection.id}/listSecrets?api-version=2022-01-01-preview'
    auth_header = f'Bearer {context.credential.get_token(get_resource_management_scope()).token}'

    secrets_response = context.http.post(url, headers={'Authorization': auth_header}).json()

    api_key = secrets_response.get('properties', {}).get('credentials', {}).get('keys', {}).get('api_key')
    cluster_url = selected_connection.properties.metadata.get('cluster_url')

    weaviate_client = weaviate.connect_to_wcs(
        cluster_url=cluster_url,
        auth_credentials=weaviate.auth.AuthApiKey(api_key),
    )

    return weaviate_client


@tool_ui_callback
def list_weaviate_connections(context: CallbackContext) -> List[Dict[str, str]]:
    connections = context.ml_client.connections._operation.list(
        workspace_name=context.workspace_name,
        cls=lambda objs: objs,
        category=None,
        **context.ml_client.connections._scope_kwargs)

    options = []
    for connection in connections:
        if connection.properties.category == "CustomKeys" and \
                connection.properties.metadata.get("connection_type") == "vectorindex" and \
                connection.properties.metadata.get("index_type") == "weaviate":
            options.append({'value': connection.name, 'display_value': connection.name})

    return options


@tool_ui_callback
def list_weaviate_collections(context: CallbackContext, weaviate_connection: str) -> List[Dict[str, str]]:
    client = _get_weaviate_client(context, weaviate_connection)
    options = []

    for collection in client.collections.list_all():
        options.append({'value': collection, 'display_value': collection})

    return options


@tool_ui_callback
def list_weaviate_collection_properties(
    context: CallbackContext,
    weaviate_connection: str,
    weaviate_collection: str,
    field_data_type: str
) -> List[Dict[str, str]]:
    client = _get_weaviate_client(context, weaviate_connection)
    collection = client.collections.get(weaviate_collection)

    properties = []
    for property in collection.config.get().properties:
        if str(property.data_type) == field_data_type:
            properties.append({'value': property.name, 'display_value': property.name})

    return properties


@tool_ui_callback
def list_weaviate_collection_vector_fields(
    context: CallbackContext,
    weaviate_connection: str,
    weaviate_collection: str,
) -> List[Dict[str, str]]:
    client = _get_weaviate_client(context, weaviate_connection)
    collection = client.collections.get(weaviate_collection)

    vector_configs = collection.config.get().vector_config
    if not vector_configs:
        return []

    vector_fields = []
    for field in vector_configs:
        vector_fields.append({'value': field, 'display_value': field})

    return vector_fields
