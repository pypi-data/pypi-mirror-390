import os
from typing import List, Dict
import requests
import urllib.request

from .remote_client import (
    RemoteClient,
    UnsupportedRemoteClientOperationException
)
from ..utils.common_utils import CommonUtils


class HttpClient(RemoteClient):

    def __init__(self, urls: List[str], local_path: str):
        self.__urls = urls
        self.__local_path = local_path
        self.__url_to_relatvie_path = self.map_to_relatvie_paths(
            urls=self.__urls
        )

    def if_folder_exists(self) -> bool:
        if len(self.__urls) > 0:
            response = requests.head(self.__urls[0])
            if response.status_code == 200:
                return True
        return False

    def download(self):
        for url, path in self.__url_to_relatvie_path.items():
            destination_path = os.path.join(self.__local_path, path)
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            urllib.request.urlretrieve(url, destination_path)

    def upload(self):
        raise UnsupportedRemoteClientOperationException(
            "upload is not supported for http client"
        )

    def get_etag(self, file_relative_path) -> str:
        for url, relative_path in self.__url_to_relatvie_path.items():
            if file_relative_path in relative_path:
                return self.get_url_etag(url)
        return CommonUtils.generate_timestamp_based_unique_id()

    def get_remote_store_files_size(self) -> int:
        total_size = 0
        for url in self.__urls:
            total_size += self.get_remote_file_size_by_url(url)
        return total_size

    def get_downloaded_store_files_size(self) -> int:
        total_size = 0
        for dirpath, _, filenames in os.walk(self.__local_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    @staticmethod
    def map_to_relatvie_paths(urls: List[str]) -> Dict[str, str]:
        if urls is None or len(urls) == 0:
            return None

        url_to_splitted = {url: url.split('/') for url in urls}

        min_len = min([len(splitted) for splitted in url_to_splitted.values()])
        relavite_start_index = 0
        for i in range(min_len):
            if not all(
                [splitted[i] == url_to_splitted[urls[0]][i] for splitted in url_to_splitted.values()]
            ):
                relavite_start_index = i
                break
        url_to_path = {
            url: os.sep.join(splitted[relavite_start_index:]) for url, splitted in url_to_splitted.items()
        }
        return url_to_path

    @staticmethod
    def get_url_etag(url: str) -> str:
        response = requests.head(url)
        if response.status_code == 200:
            etag = response.headers.get('ETag')
            if etag:
                return etag
            last_modified = response.headers.get('Last-Modified')
            if last_modified:
                return last_modified
        return None

    @staticmethod
    def get_remote_file_size_by_url(url) -> int:
        response = requests.head(url)
        if response.status_code == 200:
            content_length = response.headers.get('content-length')
            if content_length:
                return int(content_length)
        return 0
