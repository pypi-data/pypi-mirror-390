import json
from typing import Any, Dict

from ...utils.callback import CallbackContext, tool_ui_callback
from .constants import RankerType


@tool_ui_callback
def generate_ranker_parameters(
    context: CallbackContext,
    ranker_type: str,
    serverless_deployment: str = None,
    ssf_rank_constant: int = None,
) -> Dict[str, Any]:
    if ranker_type == RankerType.BM25:
        ranker_config = {"ranker_type": RankerType.BM25}
    elif ranker_type == RankerType.ScaledScoreFusion:
        ranker_config = {"ranker_type": RankerType.ScaledScoreFusion, "ssf_rank_constant": ssf_rank_constant}
    elif ranker_type == RankerType.ServerlessDeployment:
        if serverless_deployment is not None:
            connection_id = f"{context.arm_id}/connections/{serverless_deployment}"
            ranker_config = {"ranker_type": RankerType.ServerlessDeployment, "connection_id": connection_id}
        else:
            raise NotImplementedError("Serverless connections require an explicit connection.")
    else:
        raise ValueError(f"Unexpected ranker type: {ranker_type}")

    try:
        ranker_parameters = json.dumps(ranker_config)
    except Exception as e:
        raise ValueError(f"Failed to process ranker parameters with exception: { e }")

    return ranker_parameters


@tool_ui_callback
def reverse_ranker_parameters(
    context: CallbackContext,
    ranker_parameters: str,
) -> Dict[str, Any]:
    ranker_config = dict()
    ranker_parameters = json.loads(ranker_parameters)
    ranker_type = ranker_parameters.get("ranker_type")

    if ranker_type == RankerType.BM25:
        ranker_config = {"ranker_type": ranker_type}
    elif ranker_type == RankerType.ScaledScoreFusion:
        ranker_config = {"ranker_type": ranker_type, "ssf_rank_constant": ranker_parameters.get("ssf_rank_constant")}
    elif ranker_type == RankerType.ServerlessDeployment:
        connection_id = ranker_parameters.get("connection_id")
        if connection_id:
            connection_specs = connection_id.split("/")
            serverless_deployment = connection_specs[connection_specs.index("connections") + 1]
            ranker_config = {"ranker_type": ranker_type, "serverless_deployment": serverless_deployment}

    return ranker_config
