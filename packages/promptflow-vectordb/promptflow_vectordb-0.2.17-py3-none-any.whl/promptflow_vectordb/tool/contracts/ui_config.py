from dataclasses import dataclass

from .types import StoreType
from ...core.contracts.config import LoggingConfig


@dataclass
class VectorSearchToolUIConfig:

    store_type: StoreType = None,

    path: str = None,  # for faiss and vector index

    connection: object = None,

    logging_config: LoggingConfig = None
