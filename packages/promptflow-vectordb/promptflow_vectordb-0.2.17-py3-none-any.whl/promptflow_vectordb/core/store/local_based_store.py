import json
import os
from typing import Iterable, List, Optional

from .store import (
    UnsupportedStoreOperationException,
    IndexFileSizeExceededException
)
from .in_memory_store import InMemoryStore
from ..contracts import StoreCoreConfig, EmbeddingConfig, SearchResultEntity
from ..contracts import FileNames, StoreCoreEventNames
from ..contracts.exceptions import FileNotFoundException
from ..logging.utils import LoggingUtils


class LocalStoreFileNotFoundException(FileNotFoundException):
    pass


class LocalBasedStore(InMemoryStore):

    def batch_insert_texts(self, texts: Iterable[str], metadatas: Optional[List[dict]] = None) -> None:
        super().batch_insert_texts(texts, metadatas)
        self.__dump_data_and_index()

    def batch_insert_texts_with_embeddings(
            self,
            texts: Iterable[str],
            embeddings: Iterable[List[float]],
            metadatas: Optional[List[dict]] = None) -> None:
        super().batch_insert_texts_with_embeddings(texts, embeddings, metadatas)
        self.__dump_data_and_index()

    def search_by_text(self, query_text: str, top_k: int = 5) -> List[SearchResultEntity]:
        return super().search_by_text(query_text, top_k)

    def search_by_embedding(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResultEntity]:
        return super().search_by_embedding(query_embedding, top_k)

    def merge_from(self, other_store: 'LocalBasedStore'):
        raise UnsupportedStoreOperationException(
            'merge is not supported for local based store'
        )

    def clear(self):
        super().clear()

    def save(self):
        super().save()
        self.__dump_data_and_index()
        self.__dump_embedding_config()

    def __init__(self, config: StoreCoreConfig):

        self.__config = config
        self.__logger = LoggingUtils.sdk_logger(__package__, self.__config)
        self.__embedding_config_file_path = os.path.join(
            self.__config.local_store_path, FileNames.EMBEDDING_CONFIG_FILE_NAME)

        self.__create_if_not_exists()
        self.__load_and_update_embedding_config()

        super().__init__(config)

        if self.__config.max_file_size is not None:
            if self._engine.get_store_files_size(self.__config.local_store_path) > self.__config.max_file_size:
                error_msg = (f"index files at local path {config.local_store_path}"
                             f"exceed the max allowed file size {self.__config.max_file_size}")
                raise IndexFileSizeExceededException(error_msg)

        self.__load_data_and_index()

    def __create_if_not_exists(self):

        if not os.path.exists(self.__config.local_store_path):
            if self.__config.create_if_not_exists:
                os.makedirs(self.__config.local_store_path)
                self.__dump_embedding_config()
            else:
                error_msg = f'store: {self.__config.store_name} not found at path {self.__config.local_store_path}'
                self.__logger.error(error_msg)
                raise LocalStoreFileNotFoundException(error_msg)
        elif self.__config.create_if_not_exists:
            self.__logger.warning(
                f'store: {self.__config.store_name} already exists at path {self.__config.local_store_path}')

        if (
            not os.path.exists(self.__embedding_config_file_path)
            or self.__config.create_if_not_exists
        ):
            self.__dump_embedding_config()

    @LoggingUtils.log_event(__package__, StoreCoreEventNames.DUMP_INDEX)
    def __dump_data_and_index(self):
        self._engine.save_data_index_to_disk(self.__config.local_store_path)

    @LoggingUtils.log_event(__package__, StoreCoreEventNames.LOAD_INDEX)
    def __load_data_and_index(self):
        self._engine.load_data_index_from_disk(self.__config.local_store_path)

    @LoggingUtils.log_event(__package__, StoreCoreEventNames.LOAD_CONFIG)
    def __load_and_update_embedding_config(self):
        with open(self.__embedding_config_file_path, "r") as f:
            embedding_config = json.load(f)
            update_embedding_config = False
            for key, on_file_value in embedding_config.items():
                if key in EmbeddingConfig.__dataclass_fields__.keys():
                    assigned_value = getattr(self.__config, key)
                    if (
                        (not EmbeddingConfig.is_field_empty(key, on_file_value))
                        and (EmbeddingConfig.is_field_empty(key, assigned_value))
                    ):
                        setattr(self.__config, key, on_file_value)
                    if (
                        (not EmbeddingConfig.is_field_empty(key, assigned_value))
                        and (assigned_value != on_file_value)
                    ):
                        update_embedding_config = True

            if update_embedding_config:
                self.__dump_embedding_config()

    @LoggingUtils.log_event(__package__, StoreCoreEventNames.DUMP_CONFIG)
    def __dump_embedding_config(self):
        embedding_config = {
            k: v for k, v in self.__config.__dict__.items()
            if k in EmbeddingConfig.__dataclass_fields__.keys()
        }
        with open(self.__embedding_config_file_path, "w") as f:
            f.write(json.dumps(embedding_config))
