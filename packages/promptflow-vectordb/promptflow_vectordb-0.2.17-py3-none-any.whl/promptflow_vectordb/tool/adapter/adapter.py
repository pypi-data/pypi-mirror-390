from abc import ABC, abstractmethod
from typing import List, Union


class Adapter(ABC):

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def search(
        self,
        query: Union[List[float], str],
        top_k: int = 5,
        **kwargs
    ) -> List[dict]:
        pass
