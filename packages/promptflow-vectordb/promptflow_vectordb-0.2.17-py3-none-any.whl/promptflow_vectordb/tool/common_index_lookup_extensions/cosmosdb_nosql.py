from azureml.rag import MLIndex
from langchain.docstore.document import Document
from typing import List, Tuple


def similarity_search_with_score(
    query: str,
    index: MLIndex,
    top_k: int,
    query_type: str,
    similarity_method: str = "cosine",
) -> List[Tuple[Document, float]]:
    results = []
    if query_type == "Vector":
        vector_store = index.as_langchain_vectorstore()
        results = vector_store.similarity_search_with_score(
            query=query,
            k=top_k,
            search_type=similarity_method
        )
    else:
        raise NotImplementedError()

    return results
