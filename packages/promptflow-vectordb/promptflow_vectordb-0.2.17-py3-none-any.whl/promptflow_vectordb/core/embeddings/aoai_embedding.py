from typing import List

import openai
from openai import AzureOpenAI
from .embedding import Embedding
from ..contracts import StoreCoreConfig
from ..utils.retry_utils import retry_and_handle_exceptions


def extract_delay_from_rate_limit_error_msg(text):
    import re
    pattern = r'retry after (\d+)'
    match = re.search(pattern, text)
    if match:
        retry_time_from_message = match.group(1)
        return float(retry_time_from_message)
    else:
        return None


class AOAIEmbedding(Embedding):

    @retry_and_handle_exceptions(
        exception_to_check=openai.RateLimitError,
        max_retries=5,
        extract_delay_from_error_message=extract_delay_from_rate_limit_error_msg)
    def embed(self, text: str) -> List[float]:
        client = AzureOpenAI(
            api_version=self.__config.model_api_version,
            api_key=self.__config.model_api_key.get_value() if self.__config.model_api_key else None,
            azure_endpoint=self.__config.model_api_base
        )
        return client.embeddings.create(
            input=text,
            model=self.__config.model_name).data[0].embedding

    def __init__(self, config: StoreCoreConfig):
        self.__config = config
