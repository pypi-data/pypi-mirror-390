from abc import ABC, abstractmethod

from ..contracts.exceptions import UnsupportedFeatureException


class UnsupportedRemoteClientOperationException(UnsupportedFeatureException):
    pass


class RemoteClient(ABC):

    @abstractmethod
    def if_folder_exists(self) -> bool:
        pass

    @abstractmethod
    def download(self):
        pass

    @abstractmethod
    def upload(self):
        pass

    @abstractmethod
    def get_etag(self, file_relative_path) -> str:
        pass

    @abstractmethod
    def get_remote_store_files_size(self) -> int:
        pass

    @abstractmethod
    def get_downloaded_store_files_size(self) -> int:
        pass
