from typing import Dict, List

from promptflow.runtime.utils._utils import get_resource_management_scope
from pymongo import MongoClient
from pymongo_schema.extract import extract_pymongo_client_schema

from ..utils.callback import CallbackContext, tool_ui_callback
from .constants import IndexTypes


@tool_ui_callback
def list_mongodb_connections(context: CallbackContext, index_type: str) -> List[Dict[str, str]]:
    connections = context.ml_client.connections._operation.list(
        workspace_name=context.workspace_name,
        cls=lambda objs: objs,
        category=None,
        **context.ml_client.connections._scope_kwargs)

    options = []
    index_kind = "azurecosmosdbformongodbvcore" \
        if index_type == IndexTypes.AzureCosmosDBforMongoDBvCore else "mongodb"
    for connection in connections:
        if connection.properties.category == "CustomKeys" and \
                connection.properties.metadata.get("connection_type") == "vectorindex" and \
                connection.properties.metadata.get("index_type") == index_kind:
            options.append({'value': connection.name, 'display_value': connection.name})

    return options


@tool_ui_callback
def list_mongodb_databases(
        context: CallbackContext,
        mongodb_connection: str,
        **kwargs
) -> List[Dict[str, str]]:
    client = _get_mongo_client(context, mongodb_connection)
    options = []

    for database in client.list_database_names():
        options.append({'value': database, 'display_value': database})

    return options


@tool_ui_callback
def list_mongodb_collections(
        context: CallbackContext,
        mongodb_connection: str,
        mongodb_database: str,
        **kwargs
) -> List[Dict[str, str]]:
    client = _get_mongo_client(context, mongodb_connection)
    options = []

    for collection in client[mongodb_database].list_collection_names():
        options.append({'value': collection, 'display_value': collection})

    return options


@tool_ui_callback
def list_mongodb_indexes(
        context: CallbackContext,
        mongodb_connection: str,
        mongodb_database: str,
        mongodb_collection: str
) -> List[Dict[str, str]]:
    client = _get_mongo_client(context, mongodb_connection)
    options = []

    for collection in client[mongodb_database][mongodb_collection].index_information():
        options.append({'value': collection, 'display_value': collection})

    return options


@tool_ui_callback
def list_mongodb_search_indexes(
        context: CallbackContext,
        mongodb_connection: str,
        mongodb_database: str,
        mongodb_collection: str
) -> List[Dict[str, str]]:
    client = _get_mongo_client(context, mongodb_connection)
    options = []

    for index in client[mongodb_database][mongodb_collection].list_search_indexes():
        if index['type'] == 'vectorSearch':
            options.append({'value': index['name'], 'display_value': index['name']})

    return options


@tool_ui_callback
def list_mongodb_index_fields(
        context: CallbackContext,
        mongodb_connection: str,
        mongodb_database: str,
        mongodb_collection: str,
        field_data_type: str,
        **kwargs
) -> List[Dict[str, str]]:
    client = _get_mongo_client(context, mongodb_connection)
    options = []

    collection_schema = extract_pymongo_client_schema(
        client,
        mongodb_database,
        mongodb_collection)[mongodb_database][mongodb_collection]

    if field_data_type.startswith("ARRAY("):
        type_matcher = {
            'type': 'ARRAY',
            'array_type': field_data_type[6:].rstrip(')'),
        }
    else:
        type_matcher = {
            'type': field_data_type,
        }

    for field, spec in collection_schema['object'].items():
        match = True
        for key, value in type_matcher.items():
            if spec.get(key) != value:
                match = False
                break
        if match:
            options.append({'value': field, 'display_value': field})

    return options


@tool_ui_callback
def list_mongodb_embedding_fields(
        context: CallbackContext,
        index_type: str,
        mongodb_connection: str,
        mongodb_database: str,
        mongodb_collection: str,
        mongodb_search_index: str = None,
) -> List[Dict[str, str]]:
    client = _get_mongo_client(context, mongodb_connection)
    options = []

    if index_type == IndexTypes.MongoDB:
        for index in client[mongodb_database][mongodb_collection].list_search_indexes(mongodb_search_index):
            for field in index['latestDefinition']['fields']:
                if field['type'] == 'vector':
                    options.append({'value': field['path'], 'display_value': field['path']})
    elif index_type == IndexTypes.AzureCosmosDBforMongoDBvCore:
        options = list_mongodb_index_fields(
            context=context,
            mongodb_collection=mongodb_connection,
            mongodb_database=mongodb_database,
            mongodb_connection=mongodb_collection,
            field_data_type="ARRAY(float)"
        )
    else:
        raise NotImplementedError()

    return options


def _get_mongo_client(context: CallbackContext, mongodb_connection: str) -> MongoClient:
    selected_connection = context.ml_client.connections._operation.get(
        workspace_name=context.workspace_name,
        connection_name=mongodb_connection,
        **context.ml_client.connections._scope_kwargs)

    url = f'https://management.azure.com{selected_connection.id}/listSecrets?api-version=2022-01-01-preview'
    auth_header = f'Bearer {context.credential.get_token(get_resource_management_scope()).token}'

    secrets_response = context.http.post(url, headers={'Authorization': auth_header}).json()
    mongodb_connection_string = secrets_response\
        .get('properties', {})\
        .get('credentials', {})\
        .get('keys', {})\
        .get('connection_string')

    return MongoClient(mongodb_connection_string)
