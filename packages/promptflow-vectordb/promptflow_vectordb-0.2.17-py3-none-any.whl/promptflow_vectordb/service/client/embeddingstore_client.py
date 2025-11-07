from typing import List
import logging

from ...core.contracts import StorageType, SearchResultEntity, SecretSourceType
from ...core.contracts import StoreStage, StoreOperation
from ...core.utils.secret_manager import SecretManager
from ...core.logging.utils import LoggingUtils
from ..contracts import StoreServiceConfig, AgentType, StoreServiceEventNames, StoreServiceCustomDimensions
from .agent import AgentFactory, Agent


class EmbeddingStoreClient:

    def __init__(self, config: StoreServiceConfig):
        self.__logger = LoggingUtils.sdk_logger(__package__, config)
        self.__agent: Agent = None

        scope_context = {
            StoreServiceCustomDimensions.STORAGE_TYPE: config.storage_type,
            StoreServiceCustomDimensions.INDEX_TYPE: config.index_type,
            StoreServiceCustomDimensions.ENGINE_TYPE: config.engine_type,
            StoreServiceCustomDimensions.MODEL_TYPE: config.model_type,
            StoreServiceCustomDimensions.SECRET_SOURCE_TYPE: config.secret_source_type,
            StoreServiceCustomDimensions.AGENT_TYPE: config.agent_type
        }

        @LoggingUtils.log_event(
            package_name=__package__,
            event_name=StoreServiceEventNames.INIT,
            scope_context=scope_context,
            store_stage=StoreStage.INITIALIZATION,
            logger=self.__logger
        )
        def do_init():
            secret_manager = SecretManager(config)
            secret_manager.resolve_secrets(config)
            self.__agent = AgentFactory.get_agent(config)

        do_init()

    @classmethod
    def get_store(
        cls,
        store_identifier: str,
        storage_type: StorageType = StorageType.LOCAL,
        agent_type: AgentType = AgentType.FILEBASED,
        host: str = None,
        port: str = None,
        local_cache_path: str = None,
        akv_url: str = None,
        secret_source_type: SecretSourceType = SecretSourceType.PLAIN,
        blob_conn_str: str = None,
        credential: str = None,
        search_agent_api_key: str = None,
        max_file_size: int = None,
        log_handlers: List[logging.Handler] = None,
        log_level: int = logging.CRITICAL + 1
    ):
        config = StoreServiceConfig.create_config(
            store_identifier=store_identifier,
            storage_type=storage_type,
            agent_type=agent_type,
            host=host,
            port=port,
            local_cache_path=local_cache_path,
            akv_url=akv_url,
            secret_source_type=secret_source_type,
            blob_conn_str=blob_conn_str,
            credential=credential,
            search_agent_api_key=search_agent_api_key,
            max_file_size=max_file_size,
            create_if_not_exists=False,
            log_handlers=log_handlers,
            log_level=log_level
        )

        return cls(config)

    @LoggingUtils.log_event(
        package_name=__package__,
        event_name=StoreServiceEventNames.LOAD,
        store_stage=StoreStage.INITIALIZATION
    )
    def load(self):
        self.__agent.load()

    @LoggingUtils.log_event(
        package_name=__package__,
        event_name=StoreServiceEventNames.SEARCH_BY_EMBEDDING,
        store_stage=StoreStage.SEARVING,
        store_operation=StoreOperation.SEARCH
    )
    def search_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        collection: str = None,
        text_field: str = None,
        vector_field: str = None,
        search_params: dict = None,
        search_filters: dict = None,
        output_fields: List[str] = None
    ) -> List[SearchResultEntity]:
        return self.__agent.search_by_embedding(
            query_embedding=query_embedding,
            top_k=top_k,
            collection=collection,
            text_field=text_field,
            vector_field=vector_field,
            search_params=search_params,
            search_filters=search_filters,
            output_fields=output_fields
        )
