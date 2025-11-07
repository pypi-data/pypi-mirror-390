from enum import Enum


class StoreToolEventNames(str, Enum):
    INIT = "EmbeddingStore.Tool.Init"
    IDENTIFY_STORE_TYPE = "EmbeddingStore.Tool.IdentifyStoreType"
    EMBED_QUESTION = "EmbeddingStore.Tool.EmbedQuestion"
    LOAD_MLINDEX = "EmbeddingStore.Tool.LoadMLIndex"
    SEARCH = "EmbeddingStore.Tool.Search"
    AZUREML_RAG_SEARCH = "AzureML.RAG.Search"


class StoreToolEventCustomDimensions(str, Enum):
    STORE_TYPE = "store_type"
    EVENT_NAME = "event_name"
    TOOL_INSTANCE_ID = "tool_instance_id"
    EDITION = "edition"
    COMPUTE_TYPE = "compute_type"
    RUNTIME_MODE = "runtime_mode"
    RUN_MODE = "run_mode"
    RUNTIME_VERSION = "runtime_version"
    SUBSCRIPTION_ID = "subscription_id"
    RESOURCE_GROUP = "resource_group"
    WORKSPACE_NAME = "workspace_name"
    REQUEST_ID = "request_id"
    FLOW_ID = "flow_id"
    ROOT_RUN_ID = "root_run_id"
    RUN_ID = "run_id"
