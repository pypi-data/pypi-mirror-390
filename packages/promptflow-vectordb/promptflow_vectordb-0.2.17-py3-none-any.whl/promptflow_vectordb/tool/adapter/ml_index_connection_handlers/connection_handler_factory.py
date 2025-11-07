from .connection_handler import ConnectionHandler
from ...contracts.ml_index_yaml_config import MLIndexConnectionType
from ....core.contracts.exceptions import UnsupportedFeatureException


class UnsupportedConnectionHandlerTypeException(UnsupportedFeatureException):
    pass


class ConnectionHandlerFactory:
    @staticmethod
    def get_connection_handler(connection_type: MLIndexConnectionType) -> ConnectionHandler:
        if connection_type == MLIndexConnectionType.ENVIRONMENT:
            from .env_connection_handler import EnvConnectionHandler
            return EnvConnectionHandler()
        elif connection_type == MLIndexConnectionType.WORKSPACE_KEYVAULT:
            from .keyvault_connection_hander import KeyVaultConnectionHandler
            return KeyVaultConnectionHandler()
        elif connection_type == MLIndexConnectionType.WORKSPACE_CONNECTION:
            from .workspace_connection_handler import WorkspaceConnectionHandler
            return WorkspaceConnectionHandler()
        else:
            raise UnsupportedConnectionHandlerTypeException(
                f"Connection handler type {connection_type} is not supported"
            )
