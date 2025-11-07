import os
import tempfile
from io import StringIO
from typing import List

from azureml.rag.mlindex import MLIndex
from promptflow.runtime.utils._utils import get_resource_management_scope
from ruamel.yaml import YAML

from ..utils.callback import CallbackContext

yaml = YAML()


class MLIndexAssetDto(object):
    dataAssetId = None
    name = None
    version = None
    kind = None
    status = None
    sourceKind = None
    createdTime = None
    updatedTime = None

    def __init__(self, property_bag):
        self.__dict__.update(property_bag)


class MLIndexClient(object):
    def __init__(self, context: CallbackContext):
        self.context = context

    def list_indices(self) -> List[MLIndexAssetDto]:
        discovery_url = self.context.ml_client.workspaces.get(self.context.workspace_name).discovery_url
        api_url = self.context.http.get(discovery_url).json().get('api')

        url = f'{api_url}/mlindex/v1.0{self.context.arm_id}/mlindices?pageSize=2048'
        auth_header = f'Bearer {self.context.credential.get_token(get_resource_management_scope()).token}'

        response = self.context.http.post(
            url,
            data="[]",
            headers={'authorization': auth_header, 'content-type': 'application/json'})
        indices = response.json().get('value', [])

        return [MLIndexAssetDto(index) for index in indices]

    def get_mlindex_content(self, uri: str, asset_id: str = None) -> str:
        index = MLIndex(uri)
        with tempfile.TemporaryDirectory() as output_dir:
            index.save(output_dir, just_config=True)
            with open(os.path.join(output_dir, 'MLIndex'), 'r', encoding='utf-8') as src:
                index_object = yaml.load(src.read())

        if 'self' in index_object:
            # Huh? Why is 'self' already here?
            pass
        else:
            index_object['self'] = {
                'path': uri,
                'asset_id': asset_id
            }

        with StringIO() as stream:
            yaml.dump(index_object, stream)
            return stream.getvalue()
