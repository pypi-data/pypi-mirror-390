from typing import Dict, List

import psycopg2
from promptflow.runtime.utils._utils import get_resource_management_scope
from psycopg2._psycopg import connection

from ..utils.callback import CallbackContext, tool_ui_callback


@tool_ui_callback
def list_postgresql_connections(context: CallbackContext) -> List[Dict[str, str]]:
    connections = context.ml_client.connections._operation.list(
        workspace_name=context.workspace_name,
        cls=lambda objs: objs,
        category=None,
        **context.ml_client.connections._scope_kwargs,
    )

    options = []
    for conn in connections:
        if (
            conn.properties.category == "CustomKeys"
            and conn.properties.metadata.get("connection_type") == "vectorindex"
            and conn.properties.metadata.get("index_type")
            == "azurecosmosdbforpostgresql"
        ):
            options.append({"value": conn.name, "display_value": conn.name})

    return options


@tool_ui_callback
def list_postgresql_tables(
    context: CallbackContext, postgres_connection: str
) -> List[Dict[str, str]]:
    conn = _get_postgresql_connection(context, postgres_connection)
    cur = conn.cursor()
    options = []

    cur.execute(
        "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema')"
    )
    tables = cur.fetchall()

    for table in tables:
        options.append({"value": table[0], "display_value": table[0]})

    close_postgresql_connection(conn)

    return options


@tool_ui_callback
def list_postgresql_search_types(context: CallbackContext) -> List[Dict[str, str]]:
    search_types = ["L2", "Cosine", "Inner"]
    options = [{"value": st, "display_value": st} for st in search_types]
    return options


@tool_ui_callback
def list_postgresql_table_fields(
    context: CallbackContext,
    postgres_connection: str,
    postgres_table_name: str,
    field_data_type: str,
) -> List[Dict[str, str]]:
    conn = _get_postgresql_connection(context, postgres_connection)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            attname AS column_name,
            format_type(atttypid, atttypmod) AS data_type
        FROM
            pg_attribute
        WHERE
            attrelid = %s::regclass AND
            attnum > 0 AND
            NOT attisdropped
    """,
        (postgres_table_name,),
    )

    columns = cur.fetchall()
    close_postgresql_connection(conn)

    options = []
    for col, dt in columns:
        if field_data_type == str(dt):
            options.append({"value": col, "display_value": col})

    return options


def close_postgresql_connection(conn: connection):
    conn.cursor().close()
    conn.close()


def _get_postgresql_connection(
    context: CallbackContext, postgresql_connection: str
) -> connection:
    selected_connection = context.ml_client.connections._operation.get(
        workspace_name=context.workspace_name,
        connection_name=postgresql_connection,
        **context.ml_client.connections._scope_kwargs,
    )

    url = f"https://management.azure.com{selected_connection.id}/listSecrets?api-version=2022-01-01-preview"
    auth_header = f'Bearer {context.credential.get_token(get_resource_management_scope()).token}'

    secrets_response = context.http.post(
        url, headers={"Authorization": auth_header}
    ).json()
    postgresql_connection_string = (
        secrets_response.get("properties", {})
        .get("credentials", {})
        .get("keys", {})
        .get("connection_string")
    )

    return psycopg2.connect(postgresql_connection_string)
