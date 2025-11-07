from .adapter import Adapter
from ..contracts import StoreType
from ..contracts.ui_config import VectorSearchToolUIConfig
from ...core.logging.utils import LoggingUtils
from ...core.contracts import LoggingMessageTemplate
from ...core.contracts.exceptions import UnsupportedFeatureException


class UnsupportedStoreTypeException(UnsupportedFeatureException):
    pass


class AdapterFactory:

    @staticmethod
    def get_adapter(ui_config: VectorSearchToolUIConfig) -> Adapter:

        adapter : Adapter = None

        if ui_config.store_type == StoreType.MLINDEX:
            from .ml_index_adapter import MLIndexAdapter
            adapter = MLIndexAdapter(ui_config)
        elif ui_config.store_type == StoreType.LOCALFAISS:
            from .local_faiss_adapter import LocalFaissAdapter
            adapter = LocalFaissAdapter(ui_config)
        elif (ui_config.store_type.is_file_based):
            from .remote_store_faiss_adapter import RemoteStoreFaissAdapter
            adapter = RemoteStoreFaissAdapter(ui_config)
        elif ui_config.store_type == StoreType.DBSERVICE:
            from .connection_based_adapter import ConnectionBasedAdapter
            adapter = ConnectionBasedAdapter(ui_config)
        else:
            raise ValueError(f"Unsupported store type: {ui_config.store_type}")

        LoggingUtils.sdk_logger(__package__, ui_config.logging_config).info(
            LoggingMessageTemplate.COMPONENT_INITIALIZED.format(
                component_name=Adapter.__name__,
                instance_type=adapter.__class__.__name__
            )
        )

        return adapter
