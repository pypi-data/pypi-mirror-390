from abc import ABC, abstractstaticmethod

from ...contracts.ml_index_yaml_config import MLIndexConnection


class ConnectionHandler(ABC):

    @abstractstaticmethod
    def get_key(connection: MLIndexConnection) -> str:
        pass

    @abstractstaticmethod
    def get_api_base(connection: MLIndexConnection) -> str:
        pass

    @abstractstaticmethod
    def get_api_version(connection: MLIndexConnection) -> str:
        pass

    @abstractstaticmethod
    def get_api_type(connection: MLIndexConnection) -> str:
        pass
