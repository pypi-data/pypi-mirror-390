from typing import List


def ssf_rerank(
    query: str,
    result_groups: List[List[dict]],
    top_k: int,
    ssf_rank_constant: int = 60,
) -> List[dict]:
    if top_k == 0:
        return []

    results = []

    for group in result_groups:
        group_score_sum = sum([result["score"] for result in group])
        for result in group:
            if "additional_fields" not in result:
                result["additional_fields"] = dict()

            pseudo_rank = group_score_sum / result["score"]
            score = 1 / (ssf_rank_constant + pseudo_rank)
            result["additional_fields"]["@promptflow_vectordb.reranker_score"] = score
            results.append(result)

    sorted_results = list(
        reversed(sorted(results, key=lambda r: r["additional_fields"]["@promptflow_vectordb.reranker_score"]))
    )

    if top_k > 0:
        return sorted_results[:top_k]
    else:
        return sorted_results
