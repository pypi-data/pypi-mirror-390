from typing import List

from rank_bm25 import BM25Okapi


def bm25_rerank(
    query: str,
    result_groups: List[List[dict]],
    top_k: int,
) -> List[dict]:
    if top_k == 0:
        return []

    flattened_results = [item for group in result_groups for item in group]
    corpus = [result["text"] for result in flattened_results]
    tokenized_corpus = [text.split(" ") for text in corpus]

    bm25 = BM25Okapi(tokenized_corpus)
    reranker_scores = bm25.get_scores(query.split(" "))

    results = []
    for result, reranker_score in zip(flattened_results, reranker_scores):
        if "additional_fields" not in result:
            result["additional_fields"] = dict()

        result["additional_fields"]["@promptflow_vectordb.reranker_score"] = reranker_score
        results.append(result)

    sorted_results = list(
        reversed(sorted(results, key=lambda r: r["additional_fields"]["@promptflow_vectordb.reranker_score"]))
    )

    if top_k > 0:
        return sorted_results[:top_k]
    else:
        return sorted_results
