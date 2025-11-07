import os

from ..utils.azure_helpers import AzureHelpers
from ..utils.aml_helpers import AmlHelpers, AmlAgent
from ..utils.common_utils import CommonUtils
from .remote_client import (
    RemoteClient,
    UnsupportedRemoteClientOperationException
)


class AMLDataStoreClient(RemoteClient):

    @AzureHelpers.map_azure_exceptions
    def __init__(self, url: str, local_path: str):
        self.__url = url
        self.__local_path = local_path
        self.__datastore_info = AmlHelpers.parse_data_store_url(self.__url)
        self.__aml_agent = AmlAgent(self.__datastore_info)

    @AzureHelpers.map_azure_exceptions
    def if_folder_exists(self) -> bool:
        return self.__aml_agent.is_datastore_path_exists(self.__url)

    @AzureHelpers.map_azure_exceptions
    def download(self):
        self.__aml_agent.download_from_datastore_url(
            url=self.__url,
            destination=self.__local_path
        )

    def upload(self):
        raise UnsupportedRemoteClientOperationException(
            "upload is not supported for AML datastore"
        )

    def get_etag(self, file_relative_path) -> str:
        return CommonUtils.generate_timestamp_based_unique_id()

    def get_remote_store_files_size(self) -> int:
        return None

    def get_downloaded_store_files_size(self) -> int:
        total_size = 0
        for dirpath, _, filenames in os.walk(self.__local_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size
