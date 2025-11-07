from .common_index_lookup_extensions.acs import search_by_vector_with_score

from azureml.rag import MLIndex
from promptflow import tool, ToolProvider
from typing import List, Union


class VectorIndexLookup(ToolProvider):

    def __init__(self, path: str):
        index = MLIndex(path)
        self.index_kind = index.index_config.get("kind")
        self.field_mapping = index.index_config.get("field_mapping")
        self.vectorstore = index.as_langchain_vectorstore()

    @tool
    def search(
        self,
        query: Union[List[float], str],
        top_k: int = 3
    ) -> List[dict]:
        if isinstance(query, str):
            results = self.vectorstore.similarity_search_with_score(query, k=top_k)
        elif isinstance(query, list) and isinstance(query[0], float):
            results = search_by_vector_with_score(
                query,
                self.vectorstore,
                kind=self.index_kind,
                k=top_k,
                field_mapping=self.field_mapping)

        return [
            {
                'text': doc.page_content,
                'metadata': doc.metadata,
                'score': score
            } for doc, score in results]
