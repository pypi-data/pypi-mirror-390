import requests
import uuid
from typing import List
from http import HTTPStatus

from ....core.contracts import SearchResultEntity
from ....core.contracts.exceptions import (
    SystemErrorException,
    UserErrorException
)
from ....core.logging.utils import LoggingUtils
from ...contracts import StoreServiceConfig, HttpCustomHeaders, RequestType
from ...contracts import LoadRequestObj, SearchRequestObj, RequestObj
from ...contracts.telemetry import StoreServiceEventNames, StoreServiceCustomDimensions
from .agent import Agent


class RestBasedAgent(Agent):

    def __init__(self, config: StoreServiceConfig):
        self.__config = config
        self.__logger = LoggingUtils.sdk_logger(__package__, config)

    def load(self):
        url = f'{self.__config.host}:{self.__config.port}/{RequestType.LOAD}'

        obj = LoadRequestObj()
        obj.store_identifier = self.__config.store_identifier
        obj.storage_type = self.__config.storage_type
        obj.credential = self.__config.credential

        self.send_request_with_obj(url=url, obj=obj)

    def search_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        **kwargs
    ) -> List[SearchResultEntity]:
        url = f'{self.__config.host}:{self.__config.port}/{RequestType.SEARCH}'

        obj = SearchRequestObj()
        obj.store_identifier = self.__config.store_identifier
        obj.storage_type = self.__config.storage_type
        obj.credential = self.__config.credential
        obj.query_embedding = query_embedding
        obj.top_k = top_k

        response = self.send_request_with_obj(url=url, obj=obj)

        json_obj = response.json()
        res = [SearchResultEntity(**item) for item in json_obj]

        return res

    def clear(self):
        url = f'{self.__config.host}:{self.__config.port}/{RequestType.CLEAR}'
        self.send_request_with_obj(url=url)

    def send_request_with_obj(self, url: str, obj: RequestObj = None, headers: dict = None) -> requests.Response:

        request_id = str(uuid.uuid4())

        @LoggingUtils.log_event(
            package_name=__package__,
            event_name=StoreServiceEventNames.SEND_REST_REQUEST,
            scope_context={
                StoreServiceCustomDimensions.EMBEDDING_SERVICE_REQUEST_ID: request_id
            }
        )
        def send_request_of_id_with_obj(
            request_id: str,
            url: str,
            obj: RequestObj = None,
            headers: dict = None
        ) -> requests.Response:

            if not headers:
                headers = {}
            headers = {
                HttpCustomHeaders.REQUEST_ID: request_id
            }

            response = requests.post(url, headers=headers, json=obj.__dict__)

            if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
                raise SystemErrorException.from_json(response.json())
            elif response.status_code != HTTPStatus.OK:
                raise UserErrorException.from_json(response.json())

            return response

        return send_request_of_id_with_obj(request_id, url, obj, headers)
