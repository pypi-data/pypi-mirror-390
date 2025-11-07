from .store import Store
from ..contracts import StoreCoreConfig, StorageType, LoggingMessageTemplate
from ..contracts.exceptions import UnsupportedFeatureException
from ..logging.utils import LoggingUtils


class UnsupportedStorageTypeException(UnsupportedFeatureException):
    pass


class StoreFactory:

    @staticmethod
    def get_store(config: StoreCoreConfig) -> Store:

        store : Store = None

        if config.storage_type == StorageType.INMEMORY:
            from .in_memory_store import InMemoryStore
            store = InMemoryStore(config)
        elif config.storage_type == StorageType.LOCAL:
            from .local_based_store import LocalBasedStore
            store = LocalBasedStore(config)
        elif config.storage_type.is_remote_file_based:
            from .remote_based_store import RemoteBasedStore
            store = RemoteBasedStore(config)
        else:
            raise UnsupportedStorageTypeException(
                f"This storage type {config.storage_type} has not been implemented yet."
            )

        LoggingUtils.sdk_logger(__package__, config).info(
            LoggingMessageTemplate.COMPONENT_INITIALIZED.format(
                component_name=Store.__name__,
                instance_type=store.__class__.__name__
            )
        )

        return store
