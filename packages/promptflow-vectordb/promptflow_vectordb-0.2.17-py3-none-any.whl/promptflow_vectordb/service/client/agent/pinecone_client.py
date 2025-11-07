import requests
import urllib3
from urllib import parse
from typing import List
from http import HTTPStatus
from ....core.logging.utils import LoggingUtils
from ....core.contracts import SearchResultEntity
from ...contracts import StoreServiceConfig
from ...contracts.request_obj import PineconeSearchRequestObj
from ...contracts.errors import EmbeddingSearchRetryableError, HttpRetryableStatusCodes
from .agent import Agent

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
namespace_param_identifier = "namespace"
api_key_header_name = "Api-Key"
query_response_matches_key = 'matches'
query_response_score_key = 'score'
query_response_metadata_key = 'metadata'
query_response_values_key = 'values'


class PineconeClient(Agent):
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
        output_fields: List[str] = None,
    ) -> List[SearchResultEntity]:
        auth_header = {api_key_header_name: self.__config.search_agent_api_key.get_value()}
        request_obj = PineconeSearchRequestObj(vector=query_embedding,
                                               topK=top_k,
                                               namespace=self.__get_namespace(collection),
                                               includeValues=True,
                                               includeMetadata=True)
        request_obj.update(search_params)
        request_obj.update(search_filters)
        query_result_dict = self.__pinecone_query(auth_header, request_obj.as_dict())
        matched_vectors = {}
        if query_response_matches_key in query_result_dict:
            matched_vectors = query_result_dict[query_response_matches_key]

        results = []
        for matched_vector in matched_vectors:
            result = SearchResultEntity(score=matched_vector[query_response_score_key],
                                        original_entity=matched_vector,
                                        metadata=matched_vector[query_response_metadata_key],
                                        vector=matched_vector[query_response_values_key])
            if text_field in matched_vector[query_response_metadata_key]:
                result.text = matched_vector[query_response_metadata_key][text_field]
            else:
                self.__logger.info("Pinecone vector text is recommended to be provided in vector metadata with key {0},"
                                   " currently it's empty.".format(text_field))
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
            raise Exception("Empty pinecone store_identifier provided")
        self.base_url = self.__config.store_identifier
        # add query url path
        self.query_url = parse.urljoin(self.base_url, "/query")

    def __get_namespace(self, namespace: str = None):
        if namespace is None:
            # namespace info is mandatory to provide by users
            raise Exception("Pinecone namespace should be provided, currently it's empty.")
        return namespace

    def __pinecone_query(self,
                         headers: dict,
                         query_body: dict) -> dict:
        try:
            query_response = requests.post(url=self.query_url, headers=headers, json=query_body)
            if query_response.status_code in HttpRetryableStatusCodes:
                raise EmbeddingSearchRetryableError(query_response.text)
            elif query_response.status_code != HTTPStatus.OK:
                raise Exception(query_response.text)
            elif query_response.text == "":
                raise Exception("Pinecone query request returned 200, but response is empty")
            return query_response.json()
        except EmbeddingSearchRetryableError as e:
            raise e
        except Exception as e:
            raise Exception("Pinecone query requqest failed with error: {0}".format(e)) from e
