import os
from typing import Any

from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.identity import DefaultAzureCredential

from .remote_client import RemoteClient
from ..utils.azure_helpers import AzureHelpers
from ..contracts.exceptions import (
    RemoteResourceAuthenticationException,
    FileNotFoundException
)


class BlobFileNotFoundError(FileNotFoundException):
    pass


class AzureBlobClient(RemoteClient):

    @AzureHelpers.map_azure_exceptions
    def __init__(self,
                 url: str,
                 local_path: str,
                 conn_str: str = None,
                 credential: str = None):

        self.__url = url
        self.__local_path = local_path
        self.__azure_blob_info = AzureHelpers.parse_blob_url(self.__url)

        blob_service_client = None

        if conn_str:
            blob_service_client = BlobServiceClient.from_connection_string(conn_str)
            self.__container_client = blob_service_client.get_container_client(self.__azure_blob_info.container_name)
        else:
            if credential is None:
                credential = DefaultAzureCredential()
            self.__container_client = self.__get_container_client_with_credential(credential)

            # check if default credential works
            try:
                self.if_folder_exists()
            except RemoteResourceAuthenticationException:
                # try non-credential for public blob
                self.__container_client = self.__get_container_client_with_credential()
                self.if_folder_exists()

    @AzureHelpers.map_azure_exceptions
    def if_folder_exists(self):
        blob_list = self.__container_client.list_blobs(name_starts_with=self.__azure_blob_info.folder_path)
        return len(list(blob_list)) > 0

    @AzureHelpers.map_azure_exceptions
    def download(self):
        blob_list = self.__container_client.list_blobs(name_starts_with=self.__azure_blob_info.folder_path)
        for blob in blob_list:
            os.makedirs(self.__local_path, exist_ok=True)
            blob_client = self.__container_client.get_blob_client(blob.name)
            file_name = os.path.basename(blob.name)
            local_file_path = os.path.join(self.__local_path, file_name)
            with open(local_file_path, "wb") as local_copy:
                download_stream = blob_client.download_blob()
                local_copy.write(download_stream.readall())

    @AzureHelpers.map_azure_exceptions
    def upload(self):
        for root, _, files in os.walk(self.__local_path):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, self.__local_path)
                blob_client = self.__get_blob(relative_path)
                with open(local_path, "rb") as data:
                    blob_client.upload_blob(data, overwrite=True)

    @AzureHelpers.map_azure_exceptions
    def delete(self):
        blob_list = self.__container_client.list_blobs(name_starts_with=self.__azure_blob_info.folder_path)
        for blob in blob_list:
            self.__container_client.delete_blob(blob.name)

    @AzureHelpers.map_azure_exceptions
    def get_etag(self, file_relative_path):
        blob_client = self.__get_blob(file_relative_path)

        if blob_client.exists():
            properties = blob_client.get_blob_properties()
            return str(properties.etag)
        raise BlobFileNotFoundError(f'{file_relative_path} does not exist')

    @AzureHelpers.map_azure_exceptions
    def get_remote_store_files_size(self) -> int:
        total_size = 0
        for blob in self.__container_client.list_blobs(name_starts_with=self.__azure_blob_info.folder_path):
            total_size += blob.size
        return total_size

    def get_downloaded_store_files_size(self) -> int:
        total_size = 0
        for dirpath, _, filenames in os.walk(self.__local_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def __get_blob(self, file_relative_path):
        blob_name = os.path.join(self.__azure_blob_info.folder_path, file_relative_path).replace("\\", "/")
        return self.__container_client.get_blob_client(blob_name)

    def __get_container_client_with_credential(self, credential: Any = None) -> ContainerClient:
        blob_service_client = BlobServiceClient(
            account_url=self.__azure_blob_info.account_url,
            credential=credential
        )
        return blob_service_client.get_container_client(self.__azure_blob_info.container_name)
