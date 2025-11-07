from typing import List
from .adapter import Adapter

from ...service.client.embeddingstore_client import EmbeddingStoreClient
from ..contracts.config import VectorSearchToolConfig
from ..contracts.ui_config import VectorSearchToolUIConfig


class LocalFaissAdapter(Adapter):

    def __init__(self, ui_config: VectorSearchToolUIConfig):

        search_tool_config = VectorSearchToolConfig(
            store_type=ui_config.store_type,
            store_path=ui_config.path,
            logging_config=ui_config.logging_config
        )

        store_service_config = search_tool_config.generate_store_service_config()

        self.__store = EmbeddingStoreClient(store_service_config)

    def load(self):
        self.__store.load()

    def search(
        self,
        query: List[float],
        top_k: int = 5,
        **kwargs
    ) -> List[dict]:
        obj_list = self.__store.search_by_embedding(query, top_k)
        return [obj.as_dict() for obj in obj_list]
