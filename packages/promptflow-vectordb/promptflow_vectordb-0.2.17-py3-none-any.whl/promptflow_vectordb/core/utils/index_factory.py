import faiss

from ..contracts import EmbeddingConfig
from ..contracts import IndexType
from ..contracts.exceptions import UnsupportedFeatureException


class UnsupportedIndexTypeException(UnsupportedFeatureException):
    pass


class IndexFactory:

    @staticmethod
    def get_index(config: EmbeddingConfig) -> faiss.Index:
        if config.index_type == IndexType.FLATL2:
            if config.dimension is None:
                return faiss.IndexFlatL2()
            return faiss.IndexFlatL2(config.dimension)
        else:
            raise UnsupportedIndexTypeException(
                f"{config.index_type} has not been implemented yet."
            )
