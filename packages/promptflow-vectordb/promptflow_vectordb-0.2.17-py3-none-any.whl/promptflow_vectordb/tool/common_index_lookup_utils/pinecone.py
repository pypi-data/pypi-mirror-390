from typing import Dict, List

from promptflow.runtime.utils._utils import get_resource_management_scope

from ..utils.callback import CallbackContext, tool_ui_callback


def _call_pinecone_endpoint(
    context: CallbackContext,
    pinecone_connection_name: str,
    pinecone_endpoint: str,
    params: dict = None,
):
    selected_connection = context.ml_client.connections._operation.get(
        workspace_name=context.workspace_name,
        connection_name=pinecone_connection_name,
        **context.ml_client.connections._scope_kwargs)

    url = f'https://management.azure.com{context.arm_id}' +\
        f'/connections/{selected_connection.name}/listSecrets?api-version=2022-01-01-preview'
    auth_header = f'Bearer {context.credential.get_token(get_resource_management_scope()).token}'

    secrets_response = context.http.post(url, headers={'Authorization': auth_header}).json()
    pinecone_api_key = secrets_response.get('properties', {}).get('credentials', {}).get('keys', {}).get('api_key')

    if params is None:
        params = {}

    response = context.http.get(
        pinecone_endpoint,
        headers={'Api-Key': pinecone_api_key},
        params=params,
    ).json()

    return response


@tool_ui_callback
def list_pinecone_connections(context: CallbackContext) -> List[Dict[str, str]]:
    connections = context.ml_client.connections._operation.list(
        workspace_name=context.workspace_name,
        cls=lambda objs: objs,
        category=None,
        **context.ml_client.connections._scope_kwargs)

    options = []
    for connection in connections:
        if connection.properties.category == "CustomKeys":
            # Legacy pinecone connections are defined by `environment` and `project_id` metadata keys.
            if 'environment' in connection.properties.metadata and 'project_id' in connection.properties.metadata:
                options.append({'value': connection.name, 'display_value': connection.name})
            # Newer pinecone connections are defined by `connection_type=vectorindex` and `index_type=pinecone`
            elif connection.properties.metadata.get("connection_type") == "vectorindex" and\
                    connection.properties.metadata.get("index_type") == "pinecone":
                options.append({'value': connection.name, 'display_value': connection.name})

    return options


@tool_ui_callback
def list_pinecone_indices(context: CallbackContext, pinecone_connection_name: str) -> List[Dict[str, str]]:
    list_indices_url = 'https://api.pinecone.io/indexes'
    indices_response = _call_pinecone_endpoint(context, pinecone_connection_name, list_indices_url)

    return [{'value': index["name"], 'display_value': index["name"]} for index in indices_response["indexes"]]


@tool_ui_callback
def list_pinecone_index_namespaces(
    context: CallbackContext,
    pinecone_connection_name: str,
    pinecone_index_name: str
) -> List[Dict[str, str]]:
    describe_index_url = f'https://api.pinecone.io/indexes/{pinecone_index_name}'
    index_response = _call_pinecone_endpoint(context, pinecone_connection_name, describe_index_url)
    index_host = index_response.get("host")

    index_stats_url = f'https://{index_host}/describe_index_stats'
    index_stats_response = _call_pinecone_endpoint(context, pinecone_connection_name, index_stats_url)

    index_namespaces = index_stats_response.get("namespaces")

    return [{'value': namespace, 'display_value': namespace}
            if namespace != "" else {'value': "default", 'display_value': "(Default)"}
            for namespace in index_namespaces.keys()
            ]


@tool_ui_callback
def list_pinecone_index_fields(
    context: CallbackContext,
    pinecone_connection_name: str,
    pinecone_index_name: str,
    pinecone_index_namespace: str,
) -> List[Dict[str, str]]:
    describe_index_url = f'https://api.pinecone.io/indexes/{pinecone_index_name}'
    index_response = _call_pinecone_endpoint(context, pinecone_connection_name, describe_index_url)
    index_host = index_response.get("host")

    namespace = pinecone_index_namespace if pinecone_index_namespace != "default" else ""

    list_vector_ids_url = f'https://{index_host}/vectors/list'
    vector_ids_response = _call_pinecone_endpoint(
        context,
        pinecone_connection_name,
        list_vector_ids_url,
        params={"namespace": namespace}
    )
    vector_ids = vector_ids_response.get("vectors")
    if not vector_ids:
        return []

    vector_id = vector_ids[0].get("id")

    fetch_vectors_url = f'https://{index_host}/vectors/fetch'
    vector_response = _call_pinecone_endpoint(
        context,
        pinecone_connection_name,
        fetch_vectors_url,
        params={'ids': [vector_id], 'namespace': namespace}
    )
    metadata = vector_response.get('vectors', {}).get(vector_id, {}).get('metadata', {})

    return [{'value': field, 'display_value': field} for field in metadata.keys()]
