import logging
import copy
from typing import Iterable, List, Optional, Union, Any

from .store import StoreFactory, Store
from .contracts import StoreCoreConfig, SearchResultEntity
from .contracts import StoreCoreEventNames, StoreCoreEventCustomDimensions
from .contracts import StoreStage, StoreOperation
from .contracts import StorageType, IndexType, EngineType, EmbeddingModelType, SecretSourceType
from .utils.secret_manager import SecretManager
from .logging.utils import LoggingUtils


class EmbeddingStoreCore:

    def __init__(self, config: StoreCoreConfig):
        self.__logger = LoggingUtils.sdk_logger(__package__, config)
        self.__store: Store = None

        is_merged_store = False
        if isinstance(config.store_identifier, List):
            is_merged_store = True

        scope_context = {
            StoreCoreEventCustomDimensions.STORAGE_TYPE: config.storage_type,
            StoreCoreEventCustomDimensions.INDEX_TYPE: config.index_type,
            StoreCoreEventCustomDimensions.ENGINE_TYPE: config.engine_type,
            StoreCoreEventCustomDimensions.MODEL_TYPE: config.model_type,
            StoreCoreEventCustomDimensions.SECRET_SOURCE_TYPE: config.secret_source_type,
            StoreCoreEventCustomDimensions.IS_MERGED_STORE: str(is_merged_store)
        }

        @LoggingUtils.log_event(
            package_name=__package__,
            event_name=StoreCoreEventNames.INIT,
            scope_context=scope_context,
            store_stage=StoreStage.INITIALIZATION,
            logger=self.__logger
        )
        def do_init():
            secret_manager = SecretManager(config)
            secret_manager.resolve_secrets(config)

            if not is_merged_store:
                self.__store = StoreFactory.get_store(config)
            else:
                merged_store_config = copy.deepcopy(config)
                merged_store_config.storage_type = StorageType.INMEMORY
                self.__store = StoreFactory.get_store(merged_store_config)
                for store_identifier in config.store_identifier:
                    store_config = copy.deepcopy(config)
                    store_config.store_identifier = store_identifier
                    store_config.parse_store_identifier()
                    store = StoreFactory.get_store(store_config)
                    self.__store.merge_from(store)

        do_init()

    @classmethod
    def create_store(
        cls,
        store_identifier: str,
        dimension: int,
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
        blob_conn_str: str = None,
        model_api_key: str = None,
        log_handlers: List[logging.Handler] = None,
        log_level: int = logging.CRITICAL + 1
    ):
        config = StoreCoreConfig.create_config(
            store_identifier=store_identifier,
            dimension=dimension,
            storage_type=storage_type,
            local_cache_path=local_cache_path,
            engine_type=engine_type,
            index_type=index_type,
            model_type=model_type,
            model_name=model_name,
            model_api_base=model_api_base,
            model_api_version=model_api_version,
            auto_sync=auto_sync,
            embedding_function=embedding_function,
            secret_source_type=secret_source_type,
            akv_url=akv_url,
            credential=credential,
            max_file_size=max_file_size,
            create_if_not_exists=True,
            blob_conn_str=blob_conn_str,
            model_api_key=model_api_key,
            log_handlers=log_handlers,
            log_level=log_level)

        return cls(config)

    @classmethod
    def get_store(
        cls,
        store_identifier: Union[str, List[str]],
        dimension: int = None,
        storage_type: StorageType = StorageType.LOCAL,
        local_cache_path=None,
        secret_source_type: SecretSourceType = SecretSourceType.PLAIN,
        akv_url=None,
        credential: str = None,
        max_file_size=None,
        blob_conn_str: str = None,
        model_api_key: str = None,
        log_handlers: List[logging.Handler] = None,
        log_level: int = logging.CRITICAL + 1
    ):
        config = StoreCoreConfig.create_config(
            store_identifier=store_identifier,
            dimension=dimension,
            storage_type=storage_type,
            local_cache_path=local_cache_path,
            secret_source_type=secret_source_type,
            akv_url=akv_url,
            credential=credential,
            max_file_size=max_file_size,
            create_if_not_exists=False,
            blob_conn_str=blob_conn_str,
            model_api_key=model_api_key,
            log_handlers=log_handlers,
            log_level=log_level)

        return cls(config)

    @LoggingUtils.log_event(
        package_name=__package__,
        event_name=StoreCoreEventNames.BATCH_INSERT_TEXTS,
        store_stage=StoreStage.SEARVING,
        store_operation=StoreOperation.INSERTION
    )
    def batch_insert_texts(self, texts: Iterable[str], metadatas: Optional[List[dict]] = None) -> None:
        self.__store.batch_insert_texts(texts, metadatas)

    @LoggingUtils.log_event(
        package_name=__package__,
        event_name=StoreCoreEventNames.BATCH_INSERT_TEXTS_WITH_EMBEDDINGS,
        store_stage=StoreStage.SEARVING,
        store_operation=StoreOperation.INSERTION
    )
    def batch_insert_texts_with_embeddings(
            self,
            texts: Iterable[str],
            embeddings: Iterable[List[float]],
            metadatas: Optional[List[dict]] = None) -> None:
        self.__store.batch_insert_texts_with_embeddings(texts, embeddings, metadatas)

    @LoggingUtils.log_event(
        package_name=__package__,
        event_name=StoreCoreEventNames.SEARCH_BY_TEXT,
        store_stage=StoreStage.SEARVING,
        store_operation=StoreOperation.SEARCH
    )
    def search_by_text(self, query_text: str, top_k: int = 5) -> List[SearchResultEntity]:
        return self.__store.search_by_text(query_text, top_k)

    @LoggingUtils.log_event(
        package_name=__package__,
        event_name=StoreCoreEventNames.SEARCH_BY_EMBEDDING,
        store_stage=StoreStage.SEARVING,
        store_operation=StoreOperation.SEARCH
    )
    def search_by_embedding(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResultEntity]:
        return self.__store.search_by_embedding(query_embedding, top_k)

    @LoggingUtils.log_event(
        package_name=__package__,
        event_name=StoreCoreEventNames.CLEAR,
        store_stage=StoreStage.SEARVING,
        store_operation=StoreOperation.CLEAR
    )
    def clear(self):
        self.__store.clear()

    @LoggingUtils.log_event(
        package_name=__package__,
        event_name=StoreCoreEventNames.SAVE,
        store_stage=StoreStage.SEARVING,
        store_operation=StoreOperation.SAVE
    )
    @LoggingUtils.log_event(__package__, StoreCoreEventNames.SAVE)
    def save(self):
        self.__store.save()
