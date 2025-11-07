from .embedding import Embedding
from ..contracts import StoreCoreConfig, EmbeddingModelType, LoggingMessageTemplate
from ..contracts.exceptions import UnsupportedFeatureException
from ..logging.utils import LoggingUtils


class UnsupportedEmbeddingModelTypeException(UnsupportedFeatureException):
    pass


class EmbeddingFactory:

    @staticmethod
    def get_embedding(config: StoreCoreConfig) -> Embedding:

        embedding: Embedding = None

        if config.model_type == EmbeddingModelType.AOAI:
            from .aoai_embedding import AOAIEmbedding
            embedding = AOAIEmbedding(config)
        elif config.model_type == EmbeddingModelType.OPENAI:
            from .openai_embedding import OpenAIEmbedding
            embedding = OpenAIEmbedding(config)
        elif config.model_type == EmbeddingModelType.CUSTOMIZED:
            from .customized_embedding import CustomizedEmbedding
            embedding = CustomizedEmbedding(config)
        elif config.model_type == EmbeddingModelType.NONE:
            from .empty_embedding import EmptyEmbedding
            embedding = EmptyEmbedding()
        else:
            raise UnsupportedEmbeddingModelTypeException(
                f"{config.model_type} has not been implemented yet."
            )

        LoggingUtils.sdk_logger(__package__, config).info(
            LoggingMessageTemplate.COMPONENT_INITIALIZED.format(
                component_name=Embedding.__name__,
                instance_type=embedding.__class__.__name__
            )
        )

        return embedding
