from azureml.rag import MLIndex
from azureml.rag.utils.connections import get_connection_credential
from azure.core.credentials import AzureKeyCredential
from langchain.docstore.document import Document
from typing import Dict, List, Tuple, Any
import psycopg2
from psycopg2._psycopg import cursor
from psycopg2 import sql
from pgvector.psycopg2 import register_vector
import numpy as np
from promptflow_vectordb.tool.common_index_lookup_utils.postgresql import (
    close_postgresql_connection,
)


def similarity_search_with_score(
    query: str,
    index: MLIndex,
    top_k: int,
    query_type: str,
) -> List[Tuple[Document, float]]:
    field_mapping = index.index_config.get("field_mapping")
    content_field = (field_mapping or {}).get("content") or "content"
    embedding_field = (field_mapping or {}).get("embedding") or "embedding"

    vectorsearch_method = index.index_config.get("search_type")

    table_name = index.index_config.get("table")
    select_query = _build_sql_query(vectorsearch_method, query_type)

    connection_credential = get_connection_credential(index.index_config)
    if not isinstance(connection_credential, AzureKeyCredential):
        raise ValueError(
            f"Expected credential to Azure Cosmos PostgreSQL to be an "
            f"AzureKeyCredential, instead got: {type(connection_credential)}"
        )

    pg_connection = psycopg2.connect(connection_credential.key)
    register_vector(pg_connection)
    embeddings = index.get_langchain_embeddings().embed_query(query)

    select_query = sql.SQL(select_query).format(
        embedding_field=sql.Identifier(embedding_field),
        table_name=sql.Identifier(table_name),
    )

    params = {
        "embeddings": np.array(embeddings),
        "top_k": top_k,
    }

    cursor = pg_connection.cursor()
    cursor.execute(select_query, params)
    results = cursor.fetchall()
    results = _parse_results(results, cursor, embedding_field)
    close_postgresql_connection(pg_connection)

    docs = []
    for result in results:
        content = result[0].pop(content_field)
        doc_with_score = (Document(page_content=content, metadata=result[0]), result[1])
        docs.append(doc_with_score)
    return docs


def _build_sql_query(vectorsearch_method: str, query_type: str) -> str:
    if query_type == "Vector":
        if vectorsearch_method == "L2":
            select_query = (
                "SELECT *, ({embedding_field} <-> %(embeddings)s) AS score "
                "FROM {table_name} ORDER BY score LIMIT %(top_k)s"
            )
        elif vectorsearch_method == "Cosine":
            select_query = (
                "SELECT *, 1 - ({embedding_field} <=> %(embeddings)s) AS score "
                "FROM {table_name} ORDER BY score DESC LIMIT %(top_k)s"
            )
        elif vectorsearch_method == "Inner":
            select_query = (
                "SELECT *, ({embedding_field} <#> %(embeddings)s) * -1 AS score "
                "FROM {table_name} ORDER BY score DESC LIMIT %(top_k)s"
            )
    return select_query


def _parse_results(
    results: List[Any], cursor: cursor, embedding_field: str
) -> List[Tuple[Dict, float]]:
    retrieved_results = []
    for row in results:
        row_data = {}
        for idx, col in enumerate(cursor.description):
            if isinstance(row[idx], np.ndarray):
                row_data[col.name] = row[idx].tolist()
            else:
                row_data[col.name] = row[idx]
        del row_data[embedding_field]
        score = float(row_data["score"])
        retrieved_results.append((row_data, score))
    return retrieved_results
