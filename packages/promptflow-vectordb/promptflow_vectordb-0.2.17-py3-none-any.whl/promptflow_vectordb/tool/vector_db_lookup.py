from ..connections.pinecone import PineconeConnection
from .common_index_lookup_extensions.acs import search_by_vector_with_score
from .common_index_lookup_utils.constants import APIVersion

from azureml.rag import MLIndex
import os
from promptflow import tool, ToolProvider
from promptflow.connections import CognitiveSearchConnection
import random
import string
from typing import List, Optional, Union


class VectorDBLookup(ToolProvider):

    def __init__(
        self,
        connection: Union[CognitiveSearchConnection, PineconeConnection]
    ):
        self.connection = connection

    @tool
    def search(
        self,
        vector: List[float],
        top_k: int = 3,
        index_name: Optional[str] = None,  # for cognitive search
        class_name: Optional[str] = None,  # for weaviate search
        namespace: Optional[str] = None,  # for pinecone search
        collection_name: Optional[str] = None,  # for qdrant search
        text_field: Optional[str] = None,  # text field name in the response json from search engines
        vector_field: Optional[str] = None,  # vector field name in the response json from search engines
        search_params: Optional[dict] = None,  # additional params for making requests to search engines
        search_filters: Optional[dict] = None,  # additional filters for making requests to search engines
    ) -> List[dict]:
        if isinstance(self.connection, CognitiveSearchConnection):
            variable_name = 'API_KEY_' + ''.join(random.choices(string.ascii_uppercase, k=12))
            os.environ[variable_name] = self.connection.api_key
            mlindex_config = {
                'embeddings': {
                    'schema_version': '2',
                    'kind': 'none',
                },
                'index': {
                    'api_version': self.connection.api_version or APIVersion.ACSApiVersion,
                    'connection': {
                        'key': variable_name
                    },
                    'connection_type': 'environment',
                    'endpoint': self.connection.api_base,
                    'engine': 'azure-sdk',
                    'field_mapping': {
                        'content': text_field,
                        'embedding': vector_field,
                    },
                    'index': index_name,
                    'kind': 'acs',
                },
            }

            mlindex = MLIndex(mlindex_config=mlindex_config)
            vectorstore = mlindex.as_langchain_vectorstore()
            results = search_by_vector_with_score(
                vector,
                vectorstore,
                kind='acs',
                k=top_k,
                field_mapping=mlindex_config['index']['field_mapping'])

        elif isinstance(self.connection, PineconeConnection):
            variable_name = 'API_KEY_' + ''.join(random.choices(string.ascii_uppercase, k=12))
            os.environ[variable_name] = self.connection.api_key
            mlindex_config = {
                'embeddings': {
                    'schema_version': '2',
                    'kind': 'none',
                },
                'index': {
                    'connection': {
                        'key': variable_name
                    },
                    'connection_type': 'environment',
                    'engine': 'azure-sdk',
                    'index': index_name,
                    'kind': 'pinecone',
                },
            }

            mlindex = MLIndex(mlindex_config=mlindex_config)
            vectorstore = mlindex.as_langchain_vectorstore()
            results = vectorstore.similarity_search_by_vector_with_score(vector, k=top_k, namespace=namespace)

        else:
            raise ValueError(f'VectorDBLookup does not support querying connections of type {type(self.connection)}')

        return [
            {
                'text': doc.page_content,
                'metadata': doc.metadata,
                'score': score
            } for doc, score in results]
