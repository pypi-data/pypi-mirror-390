import logging
import copy
import threading
import queue
from contextvars import ContextVar

from ..contracts import IdentifierConverter
from ..utils.common_utils import CommonUtils
from ..utils.global_instance_manager import GlobalInstanceManager


class LogHandlerManager(GlobalInstanceManager):

    def get_instance(self, handler_type: type, **kwargs) -> logging.Handler:
        return super()._get_instance(
            identifier=IdentifierConverter.hash_params(**kwargs),
            handler_type=handler_type,
            **kwargs
        )

    def _create_instance(self, handler_type: type, **kwargs) -> logging.Handler:
        return handler_type(**kwargs)


class ContextVersionManager:

    def __init__(self, context_var: ContextVar):
        self.context_var = context_var
        self.version_history = []

    def push(self, value):
        self.version_history.append(value)
        self.context_var.set(value)

    def pop(self):
        if len(self.version_history) == 0:
            return
        self.version_history.pop()
        previous_value = None
        if len(self.version_history) > 0:
            previous_value = self.version_history[-1]
        self.context_var.set(previous_value)

    def get_version_history(self) -> list:
        return self.version_history


class TelemetryLogHandler(logging.Handler):

    EVENT_NAME_KEY = 'event_name'
    CUSTOM_DIMENSIONS_KEY = 'custom_dimensions'
    THREAD_CONTEXT = ContextVar('telemetry_thread_context', default=None)
    THREAD_CONTEXT_MANAGER = ContextVar("telemetry_thread_context_manager", default=None)

    def __init__(
        self,
        handler_type: type,
        formatter: logging.Formatter = None,
        context: dict = None,
        **kwargs
    ):
        super().__init__()

        self._handler = None
        self._is_valid = True
        self._context = context.copy() if context else {}
        self._formatter = formatter if formatter else logging.Formatter()
        self._record_cache = queue.Queue()
        self._thread = threading.Thread(target=self._setup_handler, args=(handler_type,), kwargs=kwargs)
        self._thread.start()

    def _update_record_before_emit(self, record: logging.LogRecord):
        pass

    def update_context(self, context: dict):
        self._context.update(context)

    def reset_context(self, context: dict):
        self._context = context.copy() if context else {}

    def emit(self, record: logging.LogRecord):
        if not self._is_valid:
            return
        record = copy.copy(record)
        self._set_custom_dimensions(record)
        record.exc_info = None  # used only for telemetry with compliant info
        if self._handler:
            self._handler.emit(record)
        else:
            self._record_cache.put(record)

    def close(self):
        self._thread.join()
        self._flush_cache()
        super().close()

    @staticmethod
    def set_telemetry_thread_context(context):
        if TelemetryLogHandler.THREAD_CONTEXT_MANAGER.get() is None:
            TelemetryLogHandler.THREAD_CONTEXT_MANAGER.set(
                ContextVersionManager(TelemetryLogHandler.THREAD_CONTEXT)
            )
        TelemetryLogHandler.THREAD_CONTEXT_MANAGER.get().push(context)

    @staticmethod
    def pop_telemetry_thread_context():
        TelemetryLogHandler.THREAD_CONTEXT_MANAGER.get().pop()

    def flush(self):
        if self._handler:
            self._handler.flush()

    def _setup_handler(self, handler_type: str, **kwargs):
        try:
            manager: LogHandlerManager = LogHandlerManager()
            self._handler: logging.Handler = manager.get_instance(
                handler_type=handler_type,
                **kwargs
            )
            if not self._handler:
                return

            self._handler.setFormatter(self._formatter)
            self._flush_cache()
        except Exception:
            self._handler = None
            self._is_valid = False

    def _flush_cache(self):
        if not self._handler:
            return
        while not self._record_cache.empty():
            record = self._record_cache.get()
            self._handler.emit(record)
            self._record_cache.task_done()
        self._handler.flush()

    def _set_custom_dimensions(self, record: logging.LogRecord):

        custom_dimensions_from_record = getattr(record, self.CUSTOM_DIMENSIONS_KEY, {})

        custom_dimensions = {}
        custom_dimensions.update(self._context)
        custom_dimensions.update(self._get_thread_context())
        custom_dimensions.update(custom_dimensions_from_record)
        custom_dimensions.update(
            {
                "process_id": record.process,
                "thread_id": threading.get_ident(),
                "name": record.name,
                "level_number": record.levelno,
                "precise_timestamp": CommonUtils.get_utc_now_standard_format_with_zone()
            }
        )
        setattr(record, self.CUSTOM_DIMENSIONS_KEY, custom_dimensions)

    def _get_thread_context(self) -> dict:
        thread_context_manager: ContextVersionManager = TelemetryLogHandler.THREAD_CONTEXT_MANAGER.get()
        if thread_context_manager is None:
            return {}
        context_version_history = thread_context_manager.get_version_history()
        merged_context = {}
        for context in context_version_history:
            if context:
                merged_context.update(context)
        return merged_context
