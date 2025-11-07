import requests
from typing import List
from http import HTTPStatus
from urllib import parse

from ....core.contracts import SearchResultEntity
from ...contracts import StoreServiceConfig
from ...contracts.request_obj import QdrantRequestObj
from .agent import Agent

HEADER_API_KEY = "api-key"
VALUE_FIELD_NAME = "result"
SCORE_FIELD_NAME = "score"
PAYLOAD_FIELD_NAME = "payload"
VECTOR_FIELD_NAME = "vector"


class QdrantClient(Agent):
    def __init__(self, config: StoreServiceConfig):
        self.__config = config
        if self.__config.store_identifier is None or self.__config.store_identifier == "":
            raise Exception("Empty store_identifier provided")

    def load(self):
        return

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

        if collection is None or collection == "":
            raise Exception("Empty collection name provided")

        query_url = parse.urljoin(self.__config.store_identifier, f"/collections/{collection}/points/search")

        headers = {}

        if self.__config.search_agent_api_key:
            headers[HEADER_API_KEY] = self.__config.search_agent_api_key.get_value()

        request_obj = QdrantRequestObj(vector=query_embedding,
                                       limit=top_k,
                                       with_vectors=True,
                                       with_payload=True)
        request_obj.update(search_params)
        request_obj.update(search_filters)
        response = requests.post(url=query_url, headers=headers, json=request_obj.as_dict())

        if response.status_code != HTTPStatus.OK:
            raise Exception(response.text)

        json_obj = response.json()
        target_list = json_obj[VALUE_FIELD_NAME]

        res = [SearchResultEntity(original_entity=item,
                                  score=item[SCORE_FIELD_NAME],
                                  vector=item[VECTOR_FIELD_NAME],
                                  metadata=item[PAYLOAD_FIELD_NAME]) for item in target_list]

        if text_field is not None:
            for item in res:
                item.text = item.original_entity[PAYLOAD_FIELD_NAME][text_field]

        return res

    def clear(self):
        return
