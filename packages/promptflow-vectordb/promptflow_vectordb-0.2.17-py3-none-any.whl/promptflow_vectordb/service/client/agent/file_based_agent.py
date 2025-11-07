from typing import List

from ....core.embeddingstore_core import EmbeddingStoreCore
from ....core.contracts import SearchResultEntity
from ...contracts import StoreServiceConfig
from .agent import Agent


class FileBasedAgent(Agent):

    def __init__(self, config: StoreServiceConfig):
        self.__config = config
        self.__store = None

    def load(self):
        self.__store = EmbeddingStoreCore(self.__config)

    def search_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        **kwargs
    ) -> List[SearchResultEntity]:
        if self.__store is None:
            self.load()
        return self.__store.search_by_embedding(query_embedding, top_k)

    def clear(self):
        self.__store = None
