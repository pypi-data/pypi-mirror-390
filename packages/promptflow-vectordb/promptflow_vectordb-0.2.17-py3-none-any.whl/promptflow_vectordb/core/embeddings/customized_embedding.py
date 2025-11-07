from typing import List

from .embedding import Embedding
from ..contracts import StoreCoreConfig
from ..contracts.exceptions import MissingConfigException


class MissingCustomizedEmbeddingFunctionException(MissingConfigException):
    pass


class CustomizedEmbedding(Embedding):

    def embed(self, text: str) -> List[float]:
        if self.__customized_embed_func is None:
            raise MissingCustomizedEmbeddingFunctionException(
                'customized embedding function needs to be specified'
            )
        return self.__customized_embed_func(text)

    def __init__(self, config: StoreCoreConfig):
        self.__customized_embed_func = config.embedding_funcion
