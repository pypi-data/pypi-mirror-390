from enum import Enum


class StoreServiceEventNames(str, Enum):

    INIT = "EmbeddingStore.Client.Init"
    LOAD = "EmbeddingStore.Client.Load"
    SEARCH_BY_EMBEDDING = "EmbeddingStore.Client.SearchByEmbedding"
    SEND_REST_REQUEST = "EmbeddingStore.Client.SendRestRequest"
    HANDLE_REST_REQUEST = "EmbeddingStore.Server.HandleRestRequest"


class StoreServiceCustomDimensions(str, Enum):
    STORAGE_TYPE = "storage_type"
    INDEX_TYPE = "index_type"
    ENGINE_TYPE = "engine_type"
    MODEL_TYPE = "model_type"
    SECRET_SOURCE_TYPE = "secret_source_type"
    AGENT_TYPE = "agent_type"
    SERVER_INSTANCE_ID = "server_instance_id"
    EMBEDDING_SERVICE_REQUEST_TYPE = "embedding_service_request_type"
    EMBEDDING_SERVICE_REQUEST_ID = "embedding_service_request_id"
