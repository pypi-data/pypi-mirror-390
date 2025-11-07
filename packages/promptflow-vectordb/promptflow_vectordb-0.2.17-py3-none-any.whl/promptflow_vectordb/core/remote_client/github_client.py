import re
from typing import List
import requests

from .http_client import HttpClient
from ..utils.path_utils import (
    PathUtils,
    GITHUB_ROOT_MAIN_URI_REGEX_FORMAT,
    GITHUB_TREE_URI_REGEX_FORMAT
)
from ..contracts.exceptions import InvalidStoreIdentifierException


class InvalidGithubUrlException(InvalidStoreIdentifierException):
    pass


class GithubClient(HttpClient):

    def __init__(self, url: str, local_path: str):

        download_urls = None
        if PathUtils.is_github_root_main_url(url):
            download_urls = self.get_download_urls_from_root_main_url(url)
        elif PathUtils.is_github_tree_url(url):
            download_urls = self.get_download_urls_from_tree_url(url)
        elif PathUtils.is_github_get_content_api_url(url):
            download_urls = self.get_download_urls_from_github_api_uri(url)

        super().__init__(
            urls=download_urls,
            local_path=local_path
        )

    @staticmethod
    def get_download_urls_from_root_main_url(url: str) -> List[str]:
        match = re.search(
            GITHUB_ROOT_MAIN_URI_REGEX_FORMAT,
            url
        )
        if not match:
            raise InvalidGithubUrlException(f"Invalid github url: {url}")

        owner = match.group(1)
        repo = match.group(2)

        uri = f'https://api.github.com/repos/{owner}/{repo}/contents'
        res = GithubClient.get_download_urls_from_github_api_uri(uri)
        return res

    @staticmethod
    def get_download_urls_from_tree_url(url: str) -> List[str]:
        url = url.rstrip('/')
        match = re.search(
            GITHUB_TREE_URI_REGEX_FORMAT,
            url
        )
        if not match:
            raise InvalidGithubUrlException(f"Invalid github url: {url}")

        owner = match.group(1)
        repo = match.group(2)
        relative = match.group(3)

        items_on_relative = relative.split('/')

        retry = min(3, len(items_on_relative))
        for i in range(retry):
            ref = '/'.join(items_on_relative[:i + 1])
            path = '/'.join(items_on_relative[i + 1:])
            uri = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}'
            res = GithubClient.get_download_urls_from_github_api_uri(uri)
            if res is not None:
                return res
        return None

    @staticmethod
    def get_download_urls_from_github_api_uri(uri: str) -> List[str]:
        uri = uri.rstrip('/')
        response = requests.get(uri)
        if response.status_code == 200:
            data = response.json()
            res = [item['download_url'] for item in data if item['type'] == 'file']
            sub_folder_uri_list = [item['url'] for item in data if item['type'] == 'dir']
            for sub_folder_uri in sub_folder_uri_list:
                res.extend(GithubClient.get_download_urls_from_github_api_uri(sub_folder_uri))
            return res
        return None
