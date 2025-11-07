from abc import ABC, abstractmethod, abstractstaticmethod
from typing import Iterable, List, Optional

from ..contracts import SearchResultEntity
from ..contracts.exceptions import InvalidInputException


class IndexInsertParametersMismatchException(InvalidInputException):
    pass


class Engine(ABC):

    @abstractmethod
    def batch_insert_texts(self, texts: Iterable[str], metadatas: Optional[List[dict]] = None) -> None:
        pass

    @abstractmethod
    def batch_insert_texts_with_embeddings(
            self,
            texts: Iterable[str],
            embeddings: Iterable[List[float]],
            metadatas: Optional[List[dict]] = None) -> None:
        pass

    @abstractmethod
    def search_by_text(self, query_text: str, top_k: int = 5) -> List[SearchResultEntity]:
        pass

    @abstractmethod
    def search_by_embedding(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResultEntity]:
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def merge_from(self, other_engine: 'Engine'):
        pass

    @abstractmethod
    def load_data_index_from_disk(self, path: str):
        pass

    @abstractmethod
    def save_data_index_to_disk(self, path: str):
        pass

    @abstractmethod
    def get_store_files_size(self, path: str) -> int:
        pass

    @abstractstaticmethod
    def get_index_file_relative_path():
        pass

    @abstractstaticmethod
    def get_data_file_relative_path():
        pass
