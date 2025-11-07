import os
from abc import ABC, abstractmethod

from ..contracts import ExecutionConfig, ConfigWithSecrets, SecretSourceType


class SecretHandler(ABC):

    @abstractmethod
    def get_secret_value(self, name: str) -> str:
        pass

    @abstractmethod
    def try_get_secret_value(self, name: str) -> str:
        pass


class AzureKeyVaultSecretHandler(SecretHandler):

    def __init__(self, akv_url: str):
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient
        credential = DefaultAzureCredential()
        self.__secret_client = SecretClient(vault_url=akv_url, credential=credential)

    def get_secret_value(self, name: str) -> str:
        return self.__secret_client.get_secret(name).value

    def try_get_secret_value(self, name: str) -> str:
        secret = self.__secret_client.get_secret(name)
        if secret:
            return secret.value
        return None


class EnvSecretHandler(SecretHandler):

    def get_secret_value(self, name: str) -> str:
        return os.environ.get(name)

    def try_get_secret_value(self, name: str) -> str:
        if (name is not None) and (name in os.environ):
            return self.get_secret_value(name)
        return None


class PlainSecretHandler(SecretHandler):

    def get_secret_value(self, name: str) -> str:
        return name

    def try_get_secret_value(self, name: str) -> str:
        return name


class SecretManager:

    def __init__(self, config: ExecutionConfig):
        self.__config = config
        self.__set_handler()

    def __set_handler(self) -> SecretHandler:
        if self.__config.secret_source_type == SecretSourceType.ENV:
            self.__handler = EnvSecretHandler()
        elif self.__config.secret_source_type == SecretSourceType.AKV:
            self.__handler = AzureKeyVaultSecretHandler(self.__config.akv_url)
        elif self.__config.secret_source_type == SecretSourceType.PLAIN:
            self.__handler = PlainSecretHandler()
        return None

    def resolve_secrets(self, config: ConfigWithSecrets):

        secret_fields = config.get_secret_fields()
        for secret_field in secret_fields:
            secret_value = self.__handler.try_get_secret_value(secret_field.name)
            secret_field.resolve(secret_value)
