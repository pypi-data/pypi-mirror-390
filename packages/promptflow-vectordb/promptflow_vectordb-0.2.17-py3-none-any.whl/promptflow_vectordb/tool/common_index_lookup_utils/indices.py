from .mlindex_client import MLIndexClient
from ..utils.callback import CallbackContext, tool_ui_callback
from typing import Dict, List


@tool_ui_callback
def list_registered_mlindices(context: CallbackContext) -> List[Dict[str, str]]:
    mlindex_client = MLIndexClient(context)
    indices = mlindex_client.list_indices()

    return [{
        'value': index.dataAssetId,
        'display_value': f'{index.name}:{index.version}',
    } for index in indices if index.status == 'Ready']
