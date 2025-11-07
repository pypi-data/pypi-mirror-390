from typing import Dict, List

from .constants import ModelType
from ...utils.callback import CallbackContext, tool_ui_callback
from .ranker_types import resolve_serverless_connection


@tool_ui_callback
def list_serverless_ranker_connections(context: CallbackContext) -> List[Dict[str, str]]:
    serverless_connections = context.ml_client.connections._operation.list(
        workspace_name=context.workspace_name,
        cls=lambda objs: objs,
        category="Serverless",
        **context.ml_client.connections._scope_kwargs,
    )

    valid_connections = []

    for connection in serverless_connections:
        if connection.properties.category == "Serverless":
            _, info = resolve_serverless_connection(context, connection)
            if info.get("model_type") == ModelType.TextClassification:
                valid_connections.append({"value": connection.name, "display_value": connection.name})

    return valid_connections
