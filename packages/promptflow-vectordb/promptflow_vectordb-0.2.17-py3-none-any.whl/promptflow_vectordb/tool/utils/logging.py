import logging
from typing import List

from ...core.contracts import LoggingConfig, StoreEntryType
from ...core.logging.utils import LoggingUtils


class ToolLoggingUtils:

    @staticmethod
    def generate_config(
        tool_name: str,
        log_level: int = logging.INFO
    ) -> LoggingConfig:
        return LoggingConfig(
            log_handlers=ToolLoggingUtils.get_tool_logging_handlers(tool_name),
            log_level=log_level
        )

    @staticmethod
    def get_tool_logging_handlers(
        tool_name: str
    ) -> List[logging.Handler]:

        handlers = []

        try:
            stream_handler = LoggingUtils.create_stream_handler(tool_name)
        except Exception:
            stream_handler = None
        if stream_handler:
            handlers.append(stream_handler)

        telemetry_handler = None
        try:
            from .pf_runtime_utils import PromptflowRuntimeUtils
            if PromptflowRuntimeUtils.is_running_in_aml():
                context = PromptflowRuntimeUtils.get_pf_context_info_for_telemetry()
                telemetry_handler = LoggingUtils.create_azure_log_handler(
                    connection_string=PromptflowRuntimeUtils.get_app_insight_conn_str(),
                    entry_type=StoreEntryType.APP,
                    entry_name=tool_name,
                    context=context
                )
        except Exception:
            telemetry_handler = None
        if telemetry_handler:
            handlers.append(telemetry_handler)

        return handlers
