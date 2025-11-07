import contextlib
import logging
import traceback
import uuid

from azureml.rag.utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    track_activity,
)

from ...core.logging.utils import LoggingUtils
from ..common_index_lookup_utils.constants import LoggerNames
from ..contracts.telemetry import StoreToolEventCustomDimensions
from ..utils.logging import ToolLoggingUtils

_promptflow_logger = None
_rag_logger = get_logger(
    "index_lookup_tool(Promptflow)"
)  # explicitly differentiate the RAG logger


def get_lookup_logger(name: LoggerNames, log_level: int = logging.INFO):
    if name == LoggerNames.PromptflowTool:
        global _promptflow_logger

        if _promptflow_logger is None:
            # Initialize promptflow logger
            logging_config = ToolLoggingUtils.generate_config(
                tool_name="index_lookup_tool",
                log_level=log_level,
            )
            _promptflow_logger = LoggingUtils.sdk_logger(__package__, logging_config)
            _promptflow_logger.update_telemetry_context(
                {StoreToolEventCustomDimensions.TOOL_INSTANCE_ID: str(uuid.uuid4())}
            )

        return _promptflow_logger
    elif name == LoggerNames.AzureMLRAG:
        return _rag_logger
    else:
        raise ValueError(f"No logger named '{name}' exists.")


def enable_rag_logger(log_level, stdout=True, appinsight=True):
    if stdout:
        enable_stdout_logging(log_level)
    if appinsight:
        enable_appinsights_logging()


@contextlib.contextmanager
def track_rag_activity(logger, activity_name, custom_dimensions={}):
    try:
        with track_activity(logger, activity_name, custom_dimensions=custom_dimensions) as activity_logger:
            try:
                yield activity_logger
            except Exception:
                activity_logger.error(
                    f"Index lookup failed with exception: {traceback.format_exc()}"
                )  # activity_logger doesn't log traceback
                raise
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
