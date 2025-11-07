from enum import Enum


class TelemetryEventStatus(str, Enum):
    STARTED = 'Started'
    COMPLETED = 'Completed'
    FAILED = 'Failed'


class StoreCoreEventNames(str, Enum):

    INIT = "EmbeddingStore.Core.Init"
    SAVE = "EmbeddingStore.Core.Save"
    CLEAR = "EmbeddingStore.Core.Clear"

    RESOLVE_SECRETS = "EmbeddingStore.Core.ResolveSecrets"

    DOWNLOAD_INDEX = "EmbeddingStore.Core.DownloadIndex"
    UPLOAD_INDEX = "EmbeddingStore.Core.UploadIndex"
    LOAD_INDEX = "EmbeddingStore.Core.LoadIndex"
    DUMP_INDEX = "EmbeddingStore.Core.DumpIndex"

    LOAD_CONFIG = "EmbeddingStore.Core.LoadConfig"
    DUMP_CONFIG = "EmbeddingStore.Core.DumpConfig"

    SEARCH_BY_EMBEDDING = "EmbeddingStore.Core.SearchByEmbedding"
    SEARCH_BY_TEXT = "EmbeddingStore.Core.SearchByText"

    BATCH_INSERT_TEXTS = "EmbeddingStore.Core.BatchInsertTexts"
    BATCH_INSERT_TEXTS_WITH_EMBEDDINGS = "EmbeddingStore.Core.BatchInsertTextsWithEmbeddings"


class StoreCoreEventCustomDimensions(str, Enum):

    SDK = "sdk"
    ENTRY_TYPE = "entry_type"
    ENTRY_NAME = "entry_name"
    STORE_STAGE = "store_stage"
    STORE_OPERATION = "store_operation"
    STORAGE_TYPE = "storage_type"
    INDEX_TYPE = "index_type"
    ENGINE_TYPE = "engine_type"
    MODEL_TYPE = "model_type"
    SECRET_SOURCE_TYPE = "secret_source_type"
    IS_MERGED_STORE = "is_merged_store"
    FAILURE_TYPE = "failure_type"


class StoreEntryType(str, Enum):

    SERVER = "Server"
    APP = "Application"


class StoreStage(str, Enum):
    INITIALIZATION = "Initialization"
    SEARVING = "Serving"


class StoreOperation(str, Enum):
    SEARCH = "Search"
    INSERTION = "Insertion"
    CLEAR = "Clear"
    SAVE = "Save"
