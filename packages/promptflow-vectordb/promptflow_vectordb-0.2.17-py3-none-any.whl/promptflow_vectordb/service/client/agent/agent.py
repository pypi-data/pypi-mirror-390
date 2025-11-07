from abc import ABC, abstractmethod
from typing import List

from ....core.contracts import SearchResultEntity


class Agent(ABC):

    @abstractmethod
    def load(self, store_identifier: str, storage_type: str):
        pass

    @abstractmethod
    def search_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        **kwargs
    ) -> List[SearchResultEntity]:
        pass

    @abstractmethod
    def clear(self):
        pass
