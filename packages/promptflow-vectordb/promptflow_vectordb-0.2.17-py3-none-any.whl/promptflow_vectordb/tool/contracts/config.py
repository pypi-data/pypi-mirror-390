import os
import logging
from dataclasses import dataclass, fields

from .constants import EnvNames
from .types import StoreType
from ..utils.pf_runtime_utils import PromptflowRuntimeUtils
from ...service.contracts import StoreServiceConfig, AgentType
from ...core.contracts import StorageType, SecretSourceType
from ...core.contracts.config import LoggingConfig


@dataclass
class VectorSearchToolConfig:

    store_type: StoreType = StoreType.LOCALFAISS

    # for Local Faiss and ML Index
    store_path: str = None

    # for all non-local source types
    url: str = None  # might be blob url, search engine endpoint
    api_version: str = None  # api version for search engine
    secret: str = None  # secret for auth the store connection, might be blob conn str, search engine api key

    logging_config: LoggingConfig = None

    def generate_store_service_config(self) -> StoreServiceConfig:

        is_rest_service_ready = self.get_is_rest_service_enabled()

        store_identifier = None
        blob_conn_str = None
        credential = None
        search_agent_api_key = None
        search_agent_api_version = None

        if self.store_type == StoreType.LOCALFAISS:
            store_identifier = self.store_path
        else:
            store_identifier = self.url
            if self.store_type == StoreType.BLOBFAISS:
                blob_conn_str = self.secret
                credential = PromptflowRuntimeUtils.get_credential_if_blob_is_on_workspace_default_storage(
                    blob_url=store_identifier
                )
            elif self.store_type.is_db_service_based:
                search_agent_api_key = self.secret
                search_agent_api_version = self.api_version

        log_handlers = None
        log_level = logging.CRITICAL + 1

        if self.logging_config:
            log_handlers = self.logging_config.log_handlers
            log_level = self.logging_config.log_level

        store_service_config = StoreServiceConfig.create_config(
            store_identifier=store_identifier,
            storage_type=self.get_storage_type(self.store_type),
            agent_type=self.get_agent_type(self.store_type, is_rest_service_ready),
            host=self.get_host(),
            port=self.get_port(),
            search_agent_api_key=search_agent_api_key,
            search_agent_api_version=search_agent_api_version,
            local_cache_path=self.get_local_cache_path(),
            secret_source_type=SecretSourceType.PLAIN,
            blob_conn_str=blob_conn_str,
            credential=credential,
            log_handlers=log_handlers,
            log_level=log_level
        )

        return store_service_config

    def update_from_dict(self, dict_obj: dict):

        field_names = {field.name for field in fields(VectorSearchToolConfig)}
        for field_name, field_value in dict_obj.items():
            if field_name in field_names:
                setattr(self, field_name, field_value)

    @staticmethod
    def get_host() -> str:

        if EnvNames.HOST in os.environ:
            return os.environ[EnvNames.HOST]

        return "http://localhost"

    @staticmethod
    def get_port() -> str:

        if EnvNames.PORT in os.environ:
            return os.environ[EnvNames.PORT]

        return None

    @staticmethod
    def get_is_rest_service_enabled() -> bool:

        if EnvNames.IS_REST_SERVICE_ENABLED in os.environ and os.environ[EnvNames.IS_REST_SERVICE_ENABLED] == "true":
            return True

        return False

    @staticmethod
    def get_local_cache_path() -> str:

        if EnvNames.LOCAL_CACHE_PATH in os.environ:
            return os.environ[EnvNames.LOCAL_CACHE_PATH]

        return None

    @staticmethod
    def get_storage_type(store_type: StoreType) -> StorageType:

        if store_type == StoreType.LOCALFAISS:
            return StorageType.LOCAL
        elif store_type == StoreType.BLOBFAISS:
            return StorageType.BLOBSTORAGE
        elif store_type == StoreType.AMLDATASTOREFAISS:
            return StorageType.AMLDATASTORE
        elif store_type == StoreType.GITHUBFAISS:
            return StorageType.GITHUBFOLDER
        elif store_type == StoreType.HTTPFAISS:
            return StorageType.HTTP
        elif store_type.is_db_service_based:
            return StorageType.DBSERVICE
        else:
            return None

    @staticmethod
    def get_agent_type(store_type: StoreType, is_rest_service_ready: bool) -> AgentType:

        if store_type.is_file_based:
            if is_rest_service_ready:
                return AgentType.RESTCLIENTBASED
            return AgentType.FILEBASED
        elif store_type == StoreType.COGNITIVESEARCH:
            return AgentType.COGNITIVESEARCHBASED
        elif store_type == StoreType.QDRANT:
            return AgentType.QDRANTBASED
        elif store_type == StoreType.WEAVIATE:
            return AgentType.WEAVIATEBASED
        elif store_type == StoreType.PINECONE:
            return AgentType.PINECONECLIENTBASED

        return None
