from .common_index_lookup_utils import forward_mapping
from .common_index_lookup_utils.constants import IndexTypes

from azureml.rag import MLIndex
from promptflow import tool, ToolProvider
from ruamel.yaml import YAML
from typing import List

yaml = YAML()


class FaissIndexLookup(ToolProvider):

    def __init__(self, path: str):
        mlindex_content = forward_mapping(None, None, None, index_type=IndexTypes.FAISS, faiss_index_path=path)
        mlindex_config = yaml.load(mlindex_content)
        index = MLIndex(mlindex_config=mlindex_config)
        self.vectorstore = index.as_langchain_vectorstore()

    @tool
    def search(
        self,
        vector: List[float],
        top_k: int = 3
    ) -> List[dict]:
        results = self.vectorstore.similarity_search_with_score_by_vector(vector, k=top_k)
        return [
            {
                'text': doc.page_content,
                'metadata': doc.metadata,
                'score': score
            } for doc, score in results]
