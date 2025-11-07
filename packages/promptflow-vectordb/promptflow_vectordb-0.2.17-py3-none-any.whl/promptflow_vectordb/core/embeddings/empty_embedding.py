from typing import List

from .embedding import Embedding
from ..contracts.exceptions import MissingConfigException


class MissingEmbeddingFunctionException(MissingConfigException):
    pass


class EmptyEmbedding(Embedding):

    def embed(self, text: str) -> List[float]:
        raise MissingEmbeddingFunctionException(
            'built-in embedding model or customized embedding function need to be specified'
        )

    def __init__(self):
        return
