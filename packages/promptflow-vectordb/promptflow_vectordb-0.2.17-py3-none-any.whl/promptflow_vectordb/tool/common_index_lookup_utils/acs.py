from typing import Dict, List

from promptflow.connections import CognitiveSearchConnection
from promptflow.runtime.utils._utils import get_resource_management_scope

from ..utils.callback import CallbackContext, tool_ui_callback


def _fetch_acs_indices(context: CallbackContext, acs_connection, acs_index_name=""):
    selected_connection = context.ml_client.connections._operation.get(
        workspace_name=context.workspace_name,
        connection_name=acs_connection,
        **context.ml_client.connections._scope_kwargs)

    if selected_connection.properties.auth_type == "ApiKey":
        # API key auth type
        url = f'https://management.azure.com{context.arm_id}' +\
            f'/connections/{selected_connection.name}/listSecrets?api-version=2022-01-01-preview'
        auth_header = f'Bearer {context.credential.get_token(get_resource_management_scope()).token}'
        secrets_response = context.http.post(url, headers={'Authorization': auth_header}).json()
        api_key = secrets_response.get('properties', dict()).get('credentials', dict()).get('key')

        headers = {'api-key': api_key}
    else:
        # AAD auth type
        auth_token = f'Bearer {context.credential.get_token("https://search.azure.com/.default").token}'
        headers = {"Authorization": auth_token}

    api_version = selected_connection.properties.metadata.get('ApiVersion', '2023-03-15-preview')

    if acs_index_name:
        response = context.http.get(
            f'{selected_connection.properties.target}/indexes/{acs_index_name}?api-version={api_version}',
            headers=headers,
        )
    else:
        response = context.http.get(
            f'{selected_connection.properties.target}/indexes?api-version={api_version}',
            headers=headers,
        )

    if response.status_code == 403:
        raise Exception(
            f"""The auth type of connection {acs_connection} does not match
            the API Access Control level of its underlying resource.
            Please check the resource setting."""
        )

    return response.json()


@tool_ui_callback
def list_acs_indices(context: CallbackContext, acs_connection: CognitiveSearchConnection) -> List[Dict[str, str]]:

    indexes_response = _fetch_acs_indices(context, acs_connection)

    return [{
        'value': index.get('name'),
        'display_value': index.get('name')} for index in indexes_response.get('value', [])]


@tool_ui_callback
def list_acs_index_fields(
        context: CallbackContext,
        acs_connection: CognitiveSearchConnection,
        acs_index_name: str,
        field_data_type: str
) -> List[Dict[str, str]]:

    selected_index = _fetch_acs_indices(context, acs_connection, acs_index_name)

    return [{
        'value': field.get('name'),
        'display_value': field.get('name')}
        for field in selected_index.get('fields', []) if field.get('type') == field_data_type]


@tool_ui_callback
def list_acs_index_semantic_configurations(
        context: CallbackContext,
        acs_connection: CognitiveSearchConnection,
        acs_index_name: str
) -> List[Dict[str, str]]:

    selected_index = _fetch_acs_indices(context, acs_connection, acs_index_name)

    configurations = selected_index.get('semantic', {}).get('configurations', [])
    return [{'value': configuration.get('name')} for configuration in configurations]
