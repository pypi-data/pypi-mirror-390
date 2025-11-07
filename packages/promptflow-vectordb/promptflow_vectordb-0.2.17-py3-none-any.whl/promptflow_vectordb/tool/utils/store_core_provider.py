from typing import List

from ...core.embeddingstore_core import EmbeddingStoreCore
from ...core.contracts.config import StoreCoreConfig
from ...core.contracts.types import StorageType
from ...core.utils.path_utils import PathUtils
from ..utils.pf_runtime_utils import PromptflowRuntimeUtils


class StoreCoreProvider:
    @staticmethod
    def create_with_pf_runtime_context(config: StoreCoreConfig) -> EmbeddingStoreCore:
        if (
            config.storage_type == StorageType.BLOBSTORAGE
            and PromptflowRuntimeUtils.is_running_in_aml()
        ):
            if isinstance(config.store_identifier, List) and len(config.store_identifier) > 0:
                for i in range(len(config.store_identifier)):
                    if not PathUtils.is_blob_storage_url(config.store_identifier[i]):
                        url = PromptflowRuntimeUtils.get_url_for_relative_path_on_workspace_blob_store(
                            relative_path=config.store_identifier[i]
                        )
                        config.store_identifier[i] = url
                config.parse_store_identifier()
                config.credential = PromptflowRuntimeUtils.get_credential_if_blob_is_on_workspace_default_storage(
                    blob_url=config.store_identifier[0]
                )
            elif not PathUtils.is_blob_storage_url(config.store_identifier):
                url = PromptflowRuntimeUtils.get_url_for_relative_path_on_workspace_blob_store(
                    relative_path=config.store_identifier
                )
                config.store_identifier = url
                config.parse_store_identifier()

            if not isinstance(config.store_identifier, List):
                config.credential = PromptflowRuntimeUtils.get_credential_if_blob_is_on_workspace_default_storage(
                    blob_url=config.store_identifier
                )

        return EmbeddingStoreCore(config=config)
