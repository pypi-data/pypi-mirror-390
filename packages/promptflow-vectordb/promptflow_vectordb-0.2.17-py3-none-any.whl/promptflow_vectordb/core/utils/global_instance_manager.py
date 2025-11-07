import threading
from typing import Dict, Any
from abc import abstractmethod

from .singleton_meta import SingletonMeta


class GlobalInstanceManager(metaclass=SingletonMeta):

    __instances: Dict[Any, Any] = {}
    __lock = threading.Lock()

    @abstractmethod
    def get_instance(self, **kwargs) -> Any:
        pass

    @abstractmethod
    def _create_instance(self, **kwargs) -> Any:
        pass

    def _get_instance(
        self,
        identifier: Any,
        **kwargs
    ) -> Any:
        if identifier in self.__instances:
            return self.__instances[identifier]
        with self.__lock:
            if identifier in self.__instances:
                return self.__instances[identifier]

            instance = self._create_instance(**kwargs)

            self.__instances[identifier] = instance
            return instance
