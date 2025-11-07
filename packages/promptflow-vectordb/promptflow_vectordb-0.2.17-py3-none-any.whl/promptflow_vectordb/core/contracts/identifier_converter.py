import hashlib
import os
from urllib.parse import quote


class IdentifierConverter:

    @staticmethod
    def hash_url(url: str) -> str:
        normalized_url = IdentifierConverter.normalize_url(url)
        return IdentifierConverter.hash(normalized_url)

    @staticmethod
    def hash_path(path: str) -> str:
        normalized_path = IdentifierConverter.normalize_path(path)
        return IdentifierConverter.hash(normalized_path)

    @staticmethod
    def map_url_to_local_path(local_cache_path: str, url: str, store_name: str = None) -> str:
        url_hash = IdentifierConverter.hash_url(url)
        if store_name is None:
            store_name = os.path.basename(os.path.normpath(url))
        local_path = os.path.join(local_cache_path, url_hash, store_name)
        return local_path

    @staticmethod
    def normalize_url(url: str):
        return quote(url, safe="%/:=&?~#+!$,;'@()*[]").rstrip('/')

    @staticmethod
    def normalize_path(url: str):
        return os.path.realpath(url).rstrip('/')

    @staticmethod
    def hash(text: str) -> str:
        sha256 = hashlib.sha256()
        sha256.update(text.encode('utf-8'))
        return sha256.hexdigest()

    @staticmethod
    def hash_params(**kwargs) -> str:
        text = ''
        for _, value in sorted(kwargs.items()):
            try:
                text += str(value)
            except Exception:
                pass
        return IdentifierConverter.hash(text)
