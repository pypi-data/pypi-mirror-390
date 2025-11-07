from langchain.docstore.document import Document
from typing import Dict, List, Optional, Tuple


def vector_search_with_score(
    query: str,
    store: "langchain_weaviate.vectorstores.WeaviateVectorStore",
    k: int = 4,
    field_mapping: Dict[str, str] = None,
    filters: Optional[str] = None
) -> List[Tuple[Document, float]]:
    from weaviate.classes.query import MetadataQuery

    content_field = (field_mapping or {}).get("content") or "content"
    embedding_field = (field_mapping or {}).get("embedding", None)

    response = store._collection.query.near_vector(
        near_vector=store.embeddings.embed_query(query),
        limit=k,
        target_vector=embedding_field,  # Required field if Named Vector is specified
        return_metadata=MetadataQuery(distance=True)
    )

    # Convert results to Document objects
    docs = [
        (
            Document(
                page_content=o.properties.pop(content_field),
                metadata=o.properties,
            ),
            float(o.metadata.distance),
        )
        for o in response.objects
    ]

    return docs


def keyword_search_with_score(
    query: str,
    store: "langchain_weaviate.vectorstores.WeaviateVectorStore",
    k: int = 4,
    field_mapping: Dict[str, str] = None,
    filters: Optional[str] = None
) -> List[Tuple[Document, float]]:
    from weaviate.classes.query import MetadataQuery

    content_field = (field_mapping or {}).get("content") or "content"

    response = store._collection.query.bm25(
        query=query,
        query_properties=[content_field],
        limit=k,
        return_metadata=MetadataQuery(score=True)
    )

    # Convert results to Document objects
    docs = [
        (
            Document(
                page_content=o.properties.pop(content_field),
                metadata=o.properties,
            ),
            float(o.metadata.score),
        )
        for o in response.objects
    ]

    return docs


def hybrid_search_with_score(
    query: str,
    store: "langchain_weaviate.vectorstores.WeaviateVectorStore",
    k: int = 4,
    field_mapping: Dict[str, str] = None,
    filters: Optional[str] = None
) -> List[Tuple[Document, float]]:
    from weaviate.classes.query import MetadataQuery

    content_field = (field_mapping or {}).get("content") or "content"
    embedding_field = (field_mapping or {}).get("embedding", None)

    response = store._collection.query.hybrid(
        query=query,
        query_properties=[content_field],
        vector=store.embeddings.embed_query(query),
        target_vector=embedding_field,
        limit=k,
        return_metadata=MetadataQuery(score=True)
    )

    # Convert results to Document objects
    docs = [
        (
            Document(
                page_content=o.properties.pop(content_field),
                metadata=o.properties,
            ),
            float(o.metadata.score),
        )
        for o in response.objects
    ]

    return docs
