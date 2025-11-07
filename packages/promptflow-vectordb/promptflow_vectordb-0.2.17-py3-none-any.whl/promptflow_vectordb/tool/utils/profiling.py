import contextlib
from time import perf_counter
from typing import Callable

from ..common_index_lookup_utils.logger import get_lookup_logger
from ..common_index_lookup_utils.constants import LoggerNames


@contextlib.contextmanager
def measure_execution_time(
    activity_name: str, callback: Callable = None
):
    pf_logger = get_lookup_logger(LoggerNames.PromptflowTool)
    rag_logger = get_lookup_logger(LoggerNames.AzureMLRAG)

    try:
        start_time = perf_counter()
        yield
    except Exception as e:
        error_msg = f"Exception occured in {activity_name}."
        raise Exception(error_msg) from e
    finally:
        end_time = perf_counter()
        log_message = f"`{activity_name}` completed in {end_time - start_time} seconds."
        if callback:
            callback(log_message)
        else:
            pf_logger.telemetry(msg=log_message, event_name=activity_name)
            rag_logger.info(log_message)
