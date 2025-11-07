from typing import List

import openai
from openai import OpenAI
from .embedding import Embedding
from ..contracts import StoreCoreConfig
from ..utils.retry_utils import retry_and_handle_exceptions


class OpenAIEmbedding(Embedding):

    @retry_and_handle_exceptions(
        exception_to_check=openai.RateLimitError,
        max_retries=5)
    def embed(self, text: str) -> List[float]:
        client = OpenAI(
            api_key=self.__config.model_api_key.get_value() if self.__config.model_api_key else None,
            base_url=self.__config.model_api_base
        )
        return client.embeddings.create(
            input=text,
            model=self.__config.model_name).data[0].embedding

    def __init__(self, config: StoreCoreConfig):
        self.__config = config
