from typing import Iterable, List, Optional

from .store import Store
from ..contracts import StoreCoreConfig, SearchResultEntity
from ..utils.index_factory import IndexFactory
from ..engine import EngineFactory
from ..embeddings import EmbeddingFactory


class InMemoryStore(Store):

    def batch_insert_texts(self, texts: Iterable[str], metadatas: Optional[List[dict]] = None) -> None:
        self._engine.batch_insert_texts(texts, metadatas)

    def batch_insert_texts_with_embeddings(
            self,
            texts: Iterable[str],
            embeddings: Iterable[List[float]],
            metadatas: Optional[List[dict]] = None) -> None:
        self._engine.batch_insert_texts_with_embeddings(texts, embeddings, metadatas)

    def search_by_text(self, query_text: str, top_k: int = 5) -> List[SearchResultEntity]:
        return self._engine.search_by_text(query_text, top_k)

    def search_by_embedding(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResultEntity]:
        return self._engine.search_by_embedding(query_embedding, top_k)

    def merge_from(self, other_store: 'InMemoryStore'):
        self._engine.merge_from(other_store._engine)

    def clear(self):
        self._engine.clear()

    def save(self):
        pass

    def __init__(self, config: StoreCoreConfig):
        self.__config = config
        self.__init_engine()

    def __init_engine(self):
        index = IndexFactory.get_index(self.__config)
        embedding = EmbeddingFactory.get_embedding(self.__config)
        self._engine = EngineFactory.get_engine(self.__config, index, embedding)
