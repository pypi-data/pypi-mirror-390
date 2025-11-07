import re
import os
from dataclasses import dataclass
from typing import Any

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml._artifacts._artifact_utilities import (
    download_artifact_from_aml_uri,
    aml_datastore_path_exists,
    get_datastore_info
)

from .global_instance_manager import GlobalInstanceManager
from .common_utils import HashableDataclass
from .azure_helpers import AzureHelpers
from .path_utils import (
    PathUtils,
    LONG_DATASTORE_URI_REGEX_FORMAT,
    InvalidAMLDatastoreUrlException,
    InvalidAMLAssetUrlException,
    InvalidAMLWorkspaceConnectionIdException
)


AML_WORKSPACE_BLOB_STORE_NAME = "workspaceblobstore"

KEY_VAULT_RESOURCE_ID_REGEX_FORMAT = (
    r"vaults\/(.+?)($|\/)"
)

WORKSPACE_CONNECTION_ID_REGEX_FORMAT = (
    r"/subscriptions/(.*)/resource[gG]roups/(.*)/providers/"
    r"Microsoft.MachineLearningServices/workspaces/(.*)/connections/(.*)"
)


@dataclass
class WorkspaceInfo(HashableDataclass):
    subscription_id: str
    resource_group: str
    workspace_name: str

    def is_valid(self):
        return (
            self.subscription_id
            and self.resource_group
            and self.workspace_name
        )


@dataclass
class DataStoreInfo(WorkspaceInfo):
    datastore_name: str
    data_path: str = None

    def is_valid(self):
        return super().is_valid() and self.datastore_name


@dataclass
class DataAssetInfo(WorkspaceInfo):
    asset_name: str
    label: str = None
    version: str = None

    def is_valid(self):
        return super().is_valid() and self.asset_name


@dataclass
class WorkspaceConnectionInfo(WorkspaceInfo):
    connection_name: str

    def is_valid(self):
        return super().is_valid() and self.connection_name


class AmlHelpers:

    @staticmethod
    def parse_data_store_url(url: str) -> DataStoreInfo:

        match = re.search(
            LONG_DATASTORE_URI_REGEX_FORMAT,
            url
        )
        if not match:
            raise InvalidAMLDatastoreUrlException(
                f"Invalid datastore url: {url}"
            )

        datastore_info = DataStoreInfo(
            subscription_id=match.group(1),
            resource_group=match.group(2),
            workspace_name=match.group(3),
            datastore_name=match.group(4),
            data_path=match.group(5)
        )

        return datastore_info

    @staticmethod
    def parse_data_asset_url(url: str) -> DataAssetInfo:

        items = url.split('/')

        subscription_id = None
        resource_group = None
        workspace_name = None
        asset_name = None
        version = None
        label = None

        for i in range(1, len(items)):
            key = items[i - 1]
            if key == 'subscriptions':
                subscription_id = items[i]
            elif key == 'resourcegroups':
                resource_group = items[i]
            elif key == 'workspaces':
                workspace_name = items[i]
            elif key == 'data':
                asset_name = items[i]
            elif key == 'versions':
                version = items[i]
            elif key == 'labels':
                version = items[i]

        if label is None and (version is None or version == 'latest'):
            label = 'latest'

        data_asset_info = DataAssetInfo(
            subscription_id=subscription_id,
            resource_group=resource_group,
            workspace_name=workspace_name,
            asset_name=asset_name,
            label=label,
            version=version
        )

        if not data_asset_info.is_valid():
            raise InvalidAMLAssetUrlException(
                f"Invalid data asset url: {url}"
            )

        return data_asset_info

    @staticmethod
    def parse_workspace_connection_id(connection_id: str) -> WorkspaceConnectionInfo:

        uri_match = re.match(
            WORKSPACE_CONNECTION_ID_REGEX_FORMAT,
            connection_id
        )

        if not uri_match:
            raise InvalidAMLWorkspaceConnectionIdException(
                f"Invalid connection id: {connection_id}"
            )

        workspace_info = WorkspaceConnectionInfo(
            subscription_id=uri_match.group(1),
            resource_group=uri_match.group(2),
            workspace_name=uri_match.group(3),
            connection_name=uri_match.group(4)
        )

        return workspace_info

    @staticmethod
    def get_workspace_data_base_url(workspace_info: WorkspaceInfo) -> str:
        return (f"azureml://subscriptions/{workspace_info.subscription_id}/resourcegroups/"
                f"{workspace_info.resource_group}/workspaces/{workspace_info.workspace_name}")


class MLClientManager(GlobalInstanceManager):

    def get_instance(
        self,
        workspace_info: WorkspaceInfo,
        credential: Any = None
    ) -> MLClient:
        workspace_identifier = workspace_info.to_tuple()
        return super()._get_instance(
            identifier=workspace_identifier,
            workspace_info=workspace_info,
            credential=credential
        )

    def _create_instance(self, workspace_info: WorkspaceInfo, credential: Any) -> Any:
        if not credential:
            credential = DefaultAzureCredential()
        return MLClient(
            credential=credential,
            subscription_id=workspace_info.subscription_id,
            resource_group_name=workspace_info.resource_group,
            workspace_name=workspace_info.workspace_name
        )


class AmlAgent:

    def __init__(self, workspace_info: WorkspaceInfo, credential: any = None):

        if credential is None:
            credential = DefaultAzureCredential()

        manager: MLClientManager = MLClientManager()
        self.__client = manager.get_instance(
            workspace_info=workspace_info,
            credential=credential
        )

    @property
    def client(self) -> MLClient:
        return self.__client

    def is_datastore_path_exists(self, url: str) -> bool:
        return aml_datastore_path_exists(
            url,
            self.__client.datastores
        )

    def download_from_datastore_url(self,
                                    url: str,
                                    destination: str):
        download_artifact_from_aml_uri(
            uri=url,
            destination=destination,
            datastore_operation=self.__client.datastores
        )

    def get_key_vault(self):

        ws = self.__client.workspaces.get()

        vault_name = re.search(
            KEY_VAULT_RESOURCE_ID_REGEX_FORMAT,
            str(ws.key_vault)
        ).group(1)

        vault_url = f"https://{vault_name}.vault.azure.net/"

        from azure.keyvault.secrets import SecretClient
        return SecretClient(
            vault_url=vault_url,
            credential=DefaultAzureCredential()
        )

    def is_blob_on_workspace_default_storage(self, blob_url: str) -> bool:
        blob_info = AzureHelpers.parse_blob_url(blob_url)
        default_storage_account = self.__client.workspaces.get().storage_account
        account_name = os.path.basename(default_storage_account)
        return blob_info.account_name == account_name

    def get_default_storage_credential(self) -> str:
        return str(get_datastore_info(self.__client.datastores, AML_WORKSPACE_BLOB_STORE_NAME)['credential'])

    def get_url_for_relative_path_on_workspace_blob_store(self, path: str) -> str:
        datastore_info = get_datastore_info(self.__client.datastores, AML_WORKSPACE_BLOB_STORE_NAME)
        container_url = PathUtils.url_join(datastore_info['account_url'], datastore_info['container_name'])
        return PathUtils.url_join(container_url, path)
