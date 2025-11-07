import os
import logging
from typing import List, Union, Any
from dataclasses import dataclass, fields

from .types import StorageType, IndexType, EngineType, EmbeddingModelType, SecretSourceType
from .constants import FileNames
from .secret import Secret
from .identifier_converter import IdentifierConverter


class ConfigWithSecrets:

    def get_secret_fields(self) -> List[Secret]:
        secret_fields = [getattr(self, field.name) for field in fields(
            self) if isinstance(getattr(self, field.name), Secret)]
        return secret_fields

    def _set_up_secret_fields(self, derived_class_type: type):
        secret_field_list = fields(derived_class_type)

        for field in secret_field_list:
            if field.type == Secret:
                secret_instance = getattr(self, field.name)
                if (secret_instance is None) or isinstance(secret_instance, Secret):
                    continue
                setattr(self, field.name, Secret(str(secret_instance)))


@dataclass
class EmbeddingConfig:
    dimension: int = None
    engine_type: EngineType = EngineType.LANGCHAIN
    index_type: IndexType = IndexType.FLATL2
    model_type: EmbeddingModelType = EmbeddingModelType.NONE
    model_name: str = None
    model_api_base: str = None
    model_api_version: str = None

    @staticmethod
    def is_field_empty(field_name: str, field_value: Any) -> bool:

        if field_value is None:
            return True

        if field_name == 'model_type':
            return field_value == EmbeddingModelType.NONE

        return False


@dataclass
class StorageConfig:
    storage_type: StorageType = StorageType.LOCAL
    local_store_path: str = None
    remote_store_path: str = None


@dataclass
class ExecutionConfig:
    store_identifier: Union[str, List[str]] = None
    local_cache_path: str = None
    create_if_not_exists: bool = False
    max_file_size: int = None
    auto_sync: bool = False
    embedding_funcion: Any = None
    secret_source_type: SecretSourceType = None
    akv_url: str = None
    credential: str = None


@dataclass
class LoggingConfig:
    log_handlers: List[logging.Handler] = None
    log_level: int = logging.CRITICAL + 1


@dataclass
class StoreCoreSecretsConfig(ConfigWithSecrets):
    blob_conn_str: Secret = None
    model_api_key: Secret = None


@dataclass
class StoreCoreConfig(StorageConfig, EmbeddingConfig, ExecutionConfig, LoggingConfig, StoreCoreSecretsConfig):

    store_name: str = None

    @classmethod
    def create_config(
        cls,
        store_identifier: Union[str, List[str]],
        dimension: int = None,
        storage_type: StorageType = StorageType.LOCAL,
        local_cache_path: str = None,
        engine_type: EngineType = EngineType.LANGCHAIN,
        index_type: IndexType = IndexType.FLATL2,
        model_type: EmbeddingModelType = EmbeddingModelType.NONE,
        model_name: str = None,
        model_api_base: str = None,
        model_api_version: str = None,
        auto_sync: bool = False,
        embedding_function: Any = None,
        secret_source_type: SecretSourceType = SecretSourceType.PLAIN,
        akv_url: str = None,
        credential: str = None,
        max_file_size: int = None,
        create_if_not_exists: bool = False,
        blob_conn_str: str = None,
        model_api_key: str = None,
        log_handlers: List[logging.Handler] = None,
        log_level: int = logging.CRITICAL + 1
    ):
        config = cls()

        config.dimension = dimension
        config.engine_type = engine_type
        config.index_type = index_type
        config.model_type = model_type
        config.model_name = model_name
        config.model_api_base = model_api_base
        config.model_api_version = model_api_version

        config.storage_type = storage_type

        config.store_identifier = store_identifier
        config.local_cache_path = local_cache_path
        config.create_if_not_exists = create_if_not_exists
        config.max_file_size = max_file_size
        config.auto_sync = auto_sync
        config.embedding_funcion = embedding_function
        config.akv_url = akv_url
        config.credential = credential

        config.secret_source_type = secret_source_type

        if blob_conn_str is not None:
            config.blob_conn_str = Secret(blob_conn_str)
        if model_api_key is not None:
            config.model_api_key = Secret(model_api_key)

        config.log_handlers = log_handlers
        config.log_level = log_level

        config.parse_store_identifier()

        return config

    @classmethod
    def from_dict(cls, dict_obj: dict):

        config = cls(**dict_obj)
        config._set_up_secret_fields(StoreCoreSecretsConfig)
        config.parse_store_identifier()

        return config

    def parse_store_identifier(self):
        if (
            self.storage_type == StorageType.INMEMORY
            or isinstance(self.store_identifier, List)
        ):
            return
        if self.storage_type == StorageType.LOCAL:
            self.local_store_path = self.store_identifier
            self.store_name = self.get_store_name(self.store_identifier, self.storage_type)
        elif self.storage_type.is_remote_file_based:
            self.remote_store_path = self.store_identifier
            self.store_name = self.get_store_name(self.store_identifier, self.storage_type)
            if self.local_cache_path is None:
                self.local_cache_path = os.getcwd()
            self.local_store_path = IdentifierConverter.map_url_to_local_path(
                self.local_cache_path,
                self.remote_store_path,
                self.store_name
            )
        else:
            return

    @staticmethod
    def get_store_name(store_identifier: str, storage_type: StorageType) -> str:
        if storage_type == StorageType.INMEMORY:
            return FileNames.DEFAULT_EMBEDDINGSTORE_NAME
        else:
            return os.path.basename(os.path.normpath(store_identifier))
