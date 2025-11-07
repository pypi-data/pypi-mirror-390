import logging

from .handlers import TelemetryLogHandler
from ..contracts import LoggingConfig, ErrorType, StoreCoreEventCustomDimensions, TelemetryEventStatus
from ..contracts import StoreStage, StoreOperation
from ..utils.global_instance_manager import GlobalInstanceManager


class StoreLogger(logging.Logger):

    def __init__(self, name: str = None, config: LoggingConfig = None):

        if name is None:
            name = ''

        log_level = logging.CRITICAL + 1

        if config and (config.log_level is not None):
            log_level = config.log_level

        super().__init__(name, log_level)

        if config is None:
            return

        self._telemetry_logger = logging.Logger(name, log_level)

        if (config.log_handlers is not None) and len(config.log_handlers) > 0:
            for handler in config.log_handlers:
                if handler is None:
                    continue
                if not isinstance(handler, TelemetryLogHandler):
                    super().addHandler(handler)
                self._telemetry_logger.addHandler(handler)

    def telemetry(
        self,
        msg: str,
        event_name: str = None,
        custom_dimensions: dict = None
    ):
        try:
            if self._telemetry_logger is None:
                return

            if not custom_dimensions:
                custom_dimensions = {}
            custom_dimensions[TelemetryLogHandler.EVENT_NAME_KEY] = event_name

            extra = {}
            extra[TelemetryLogHandler.EVENT_NAME_KEY] = event_name
            extra[TelemetryLogHandler.CUSTOM_DIMENSIONS_KEY] = custom_dimensions

            self._telemetry_logger.info(msg=msg, extra=extra)
        except Exception:
            self.warning(f"Failed to log telemetry event: {event_name}")

    def telemetry_event_with_status(
        self,
        event_name: str,
        status: TelemetryEventStatus,
        custom_dimensions: dict = None
    ):
        msg = f"{event_name} {status.value.lower()}"
        event_name_with_status = f"{event_name}.{status.value}"
        self.telemetry(
            msg=msg,
            event_name=event_name_with_status,
            custom_dimensions=custom_dimensions
        )

    def telemetry_event_started(
        self,
        event_name: str,
        store_stage: StoreStage = None,
        store_operation: StoreOperation = None,
        scope_context: dict = None,
        custom_dimensions: dict = None
    ):
        thread_context = {}
        if scope_context:
            thread_context.update(scope_context)
        if store_stage:
            thread_context[StoreCoreEventCustomDimensions.STORE_STAGE] = store_stage
        if store_operation:
            thread_context[StoreCoreEventCustomDimensions.STORE_OPERATION] = store_operation

        TelemetryLogHandler.set_telemetry_thread_context(thread_context)

        self.telemetry_event_with_status(
            event_name=event_name,
            status=TelemetryEventStatus.STARTED,
            custom_dimensions=custom_dimensions
        )

    def telemetry_event_completed(
        self,
        event_name: str,
        custom_dimensions: dict = None
    ):
        self.telemetry_event_with_status(
            event_name=event_name,
            status=TelemetryEventStatus.COMPLETED,
            custom_dimensions=custom_dimensions
        )
        TelemetryLogHandler.pop_telemetry_thread_context()

    def telemetry_event_failed(
        self,
        event_name: str,
        failure_type: ErrorType = ErrorType.UNKNOWN,
        custom_dimensions: dict = None
    ):
        failure_context = {}
        if custom_dimensions:
            failure_context.update(custom_dimensions)
        failure_context[StoreCoreEventCustomDimensions.FAILURE_TYPE] = failure_type

        self.telemetry_event_with_status(
            event_name=event_name,
            status=TelemetryEventStatus.FAILED,
            custom_dimensions=failure_context
        )
        TelemetryLogHandler.pop_telemetry_thread_context()

    def flush(self):
        if self._telemetry_logger is None:
            return
        for handler in self._telemetry_logger.handlers:
            handler.flush()

    def update_telemetry_context(self, context: dict):
        if self._telemetry_logger is None:
            return
        for handler in self._telemetry_logger.handlers:
            if isinstance(handler, TelemetryLogHandler):
                handler.update_context(context)

    def reset_telemetry_context(self, context: dict):
        if self._telemetry_logger is None:
            return
        for handler in self._telemetry_logger.handlers:
            if isinstance(handler, TelemetryLogHandler):
                handler.reset_context(context)

    def _log(self, *args, **kwargs):
        try:
            super()._log(*args, **kwargs)
        except Exception:
            pass


class LoggerManager(GlobalInstanceManager):

    def get_instance(self, name: str, config: LoggingConfig) -> StoreLogger:
        return super()._get_instance(identifier=name, name=name, config=config)

    def _create_instance(self, name: str, config: LoggingConfig) -> StoreLogger:
        return StoreLogger(name, config)
