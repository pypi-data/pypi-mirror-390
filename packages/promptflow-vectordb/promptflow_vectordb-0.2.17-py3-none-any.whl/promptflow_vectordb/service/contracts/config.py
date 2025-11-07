import logging
from typing import List, Any
from dataclasses import dataclass

from ...core.contracts import StoreCoreConfig, Secret, StoreCoreSecretsConfig
from ...core.contracts import StorageType, IndexType, EngineType, EmbeddingModelType, SecretSourceType
from .types import AgentType


@dataclass
class StoreServerConfig:
    host: str = None
    port: str = None
    search_agent_user: str = None


# @dataclass
# class SearchApiConfig:
    # collection: str = None  # for search engines, sub identifier for a store under the same endpoint.
    # text_field: str = None  # text field name in the response json from search engines
    # vector_field: str = None  # vector field name in the response json from search engines

    # search_params: dict = None  # additional params for making requests to search engines
    # search_filters: dict = None  # additional filters for making requests to search engines


@dataclass
class SearchAgentConfig:
    search_agent_api_version: str = None


@dataclass
class StoreServiceSecretsConfig(StoreCoreSecretsConfig):
    search_agent_api_key: Secret = None
    search_agent_password: Secret = None


@dataclass
class StoreServiceConfig(StoreCoreConfig, StoreServerConfig, StoreServiceSecretsConfig, SearchAgentConfig):

    agent_type: AgentType = AgentType.FILEBASED

    @classmethod
    def create_config(
        cls,
        store_identifier: str,
        dimension: int = None,
        storage_type: StorageType = StorageType.LOCAL,
        agent_type: AgentType = AgentType.FILEBASED,
        host: str = None,
        port: str = None,
        search_agent_api_key: str = None,
        search_agent_api_version: str = None,
        search_agent_user: str = None,
        search_agent_password: str = None,
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
        config.secret_source_type = secret_source_type
        config.akv_url = akv_url
        config.credential = credential

        config.log_handlers = log_handlers
        config.log_level = log_level

        config.agent_type = agent_type

        config.host = host
        config.port = port
        config.search_agent_user = search_agent_user

        config.search_agent_api_version = search_agent_api_version

        if blob_conn_str is not None:
            config.blob_conn_str = Secret(blob_conn_str)
        if model_api_key is not None:
            config.model_api_key = Secret(model_api_key)
        if search_agent_api_key is not None:
            config.search_agent_api_key = Secret(search_agent_api_key)
        if search_agent_password is not None:
            config.search_agent_password = Secret(search_agent_password)

        config.parse_store_identifier()

        return config

    @classmethod
    def from_dict(cls, dict_obj: dict):

        config = cls(**dict_obj)
        config._set_up_secret_fields(StoreServiceSecretsConfig)
        config.parse_store_identifier()

        return config
