class FileNames:
    EMBEDDING_CONFIG_FILE_NAME = "embedding_store_config.json"
    LOCAL_ETAG_FILE_NAME = "blob_index_file_etag.txt"
    DEFAULT_EMBEDDINGSTORE_NAME = "vector_store_unnamed"


class LoggingFormatTemplate:
    LONG_FORMAT = "%(asctime)s %(process)7d %(name)-24s %(levelname)-8s [{tag}] %(message)s"
    SHORT_FORMAT = "[{tag}] %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S %z"


class LoggingMessageTemplate:
    COMPONENT_INITIALIZED = "{component_name} instance: {instance_type} initialized"
