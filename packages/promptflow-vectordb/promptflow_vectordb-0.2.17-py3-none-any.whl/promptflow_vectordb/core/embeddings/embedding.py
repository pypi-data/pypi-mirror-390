from abc import ABC, abstractmethod
from typing import List


class Embedding(ABC):

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass
