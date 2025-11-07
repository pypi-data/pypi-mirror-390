import os

from .connection_handler import ConnectionHandler
from ...contracts.ml_index_yaml_config import MLIndexConnection


class EnvConnectionHandler(ConnectionHandler):

    @staticmethod
    def get_key(connection: MLIndexConnection) -> str:
        if connection.key in os.environ:
            return os.environ[connection.key]

    @staticmethod
    def get_api_base(connection: MLIndexConnection) -> str:
        return None

    @staticmethod
    def get_api_version(connection: MLIndexConnection) -> str:
        return None

    @staticmethod
    def get_api_type(connection: MLIndexConnection) -> str:
        return None
