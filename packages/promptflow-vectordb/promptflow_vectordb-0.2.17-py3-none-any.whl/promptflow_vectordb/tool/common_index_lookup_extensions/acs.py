from ...core.contracts.entities import SearchResultDocument

import json
from langchain.docstore.document import Document
from typing import Callable, Dict, List, Optional, Tuple, Union


def simple_search_with_score(
        query: str,
        store: "langchain.vectorstores.AzureSearch",
        k: int = 4,
        field_mapping: Dict[str, str] = None,
        filters: Optional[str] = None
) -> List[Tuple[Document, float]]:
    content_field = (field_mapping or {}).get("content") or "content"
    embedding_field = (field_mapping or {}).get("embedding") or "contentVector"
    metadata_field = (field_mapping or {}).get("metadata") or "meta_json_string"

    results = store.client.search(
        search_text=query,
        query_type='simple',
        filter=filters,
        top=k,
    )

    # Convert results to Document objects
    docs = [
        (
            Document(
                page_content=result.pop(content_field),
                metadata=json.loads(result[metadata_field])
                if metadata_field in result
                else {k: v for k, v in result.items() if k != embedding_field},
            ),
            float(result['@search.score']),
        )
        for result in results
    ]

    return docs


def semantic_search_with_score(
        query: str,
        store: "langchain.vectorstores.AzureSearch",
        k: int = 4,
        field_mapping: Dict[str, str] = None,
        filters: Optional[str] = None
) -> List[Tuple[Document, float]]:
    content_field = (field_mapping or {}).get("content") or "content"
    embedding_field = (field_mapping or {}).get("embedding") or "contentVector"
    metadata_field = (field_mapping or {}).get("metadata") or "meta_json_string"

    results = store.client.search(
        search_text=query,
        filter=filters,
        query_type='semantic',
        semantic_configuration_name=store.semantic_configuration_name,
        query_caption='extractive',
        query_answer='extractive',
        top=k,
    )

    # Get Semantic Answers
    semantic_answers = results.get_answers() or []
    semantic_answers_dict: Dict = {}
    for semantic_answer in semantic_answers:
        semantic_answers_dict[semantic_answer.key] = {
            'text': semantic_answer.text,
            'highlights': semantic_answer.highlights,
        }

    # Convert results to Document objects
    docs = [
        (
            Document(
                page_content=result.pop(content_field),
                metadata={
                    **(
                        json.loads(result[metadata_field])
                        if metadata_field in result
                        else {k: v for k, v in result.items() if k != embedding_field}
                    ),
                    **{
                        'captions': {
                            'text': result.get('@search.captions', [{}])[0].text,
                            'highlights': result.get('@search.captions', [{}])[
                                0
                            ].highlights,
                        }
                        if result.get('@search.captions')
                        else {},
                        'answers': semantic_answers_dict.get(
                            result.get("id", "")
                        ),
                    },
                },
            ),
            float(result['@search.score']),
        )
        for result in results
    ]

    return docs


def with_metadata_unpacker(
    search_func: Callable[[str], List[Tuple[Document, float]]],
    metadata_field_name: str
) -> Callable[[str], List[Tuple[SearchResultDocument, float]]]:
    def wrapper(query: str) -> List[Tuple[Document, float]]:
        results = search_func(query)
        processed_results = []
        for result, score in results:
            if "@search.captions" in result.metadata:
                del result.metadata["@search.captions"]
            metadata = result.metadata.pop(metadata_field_name, None)
            try:
                metadata = json.loads(metadata)
            except Exception:
                pass

            processed_results.append((
                SearchResultDocument(
                    page_content=result.page_content,
                    score=score,
                    metadata=metadata or result.metadata,
                    additional_fields=result.metadata
                ),
                score
            ))

        return processed_results

    return wrapper


def search_by_vector_with_score(
        vector: List[float],
        store: Union["langchain.vectorstores.AzureSearch", "langchain.vectorstores.FAISS"],
        kind: str,
        k: int = 4,
        field_mapping: Dict[str, str] = None,
        filters: Optional[str] = None
) -> List[Tuple[Document, float]]:
    """
    Support function supplying query-by-vector support for legacy lookup tools.
    Delete this function when decomissioning legacy tools.
    """
    from azure.search.documents.models import Vector
    import numpy as np

    content_field = (field_mapping or {}).get("content") or "content"
    embedding_field = (field_mapping or {}).get("embedding") or "contentVector"
    metadata_field = (field_mapping or {}).get("metadata") or "meta_json_string"

    if kind == "acs":
        results = store.client.search(
            search_text="",
            vectors=[
                Vector(
                    value=np.array(vector).tolist(),
                    k=k,
                    fields=embedding_field,
                )
            ],
            filter=filters,
        )

        # Convert results to Document objects
        docs = [
            (
                Document(
                    page_content=result.pop(content_field),
                    metadata=json.loads(result[metadata_field])
                    if metadata_field in result
                    else {
                        k: v for k, v in result.items() if k != embedding_field
                    },
                ),
                float(result["@search.score"]),
            )
            for result in results
        ]
        return docs

    elif kind == "faiss":
        return store.similarity_search_with_score_by_vector(vector, k=k, filter=filters)

    else:
        raise NotImplementedError(f"Unexpected index kind '{kind}'.")
