from typing import List
from .adapter import Adapter

from ...service.client.embeddingstore_client import EmbeddingStoreClient
from ..contracts import StoreType
from ..contracts.ui_config import VectorSearchToolUIConfig
from ..contracts.config import VectorSearchToolConfig
from promptflow.connections import CognitiveSearchConnection
from ...connections.pinecone import PineconeConnection
from ...connections.weaviate import WeaviateConnection
from ...connections.qdrant import QdrantConnection
from ...core.contracts.exceptions import UnsupportedFeatureException


class UnsupportedPromptflowConnectionTypeException(UnsupportedFeatureException):
    pass


class ConnectionBasedAdapter(Adapter):
    def __init__(self, ui_config: VectorSearchToolUIConfig):
        self.__search_tool_config: VectorSearchToolConfig = None

        if isinstance(ui_config.connection, CognitiveSearchConnection):
            self.__search_tool_config = self.__get_acs_config(ui_config)
        elif isinstance(ui_config.connection, PineconeConnection):
            self.__search_tool_config = self.__get_pinecone_config(ui_config)
        elif isinstance(ui_config.connection, WeaviateConnection):
            self.__search_tool_config = self.__get_weaviate_config(ui_config)
        elif isinstance(ui_config.connection, QdrantConnection):
            self.__search_tool_config = self.__get_qdrant_config(ui_config)
        else:
            raise UnsupportedPromptflowConnectionTypeException(
                f"Invalid connection type for vector db: {type(ui_config.connection)}"
            )

        store_service_config = self.__search_tool_config.generate_store_service_config()
        self.__store = EmbeddingStoreClient(store_service_config)

    def load(self):
        self.__store.load()

    def search(
        self,
        query: List[float],
        top_k: int = 5,
        index_name: str = None,  # for cognitive search
        class_name: str = None,  # for weaviate search
        namespace: str = None,  # for pinecone search
        collection_name: str = None,  # for qdrant search
        text_field: str = None,
        vector_field: str = None,
        search_params: dict = None,
        search_filters: dict = None
    ) -> List[dict]:

        collection = None

        if self.__search_tool_config.store_type == StoreType.COGNITIVESEARCH:
            collection = index_name
        elif self.__search_tool_config.store_type == StoreType.WEAVIATE:
            collection = class_name
        elif self.__search_tool_config.store_type == StoreType.PINECONE:
            collection = namespace
        elif self.__search_tool_config.store_type == StoreType.QDRANT:
            collection = collection_name

        obj_list = self.__store.search_by_embedding(
            query_embedding=query,
            top_k=top_k,
            collection=collection,
            text_field=text_field,
            vector_field=vector_field,
            search_params=search_params,
            search_filters=search_filters
        )
        return [obj.as_dict() for obj in obj_list]

    def __get_acs_config(self, ui_config: VectorSearchToolUIConfig):
        acs_connection: CognitiveSearchConnection = ui_config.connection
        return VectorSearchToolConfig(
            store_type=StoreType.COGNITIVESEARCH,
            url=acs_connection.api_base,
            api_version=acs_connection.api_version,
            secret=acs_connection.api_key,
            logging_config=ui_config.logging_config
        )

    def __get_pinecone_config(self, ui_config: VectorSearchToolUIConfig):
        pinecone_connection: PineconeConnection = ui_config.connection
        return VectorSearchToolConfig(
            store_type=StoreType.PINECONE,
            url=pinecone_connection.api_base,
            secret=pinecone_connection.api_key,
            logging_config=ui_config.logging_config
        )

    def __get_weaviate_config(self, ui_config: VectorSearchToolUIConfig):
        weaviate_connection: WeaviateConnection = ui_config.connection
        return VectorSearchToolConfig(
            store_type=StoreType.WEAVIATE,
            url=weaviate_connection.api_base,
            secret=weaviate_connection.api_key,
            logging_config=ui_config.logging_config
        )

    def __get_qdrant_config(self, ui_config: VectorSearchToolUIConfig):
        qdrant_connection: QdrantConnection = ui_config.connection
        return VectorSearchToolConfig(
            store_type=StoreType.QDRANT,
            url=qdrant_connection.api_base,
            secret=qdrant_connection.api_key,
            logging_config=ui_config.logging_config
        )
