import requests
import urllib3
from urllib import parse
from typing import List
from http import HTTPStatus
from ....core.logging.utils import LoggingUtils
from ....core.contracts import SearchResultEntity
from ...contracts import StoreServiceConfig
from ...contracts.request_obj import MilvusSearchRequestObj
from ...contracts.errors import EmbeddingSearchRetryableError, HttpRetryableStatusCodes
from .agent import Agent


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
api_key_header_name = "Api-Key"

QUERY_RESPONSE_SUCCESS_CODE = 200
QUERY_RESPONSE_CODE = 'code'
QUERY_RESPONSE_DATA = 'data'
QUERY_RESPONSE_MESSAGE = 'message'

QUERY_RESPONSE_DATA_DISTANCE = 'distance'
QUERY_RESPONSE_DATA_ID = 'id'


class MilvusClient(Agent):
    def __init__(self, config: StoreServiceConfig):
        self.__logger = LoggingUtils.sdk_logger(__package__, config)
        self.__config = config
        self.__init_and_validate_store_identifier()

    def search_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        collection: str = None,
        text_field: str = None,
        vector_field: str = None,
        search_params: dict = None,
        search_filters: dict = None,
        output_fields: List[str] = None
    ) -> List[SearchResultEntity]:
        if collection is None or collection == "":
            raise Exception("Empty collection name provided")
        if vector_field is None or vector_field == "":
            raise Exception("Empty vector field provided")

        token = f"{self.__config.search_agent_user}:{self.__config.search_agent_password.get_value()}"
        auth_header = {"Authorization": f"Bearer {token}"}
        request_obj = MilvusSearchRequestObj(collectionName=collection,
                                             limit=top_k,
                                             vector=query_embedding,
                                             outputFields=output_fields)
        request_obj.update(search_params)
        request_obj.update(search_filters)  # such as  dict "filter": "word_count > 0"
        query_result_dict = self.__milvus_query(auth_header, request_obj.as_dict())

        matched_vectors = {}
        results = []
        if query_result_dict[QUERY_RESPONSE_CODE] is QUERY_RESPONSE_SUCCESS_CODE:
            matched_vectors = query_result_dict[QUERY_RESPONSE_DATA]
            for matched_vector in matched_vectors:
                result = SearchResultEntity(score=matched_vector[QUERY_RESPONSE_DATA_DISTANCE],
                                            original_entity=matched_vector,
                                            # The vector_field should be contained in outputFields
                                            vector=matched_vector[vector_field]
                                            )
                # Notes: text_field is the result string,
                # and query_embedding is the embedding of the customer's input question
                if text_field in matched_vector.keys():
                    result.text = matched_vector[text_field]
                else:
                    self.__logger.info("Milvus vector text is recommended to be "
                                       "provided in vector metadata with key {0}, "
                                       "currently it's empty.".format(text_field))
                results.append(result)
        return results

    def load(self):
        return

    def clear(self):
        return

    def __init_and_validate_store_identifier(self):
        if (
            (self.__config.store_identifier is None)
            or (self.__config.store_identifier == "")
        ):
            raise Exception("Empty milvus store_identifier provided")
        self.base_url = self.__config.store_identifier
        self.query_url = parse.urljoin(self.base_url, "/v1/vector/search")

    def __milvus_query(self,
                       headers: dict,
                       query_body: dict) -> dict:
        try:
            query_response = requests.post(url=self.query_url, headers=headers, json=query_body)
            if query_response.status_code in HttpRetryableStatusCodes:
                raise EmbeddingSearchRetryableError(query_response.text)
            elif query_response.status_code != HTTPStatus.OK:
                raise Exception(query_response.text)
            elif query_response.text == "":
                raise Exception("Milvus query request returned 200, but response is empty")
            return query_response.json()
        except EmbeddingSearchRetryableError as e:
            raise e
        except Exception as e:
            raise Exception("Milvus query request failed with error: {0}".format(e)) from e
