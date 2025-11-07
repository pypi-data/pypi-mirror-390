import re
import os
import functools
from urllib.parse import urlparse
from dataclasses import dataclass

from azure.core.exceptions import HttpResponseError

from ..contracts.exceptions import RemoteResourceAuthenticationException
from .common_utils import HashableDataclass
from .path_utils import (
    PathUtils,
    BLOB_URL_REGEX_FORMAT,
    InvalidAzureBlobUrlException
)


@dataclass
class AzureBlobInfo(HashableDataclass):
    account_name: str
    account_url: str
    container_name: str
    folder_path: str


class AzureHelpers:

    @staticmethod
    def parse_blob_url(url: str) -> AzureBlobInfo:
        if not PathUtils.is_blob_storage_url(url):
            raise InvalidAzureBlobUrlException(
                f"Invalid blob url: {url}"
            )
        res = urlparse(url)
        dirs = res.path.split('/')
        account_name = re.match(BLOB_URL_REGEX_FORMAT, url)[1]
        account_url = f'{res.scheme}://{res.hostname}'
        container_name = dirs[1]
        if len(dirs) > 2:
            folder_path = os.path.join(*dirs[2:])
        else:
            folder_path = ''

        return AzureBlobInfo(
            account_name=account_name,
            account_url=account_url,
            container_name=container_name,
            folder_path=folder_path
        )

    @staticmethod
    def map_azure_exceptions(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HttpResponseError as e:
                if RemoteResourceAuthenticationException.is_http_authentication_failure(e.status_code):
                    raise RemoteResourceAuthenticationException(e.message, e.status_code)
                else:
                    raise e
        return wrapper
