from typing import Any

from promptflow.runtime.connections import build_connection_dict
from promptflow.connections import (  # noqa: F401
    AzureOpenAIConnection,
    OpenAIConnection,
    CognitiveSearchConnection,
    CustomConnection
)

from ...connections.pinecone import PineconeConnection  # noqa: F401
from ...connections.qdrant import QdrantConnection  # noqa: F401
from ...connections.weaviate import WeaviateConnection  # noqa: F401

from ...core.utils.global_instance_manager import GlobalInstanceManager
from ...core.utils.aml_helpers import WorkspaceConnectionInfo, AmlHelpers


class WorkspaceConnectionManager(GlobalInstanceManager):

    def get_connection_with_id(
        self,
        connection_id: str,
        credential: Any = None
    ) -> Any:

        ws_connection_info = AmlHelpers.parse_workspace_connection_id(connection_id)
        return self.get_instance(
            ws_connection_info=ws_connection_info,
            credential=credential
        )

    def get_instance(
        self,
        ws_connection_info: WorkspaceConnectionInfo,
        credential: Any = None
    ) -> Any:

        ws_connection_identifier = ws_connection_info.to_tuple()

        return super()._get_instance(
            identifier=ws_connection_identifier,
            ws_connection_info=ws_connection_info,
            credential=credential
        )

    def _create_instance(
        self,
        ws_connection_info: WorkspaceConnectionInfo,
        credential: Any = None
    ) -> Any:
        connections = build_connection_dict(
            connection_names=[ws_connection_info.connection_name],
            subscription_id=ws_connection_info.subscription_id,
            resource_group=ws_connection_info.resource_group,
            workspace_name=ws_connection_info.workspace_name,
            credential=credential
        )

        if (connections is not None) and (ws_connection_info.connection_name in connections):
            data: dict = connections[ws_connection_info.connection_name]
            connection_type = globals()[data["type"]]
            value_dict: dict = data.get("value", {})
            if connection_type == CustomConnection:
                secrets = {k: v for k, v in value_dict.items() if k in data.get("secret_keys", [])}
                configs = {k: v for k, v in value_dict.items() if k not in secrets}
                connection = CustomConnection(configs=configs, secrets=secrets)
            else:
                connection = connection_type(**value_dict)
        return connection
