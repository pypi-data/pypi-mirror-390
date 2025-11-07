import requests
from typing import List
from http import HTTPStatus

from ....core.contracts import SearchResultEntity
from ...contracts import StoreServiceConfig
from ...contracts.request_obj import CognitiveSearchRequestObj, CognitiveSearchVectorObj, RequestObj
from .agent import Agent

HEADER_API_KEY = 'api-key'
VALUE_FIELD_NAME = 'value'
SCORE_FIELD_NAME = '@search.score'
SEMANTIC_ANSWER_FIELD_NAME = '@search.answers'


class CogSearchClient(Agent):

    def __init__(self, config: StoreServiceConfig):
        self.__config = config

    def load(self):
        return

    def search_by_embedding(
        self,
        query_embedding: List[float] = None,
        top_k: int = 5,
        collection: str = None,
        text_field: str = None,
        vector_field: str = None,
        search_params: dict = None,
        search_filters: dict = None,
        output_fields: List[str] = None,
    ) -> List[SearchResultEntity]:

        url = (
            f"{self.__config.store_identifier}/indexes/{collection}/"
            f"docs/search?api-version={self.__config.search_agent_api_version}"
        )

        headers = {}

        if self.__config.search_agent_api_key:
            headers[HEADER_API_KEY] = self.__config.search_agent_api_key.get_value()
        headers["User-Agent"] = "promptflow-tool"

        if query_embedding is not None and len(query_embedding) > 0:
            vector_obj = CognitiveSearchVectorObj(value=query_embedding, fields=vector_field, k=top_k)
            vector_obj_list = []
            vector_obj_list.append(vector_obj.as_dict())
            request_obj = CognitiveSearchRequestObj(vectors=vector_obj_list)
        # for non-vector search
        else:
            request_obj = RequestObj()
        request_obj.update(search_params)
        request_obj.update(search_filters)

        response = requests.post(url=url, headers=headers, json=request_obj.as_dict())

        if response.status_code != HTTPStatus.OK:
            raise Exception(response.text)

        json_obj = response.json()
        target_list = json_obj[VALUE_FIELD_NAME]
        res = [SearchResultEntity(original_entity=item, score=item[SCORE_FIELD_NAME]) for item in target_list]

        if self.has_semantic_search_answer(search_params):
            for item in res:
                item.original_entity[SEMANTIC_ANSWER_FIELD_NAME] = json_obj[SEMANTIC_ANSWER_FIELD_NAME]

        if vector_field is not None:
            for item in res:
                if vector_field in item.original_entity:
                    item.vector = item.original_entity[vector_field]

        if text_field is not None:
            for item in res:
                if text_field in item.original_entity:
                    item.text = item.original_entity[text_field]

        return res

    def clear(self):
        return

    @staticmethod
    def has_semantic_search_answer(search_params: dict) -> bool:
        return (search_params is not None
                and search_params.get("queryType") == "semantic"
                and search_params.get("answers") == "extractive")
