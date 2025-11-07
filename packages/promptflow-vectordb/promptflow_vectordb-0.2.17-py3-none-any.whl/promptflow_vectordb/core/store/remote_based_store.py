import os
from typing import Iterable, List, Optional

from .store import (
    UnsupportedStoreOperationException,
    IndexFileSizeExceededException
)
from .local_based_store import LocalBasedStore
from ..contracts import StoreCoreConfig, SearchResultEntity
from ..contracts import FileNames, StoreCoreEventNames
from ..contracts.exceptions import FileNotFoundException
from ..remote_client import RemoteClientFactory
from ..engine import EngineFactory
from ..logging.utils import LoggingUtils


class RemoteStoreFileNotFountException(FileNotFoundException):
    pass


class RemoteBasedStore(LocalBasedStore):

    def batch_insert_texts(self, texts: Iterable[str], metadatas: Optional[List[dict]] = None) -> None:
        super().batch_insert_texts(texts, metadatas)
        self.__upload_to_remote()

    def batch_insert_texts_with_embeddings(self,
                                           texts: Iterable[str],
                                           embeddings: Iterable[List[float]],
                                           metadatas: Optional[List[dict]] = None) -> None:
        super().batch_insert_texts_with_embeddings(texts, embeddings, metadatas)
        self.__upload_to_remote()

    def search_by_text(self, query_text: str, top_k: int = 5) -> List[SearchResultEntity]:
        return super().search_by_text(query_text, top_k)

    def search_by_embedding(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResultEntity]:
        return super().search_by_embedding(query_embedding, top_k)

    def merge_from(self, other_store: 'RemoteBasedStore'):
        raise UnsupportedStoreOperationException(
            'merge is not supported for remote based store'
        )

    def clear(self):
        super().clear()

    def save(self):
        super().save()
        self.__remote_client.upload()

    def __init__(self, config: StoreCoreConfig):
        self.__config = config
        self.__logger = LoggingUtils.sdk_logger(__package__, self.__config)
        self.__remote_client = RemoteClientFactory.get_remote_client(
            config=self.__config,
            file_relative_paths=[
                EngineFactory.get_index_file_relative_path(self.__config),
                EngineFactory.get_data_file_relative_path(self.__config),
            ]
        )

        if self.__remote_client.if_folder_exists():
            if self.__config.max_file_size is not None:
                remote_store_file_size = self.__remote_client.get_remote_store_files_size()
                if remote_store_file_size is not None and remote_store_file_size > self.__config.max_file_size:
                    error_msg = (f"index files at remote path {config.remote_store_path}"
                                 f"exceed the max allowed file size {self.__config.max_file_size}")
                    raise IndexFileSizeExceededException(error_msg)
            self.__sync_to_local()
            if self.__config.max_file_size is not None:
                downloaded_store_files_size = self.__remote_client.get_downloaded_store_files_size()
                if downloaded_store_files_size > self.__config.max_file_size:
                    error_msg = (f"index files downloaded at path {config.local_store_path}"
                                 f"exceed the max allowed file size {self.__config.max_file_size}")
                    raise IndexFileSizeExceededException(error_msg)
        elif not self.__config.create_if_not_exists:
            raise RemoteStoreFileNotFountException(
                f'store: {self.__config.store_name} not found at path {self.__config.remote_store_path}')

        super().__init__(config)

    def __sync_to_local(self):
        index_file_relative_path = EngineFactory.get_index_file_relative_path(self.__config)
        self.__local_etag_file_path = os.path.join(self.__config.local_store_path, FileNames.LOCAL_ETAG_FILE_NAME)
        remote_etag = self.__remote_client.get_etag(index_file_relative_path)
        local_etag = self.__get_local_etag()

        if remote_etag != local_etag:

            self.__logger.telemetry_event_started(
                StoreCoreEventNames.DOWNLOAD_INDEX
            )

            self.__remote_client.download()

            self.__logger.telemetry_event_completed(
                StoreCoreEventNames.DOWNLOAD_INDEX
            )

            self.__save_to_local_etag(remote_etag)

    @LoggingUtils.log_event(__package__, StoreCoreEventNames.UPLOAD_INDEX)
    def __upload_to_remote(self):
        self.__remote_client.upload()

    def __get_local_etag(self):
        if os.path.exists(self.__local_etag_file_path):
            with open(self.__local_etag_file_path, "r") as f:
                return f.read()

    def __save_to_local_etag(self, etag: str):
        with open(self.__local_etag_file_path, 'w') as f:
            f.write(etag)
