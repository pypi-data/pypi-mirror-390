from typing import Dict, List

from promptflow.runtime.utils._utils import get_resource_management_scope

from ..utils.callback import CallbackContext, tool_ui_callback


def get_es_connection_credentials(context: CallbackContext, es_index_connection: str):
    selected_connection = context.ml_client.connections._operation.get(
        workspace_name=context.workspace_name,
        connection_name=es_index_connection,
        **context.ml_client.connections._scope_kwargs)

    url = f'https://management.azure.com{context.arm_id}' +\
        f'/connections/{selected_connection.name}/listSecrets?api-version=2022-01-01-preview'
    auth_header = f'Bearer {context.credential.get_token(get_resource_management_scope()).token}'

    secrets_response = context.http.post(url, headers={'Authorization': auth_header}).json()
    return secrets_response


@tool_ui_callback
def list_es_connections(context: CallbackContext) -> List[Dict[str, str]]:
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
                connection.properties.metadata.get("index_type") == "elasticsearch":
            options.append({'value': connection.name, 'display_value': connection.name})

    return options


@tool_ui_callback
def list_es_fields(
        context: CallbackContext,
        es_index_connection: str,
        es_index_name: str,
        type_match: str
) -> List[Dict[str, str]]:
    secrets_response = get_es_connection_credentials(context, es_index_connection)
    es_api_key = secrets_response.get('properties', {}).get('credentials', {}).get('keys', {}).get('api_key')
    es_search_host = secrets_response.get('properties', {}).get('metadata', {}).get('endpoint').rstrip()

    list_indices_mapping_url = f'{es_search_host}/{es_index_name}/_mapping'
    index_mapping_response = context.http.get(
        list_indices_mapping_url, headers={"Authorization": f"ApiKey {es_api_key}"}
    ).json()
    options = []
    property_fields = index_mapping_response.get(es_index_name, {}).get('mappings', {}).get('properties', {})
    for field in property_fields:
        if (property_fields[field].get('type') == type_match):
            options.append({'value': field, 'display_value': field})
    return options


@tool_ui_callback
def list_es_indices(context: CallbackContext, es_index_connection: str) -> List[Dict[str, str]]:
    secrets_response = get_es_connection_credentials(context, es_index_connection)

    es_api_key = secrets_response.get('properties', {}).get('credentials', {}).get('keys', {}).get('api_key')
    es_search_host = secrets_response.get('properties', {}).get('metadata', {}).get('endpoint').rstrip()

    # Construct the es list indices api request
    list_indices_url = f'{es_search_host}/_cat/indices?v&format=json'
    indices_response = context.http.get(list_indices_url, headers={"Authorization": f"ApiKey {es_api_key}"}).json()
    # filter out system indices that begins with .
    return [{"value": index["index"], "display_value": index["index"]}
            for index in indices_response if not index["index"].startswith(".")]
