import logging
from functools import wraps

from .loggers import LoggerManager, StoreLogger
from ..contracts import LoggingConfig, LoggingFormatTemplate, StoreCoreEventCustomDimensions
from ..contracts import StoreEntryType, StoreStage, StoreOperation, ErrorType
from ..contracts.exceptions import EmbeddingStoreException
from ..utils.common_utils import CommonUtils


class LoggingUtils:

    @staticmethod
    def create_stream_handler(entry_name: str) -> logging.Handler:
        stream_handler = logging.StreamHandler()
        stream_formatter = logging.Formatter(
            fmt=LoggingFormatTemplate.LONG_FORMAT.format(tag=entry_name),
            datefmt=LoggingFormatTemplate.DATE_FORMAT
        )
        stream_handler.setFormatter(stream_formatter)
        return stream_handler

    @staticmethod
    def create_azure_log_handler(
        connection_string: str,
        entry_type: StoreEntryType = StoreEntryType.APP,
        entry_name: str = 'Customized',
        context: dict = None
    ) -> logging.Handler:

        try:
            from opencensus.ext.azure.log_exporter import AzureLogHandler
            from .handlers import TelemetryLogHandler

            sdk_name = CommonUtils.get_package_name_to_level(
                package=__package__,
                level=1
            )
            logging_context = context.copy() if context else {}
            logging_context[StoreCoreEventCustomDimensions.SDK] = sdk_name
            logging_context[StoreCoreEventCustomDimensions.ENTRY_TYPE] = entry_type
            logging_context[StoreCoreEventCustomDimensions.ENTRY_NAME] = entry_name

            azure_log_formatter = logging.Formatter(
                LoggingFormatTemplate.SHORT_FORMAT.format(tag=entry_name)
            )
            azure_log_handler = TelemetryLogHandler(
                handler_type=AzureLogHandler,
                formatter=azure_log_formatter,
                context=logging_context,
                connection_string=connection_string
            )
            return azure_log_handler

        except Exception:
            return None

    @staticmethod
    def sdk_logger(package_name: str, config: LoggingConfig) -> StoreLogger:
        try:
            sdk_sub_package_name = CommonUtils.get_package_name_to_level(package_name, 2)
            logger_manager: LoggerManager = LoggerManager()
            return logger_manager.get_instance(sdk_sub_package_name, config)
        except Exception:
            return StoreLogger()

    @staticmethod
    def log_event(
        package_name: str,
        event_name: str,
        scope_context: dict = None,
        store_stage: StoreStage = None,
        store_operation: StoreOperation = None,
        logger: StoreLogger = None,
        flush: bool = False
    ):
        def decorator_func(func):
            @wraps(func)
            def wrapper(*args, **kwargs):

                if logger:
                    event_logger = logger
                else:
                    try:
                        event_logger = LoggingUtils.sdk_logger(package_name, None)
                    except Exception:
                        event_logger = StoreLogger()

                event_logger.telemetry_event_started(
                    event_name=event_name,
                    store_stage=store_stage,
                    store_operation=store_operation,
                    scope_context=scope_context
                )

                failed = False
                try:
                    res = func(*args, **kwargs)
                    event_logger.telemetry_event_completed(
                        event_name=event_name
                    )
                    return res
                except Exception as e:
                    event_logger._telemetry_logger.exception("")

                    failure_type = ErrorType.UNKNOWN
                    if isinstance(e, EmbeddingStoreException):
                        failure_type = e.error_type
                    event_logger.telemetry_event_failed(
                        event_name=event_name,
                        failure_type=failure_type
                    )
                    failed = True
                    raise
                finally:
                    if flush or failed:
                        event_logger.flush()

            return wrapper
        return decorator_func
