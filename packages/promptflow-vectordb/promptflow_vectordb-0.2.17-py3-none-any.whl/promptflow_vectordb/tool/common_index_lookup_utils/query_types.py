from .constants import QueryTypes
from ..utils.callback import CallbackContext, tool_ui_callback

from azureml.rag import MLIndex
from ruamel.yaml import YAML
from typing import Dict, List


@tool_ui_callback
def list_available_query_types(context: CallbackContext, mlindex_content: str) -> List[Dict[str, str]]:
    try:
        yaml = YAML()
        mlindex_config = yaml.load(mlindex_content)
        index = MLIndex(mlindex_config=mlindex_config)
    except Exception:
        return []

    # ACS
    if index.index_config.get('kind') == 'acs':
        supports_text = index.index_config.get('field_mapping', {}).get('content') is not None
        supports_semantic = supports_text and index.index_config.get('semantic_configuration_name') is not None
        supports_vector = index.embeddings_config.get('kind', 'none') != 'none' and\
            index.index_config.get('field_mapping', {}).get('embedding') is not None

        query_types = []
        if supports_text:
            query_types.append({'value': QueryTypes.Simple, 'display_value': QueryTypes.Simple})

        if supports_semantic:
            query_types.append({'value': QueryTypes.Semantic, 'display_value': QueryTypes.Semantic})

        if supports_vector:
            query_types.append({'value': QueryTypes.Vector, 'display_value': QueryTypes.Vector})

        if supports_text and supports_vector:
            query_types.append({'value': QueryTypes.VectorSimpleHybrid, 'display_value': QueryTypes.VectorSimpleHybrid})

        if supports_semantic and supports_vector:
            query_types.append(
                {'value': QueryTypes.VectorSemanticHybrid, 'display_value': QueryTypes.VectorSemanticHybrid})

        return query_types

    # Weaviate
    if index.index_config.get('kind') == 'weaviate':
        supports_text = index.index_config.get('field_mapping', {}).get('content') is not None
        supports_vector = index.embeddings_config.get('kind', 'none') != 'none'

        query_types = []
        if supports_text:
            query_types.append({'value': QueryTypes.Simple, 'display_value': QueryTypes.Simple})
        if supports_vector:
            query_types.append({'value': QueryTypes.Vector, 'display_value': QueryTypes.Vector})
        if supports_text and supports_vector:
            query_types.append({'value': QueryTypes.VectorSimpleHybrid, 'display_value': QueryTypes.VectorSimpleHybrid})

        return query_types

    # Everything else
    return [{'value': QueryTypes.Vector, 'display_value': QueryTypes.Vector}]
