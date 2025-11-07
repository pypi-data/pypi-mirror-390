from azureml.rag import MLIndex
from functools import partial
import json
from langchain.docstore.document import Document
from typing import Callable, Dict, List, Tuple


def build_metadata_aware_search_func(
        index: MLIndex,
        k: int = 4,
) -> Callable[[str], List[Tuple[Document, float]]]:
    """
    Support function supplying metadata-aware query-by-vector support for elasticsearch indices.
    """
    index_kind = index.index_config.get('kind')
    if index_kind != 'elasticsearch':
        raise NotImplementedError(f'Unsupported index kind: {index_kind}')

    metadata_field = index.index_config.get('field_mapping', {}).get('metadata')
    if metadata_field:
        fields = [metadata_field]
    else:
        fields = []

    store = index.as_langchain_vectorstore()

    def custom_doc_builder(hit: Dict) -> Document:
        if metadata_field and metadata_field in hit['_source']:
            metadata_result = hit['_source'][metadata_field]
            try:
                metadata_result = json.loads(metadata_result)
            except Exception:
                metadata_result = {(metadata_field or 'metadata'): metadata_result}
        else:
            metadata_result = dict()

        return Document(
            page_content=hit['_source'].get(store.query_field, ''),
            metadata=metadata_result,
        )

    return partial(store.similarity_search_with_score, k=k, fields=fields, doc_builder=custom_doc_builder)
