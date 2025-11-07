from typing import List
from .remote_client import RemoteClient
from ..contracts import StoreCoreConfig, StorageType, LoggingMessageTemplate
from ..utils.path_utils import PathUtils
from ..logging.utils import LoggingUtils
from ..contracts.exceptions import UnsupportedFeatureException, MissingInputException


class UnsupportedRemoteClientTypeException(UnsupportedFeatureException):
    pass


class MissingFileRelativePathsException(MissingInputException):
    pass


class RemoteClientFactory:

    @staticmethod
    def get_remote_client(
        config: StoreCoreConfig,
        file_relative_paths: List[str] = None
    ) -> RemoteClient:

        remote_client : RemoteClient = None

        if config.storage_type == StorageType.BLOBSTORAGE:
            from .azure_blob_client import AzureBlobClient
            conn_str = None
            if config.blob_conn_str:
                conn_str = config.blob_conn_str.get_value()
            remote_client = AzureBlobClient(
                url=config.remote_store_path,
                local_path=config.local_store_path,
                conn_str=conn_str,
                credential=config.credential
            )
        elif config.storage_type == StorageType.AMLDATASTORE:
            from .aml_data_store_client import AMLDataStoreClient
            remote_client = AMLDataStoreClient(
                url=config.remote_store_path,
                local_path=config.local_store_path
            )
        elif config.storage_type == StorageType.HTTP:
            if file_relative_paths is None:
                raise MissingFileRelativePathsException(
                    "file_relative_paths must be provided for HttpUrl storage type."
                )
            from .http_client import HttpClient
            remote_client = HttpClient(
                urls=[
                    PathUtils.url_join(config.remote_store_path, file_relative_path)
                    for file_relative_path in file_relative_paths
                ],
                local_path=config.local_store_path
            )
        elif config.storage_type == StorageType.GITHUBFOLDER:
            from .github_client import GithubClient
            remote_client = GithubClient(
                url=config.remote_store_path,
                local_path=config.local_store_path
            )
        else:
            raise UnsupportedRemoteClientTypeException(
                f"This remote client {config.storage_type} has not been implemented yet."
            )

        LoggingUtils.sdk_logger(__package__, config).info(
            LoggingMessageTemplate.COMPONENT_INITIALIZED.format(
                component_name=RemoteClient.__name__,
                instance_type=remote_client.__class__.__name__
            )
        )

        return remote_client
