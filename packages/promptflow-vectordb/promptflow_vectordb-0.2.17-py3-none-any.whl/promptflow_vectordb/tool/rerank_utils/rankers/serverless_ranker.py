import requests

from typing import List
from ...common_index_lookup_utils.constants import LoggerNames
from ...common_index_lookup_utils.logger import get_lookup_logger

pf_tool_logger = get_lookup_logger(LoggerNames.PromptflowTool)


def serverless_rerank(
    query: str,
    result_groups: List[List[dict]],
    top_k: int,
    api_base: str,
    api_key: str,
) -> List[dict]:
    if top_k == 0:
        return []
    if api_base is None:
        raise ValueError("API Base was None. An API Base is required for API-based reranker deployments.")
    if api_key is None:
        raise ValueError("API Key was None. An API Key is required for API-based reranker deployments.")

    flattened_results = [item for group in result_groups for item in group]
    corpus = [result["text"] for result in flattened_results]

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    json_body = {"query": query, "documents": corpus}
    if top_k > 0:
        json_body.update({"top_n": top_k})

    try:
        api_response = requests.post(api_base, headers=headers, json=json_body)
        api_response.raise_for_status()
        api_json = api_response.json()
    except Exception as e:
        pf_tool_logger.error(f'Attempting to reach API endpoint "{api_base}" resulted in an error.')
        raise ValueError(f'Failed to get a successful response from API endpoint "{api_base}".') from e

    sorted_results = []
    api_response_results = api_json.get("results")
    for api_response_result in api_response_results:
        result_index = api_response_result.get("index")
        result = flattened_results[result_index]
        if "additional_fields" not in result:
            result["additional_fields"] = dict()

        result["additional_fields"]["@promptflow_vectordb.reranker_score"] = api_response_result.get(
            "relevance_score"
        )
        sorted_results.append(result)

    return sorted_results
