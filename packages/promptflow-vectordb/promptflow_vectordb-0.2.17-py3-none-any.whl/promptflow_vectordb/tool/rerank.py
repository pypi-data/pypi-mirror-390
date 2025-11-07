import json
import logging
import os
from functools import lru_cache, partial
from typing import Any, Callable, Dict, List, Union

from opentelemetry import trace

from promptflow import tool

from ..core.logging.utils import LoggingUtils
from .common_index_lookup_utils.constants import LoggerNames, LoggingEvents
from .common_index_lookup_utils.logger import get_lookup_logger
from .rerank_utils.callbacks.constants import RankerType
from .rerank_utils.callbacks.ranker_types import resolve_serverless_connection, get_connection_key
from .rerank_utils.rankers import bm25_rerank, ssf_rerank, serverless_rerank
from .utils.callback import CallbackContext

__LOG_LEVEL_ENV_KEY = "PF_LOGGING_LEVEL"
try:
    __LOG_LEVEL_MAPPINGS = logging.getLevelNamesMapping()
except AttributeError:
    # logging.getLevelNamesMapping was only introduced in 3.11; fallback for older versions
    __LOG_LEVEL_MAPPINGS = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }

tracer = trace.get_tracer(__name__)

pf_tool_logger = get_lookup_logger(
    LoggerNames.PromptflowTool,
    log_level=__LOG_LEVEL_MAPPINGS.get(os.getenv(__LOG_LEVEL_ENV_KEY), logging.INFO),
)


def _fetch_ranker_config_from_connection(
    connection_id: str,
    connection_category: str,
) -> Dict[str, Any]:
    context_specs = connection_id.split("/")
    subscription_id = context_specs[context_specs.index("subscriptions") + 1]
    resource_group_name = context_specs[context_specs.index("resourceGroups") + 1]
    workspace_name = context_specs[context_specs.index("workspaces") + 1]
    context = CallbackContext.get(subscription_id, resource_group_name, workspace_name)
    connection_name = context_specs[context_specs.index("connections") + 1]

    serverless_connections = context.ml_client.connections._operation.list(
        workspace_name=context.workspace_name,
        cls=lambda objs: objs,
        category=connection_category,
        **context.ml_client.connections._scope_kwargs,
    )

    for connection in serverless_connections:
        if connection.properties.category == connection_category and connection.name == connection_name:

            api_base, _ = resolve_serverless_connection(context, connection)
            api_key = get_connection_key(context, connection)

            api_base = f"{api_base.rstrip('/')}/v1/rerank"
            return {"api_base": api_base, "api_key": api_key}

    raise ValueError(f'No connection was found with name "{connection_name}".')


@lru_cache(maxsize=32)
def _get_rerank_func(
    ranker_parameters: Union[dict, str],
) -> Callable[[str, List[List[dict]]], List[dict]]:

    if isinstance(ranker_parameters, str):
        ranker_parameters = json.loads(ranker_parameters)

    ranker_type = ranker_parameters.get("ranker_type")

    if ranker_type == RankerType.BM25:
        return bm25_rerank

    if ranker_type == RankerType.ScaledScoreFusion:
        ssf_rank_constant = ranker_parameters.get("ssf_rank_constant")
        if ssf_rank_constant:
            return partial(ssf_rerank, ssf_rank_constant=ssf_rank_constant)
        else:
            return ssf_rerank

    if ranker_type == RankerType.ServerlessDeployment:
        api_parameters = _fetch_ranker_config_from_connection(ranker_parameters.get("connection_id"), "Serverless")
        return partial(
            serverless_rerank,
            api_base=api_parameters.get("api_base"),
            api_key=api_parameters.get("api_key"),
        )

    raise ValueError(f'Ranker type "{ranker_type}" not supported.')


@tool
@LoggingUtils.log_event(
    package_name=__package__,
    event_name=LoggingEvents.AzureMLRagSearch,
    logger=pf_tool_logger,
    flush=True,
)
def rerank(
    ranker_parameters: Union[str, dict],
    query: str,
    result_groups: Union[List[dict], List[List[dict]]],
    top_k: int,
) -> List[dict]:
    if isinstance(result_groups, list):
        is_list_dict = True
        for result in result_groups:
            if not isinstance(result, dict):
                is_list_dict = False
                break

        is_list_list_dict = not is_list_dict
        for result in result_groups:
            if not is_list_list_dict or not isinstance(result, list):
                is_list_list_dict = False
                break
            else:
                for entry in result:
                    if not isinstance(entry, dict):
                        is_list_list_dict = False
                        break

        if is_list_dict:
            result_groups = [result_groups]
        elif is_list_list_dict:
            pass
        else:
            pf_tool_logger.error('Rerank cannot be performed - result_groups has an incompatible type.')
            raise TypeError('result_groups must be of type List[dict] or List[List[dict]].')
    else:
        pf_tool_logger.error(f'Rerank cannot be performed - result_groups is of type "{type(result_groups)}".')
        raise TypeError(f'result_groups must be of type list, not of type "{type(result_groups)}".')

    rerank_func = _get_rerank_func(ranker_parameters)
    return rerank_func(query=query, result_groups=result_groups, top_k=top_k)
