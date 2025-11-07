import re

from ..contracts.exceptions import InvalidStoreIdentifierException


BLOB_URL_REGEX_FORMAT = r"https://([^/]+)\.blob\.core\.windows\.net/.+"

LONG_DATASTORE_URI_REGEX_FORMAT = (
    r"subscriptions/([^/]+)/resource[gG]roups/([^/]+)/workspaces/([^/]+)/datastores/([^/]+)/paths/(.+)"
)

LONG_DATA_ASSET_ID_REGEX_FORMAT = (
    r"azureml://subscriptions/([^/]+)/resource[gG]roups/([^/]+)/"
    r"(?:workspaces|providers/Microsoft.MachineLearningServices/workspaces)/"
    r"([^/]+)/data/(.+)"
)

WORKSPACE_CONNECTION_ID_REGEX_FORMAT = (
    r"/subscriptions/(.*)/resource[gG]roups/(.*)/providers/"
    r"Microsoft.MachineLearningServices/workspaces/(.*)/connections/(.*)"
)

GITHUB_TREE_URI_REGEX_FORMAT = (
    r"(?:http|https)://github.com/([^/]+)/([^/]+)/tree/(.+)"
)

GITHUB_ROOT_MAIN_URI_REGEX_FORMAT = (
    r"(?:http|https)://github.com/([^/]+)/([^/]+)$"
)

GITHUB_GET_CONTENT_API_REGEX_FORMAT = (
    r"(?:http|https)://api.github.com/repos/([^/]+)/([^/]+)/contents($|/(.+))"
)

URL_LIST_SEP = ','


class InvalidAMLDatastoreUrlException(InvalidStoreIdentifierException):
    pass


class InvalidAMLAssetUrlException(InvalidStoreIdentifierException):
    pass


class InvalidAMLWorkspaceConnectionIdException(InvalidStoreIdentifierException):
    pass


class InvalidAzureBlobUrlException(InvalidStoreIdentifierException):
    pass


class PathUtils:

    @staticmethod
    def is_blob_storage_url(url: str) -> bool:
        match = re.match(
            BLOB_URL_REGEX_FORMAT,
            url
        )
        return match is not None

    @staticmethod
    def is_data_store_url(url: str) -> bool:
        match = re.search(
            LONG_DATASTORE_URI_REGEX_FORMAT,
            url
        )
        return match is not None

    @staticmethod
    def is_data_asset_url(url: str) -> bool:
        match = re.search(
            LONG_DATA_ASSET_ID_REGEX_FORMAT,
            url
        )
        return match is not None

    @staticmethod
    def is_workspace_connection_id(url: str) -> bool:
        match = re.search(
            WORKSPACE_CONNECTION_ID_REGEX_FORMAT,
            url
        )
        return match is not None

    @staticmethod
    def is_github_url(url: str) -> bool:
        return (
            PathUtils.is_github_tree_url(url)
            or PathUtils.is_github_root_main_url(url)
            or PathUtils.is_github_get_content_api_url(url)
        )

    @staticmethod
    def is_github_tree_url(url: str) -> bool:
        match = re.match(
            GITHUB_TREE_URI_REGEX_FORMAT,
            url
        )
        return match is not None

    @staticmethod
    def is_github_root_main_url(url: str) -> bool:
        match = re.match(
            GITHUB_ROOT_MAIN_URI_REGEX_FORMAT,
            url
        )
        return match is not None

    @staticmethod
    def is_github_get_content_api_url(url: str) -> bool:
        match = re.match(
            GITHUB_GET_CONTENT_API_REGEX_FORMAT,
            url
        )
        return match is not None

    @staticmethod
    def is_http_url(url: str) -> bool:
        return url.startswith('http://') or url.startswith('https://')

    @staticmethod
    def url_join(url_prefix: str, relative_path: str) -> str:
        return f"{url_prefix.rstrip('/')}/{relative_path.lstrip('/')}"
