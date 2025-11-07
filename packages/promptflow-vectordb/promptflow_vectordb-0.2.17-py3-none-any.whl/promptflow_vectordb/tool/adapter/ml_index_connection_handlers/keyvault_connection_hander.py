from azure.keyvault.secrets import SecretClient

from .connection_handler import ConnectionHandler
from ...contracts.ml_index_yaml_config import MLIndexConnection
from ....core.utils.aml_helpers import WorkspaceInfo, AmlAgent


class KeyVaultConnectionHandler(ConnectionHandler):

    @staticmethod
    def get_key(connection: MLIndexConnection) -> str:

        workspace_info = WorkspaceInfo(
            subscription_id=connection.subscription,
            resource_group=connection.resource_group,
            workspace_name=connection.workspace
        )
        secret_client = AmlAgent(workspace_info).get_key_vault()
        return KeyVaultConnectionHandler.__get_secret(connection.key, secret_client)

    @staticmethod
    def get_api_base(connection: MLIndexConnection) -> str:
        return None

    @staticmethod
    def get_api_version(connection: MLIndexConnection) -> str:
        return None

    @staticmethod
    def get_api_type(connection: MLIndexConnection) -> str:
        return None

    @staticmethod
    def __get_secret(name: str, secret_client: SecretClient = None) -> str:

        if secret_client:
            return secret_client.get_secret(name).value
