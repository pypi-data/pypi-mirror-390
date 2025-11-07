import gc
import threading
import time
from typing import Dict, List

from ....core.embeddingstore_core import EmbeddingStoreCore
from ....core.contracts import SearchResultEntity, StorageType, StoreCoreConfig
from ....core.contracts import IdentifierConverter, LoggingConfig
from ....core.utils.common_utils import CommonUtils
from ....core.logging.utils import LoggingUtils
from .sys_utils import SysUtils


class StoreJobWorker:
    def __init__(self, config: StoreCoreConfig):
        self.__loading_completed = False
        self.__config = config
        self.loading_lock = threading.Lock()
        self.__logger = LoggingUtils.sdk_logger(__package__, config)

    def load(self):
        with self.loading_lock:
            if self.__loading_completed:
                return
            self.__logger.debug(f"loading [{self.__config.store_identifier}]")
            self.__store = EmbeddingStoreCore(self.__config)
            self.__loading_completed = True

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResultEntity]:
        if not self.__loading_completed:
            self.load()

        self.__logger.debug(f"store is ready [{self.__config.store_identifier}]")

        return self.__store.search_by_embedding(query_embedding, top_k)


class SearchTask:
    def __init__(self, worker: StoreJobWorker):
        self.__completed = False
        self.__worker = worker

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResultEntity]:
        return self.__worker.search(query_embedding, top_k)

    def complete(self):
        self.__completed = True

    def is_completed(self) -> bool:
        return self.__completed


DEFAULT_MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB
PROPORTION_OF_AVAILABLE_MEMORY_FOR_SIZE_LIMIT = 0.33
CLEAR_WAIT_TIMEOUT = 5
CLEAR_CHECK_INTERVAL = 0.1


class StoreRequestManager:
    def __init__(
        self,
        local_cache_path: str,
        default_max_file_size: int,  # size limit when available memory can not be detected or is too small
        logging_config: LoggingConfig
    ):

        self.__workers: Dict[str, StoreJobWorker] = {}
        self.__searching_tasks: Dict[str, SearchTask] = {}

        self.__local_cache_path = local_cache_path

        if default_max_file_size is None:
            default_max_file_size = DEFAULT_MAX_FILE_SIZE
        self.__shared_config = StoreCoreConfig.create_config(
            store_identifier="",
            max_file_size=default_max_file_size,
            local_cache_path=local_cache_path,
            log_handlers=logging_config.log_handlers,
            log_level=logging_config.log_level
        )

        self.__workers_lock = threading.Lock()
        self.__searching_tasks_lock = threading.Lock()

        self.__logger = LoggingUtils.sdk_logger(__package__, logging_config)

    def load(
        self,
        store_identifier: str,
        storage_type: StorageType,
        credential: str = None
    ) -> StoreJobWorker:
        worker = self.__get_worker(
            store_identifier=store_identifier,
            storage_type=storage_type,
            credential=credential
        )
        worker.load()
        return worker

    def search_by_embedding(
        self,
        store_identifier: str,
        storage_type: StorageType,
        query_embedding: List[float],
        top_k: int = 5,
        credential: str = None
    ) -> List[SearchResultEntity]:

        search_task_id = CommonUtils.generate_timestamp_based_unique_id()

        try:
            self.__logger.debug(f"start search [{store_identifier}]")

            worker = None
            with self.__searching_tasks_lock:
                worker = self.__get_worker(
                    store_identifier=store_identifier,
                    storage_type=storage_type,
                    credential=credential
                )
                task = SearchTask(worker)
                self.__searching_tasks[search_task_id] = task

            res = task.search(query_embedding, top_k)
            task.complete()
            return res

        except Exception as e:
            if task is not None:
                task.complete()
            raise e

        finally:
            with self.__searching_tasks_lock:
                self.__searching_tasks.pop(search_task_id, None)

    def clear(self):
        self.__logger.debug("start clear")

        leftover_workers: Dict[str, StoreJobWorker] = {}
        leftover_searching_tasks: Dict[str, SearchTask] = {}

        with self.__workers_lock, self.__searching_tasks_lock:
            leftover_workers = self.__workers.copy()
            self.__workers.clear()
            leftover_searching_tasks = self.__searching_tasks.copy()
            self.__searching_tasks.clear()

        wait_start_time = time.time()
        while True:
            for task_id, task in leftover_searching_tasks.items():
                if (task is None) or task.is_completed():
                    leftover_searching_tasks.pop(task_id, None)
            if len(leftover_searching_tasks) == 0 or (time.time() - wait_start_time > CLEAR_WAIT_TIMEOUT):
                leftover_searching_tasks.clear()
                leftover_workers.clear()
                gc.collect()
                self.__logger.debug("end clear")
                return
            time.sleep(CLEAR_CHECK_INTERVAL)

    def get_searching_tasks_count(self) -> int:
        return len(self.__searching_tasks)

    def get_job_workers_count(self) -> int:
        return len(self.__workers)

    def __get_worker(self, store_identifier: str, storage_type: StorageType, credential: str = None) -> StoreJobWorker:

        try:
            store_key = self.__get_store_unique_key(store_identifier, storage_type)

            with self.__workers_lock:
                if store_key not in self.__workers:
                    config = StoreCoreConfig.create_config(
                        store_identifier=store_identifier,
                        storage_type=storage_type,
                        credential=credential,
                        local_cache_path=self.__shared_config.local_cache_path,
                        max_file_size=self.__get_file_size_limit_according_to_available_memory(),
                        log_handlers=self.__shared_config.log_handlers,
                        log_level=self.__shared_config.log_level
                    )
                    worker = StoreJobWorker(config)
                    self.__workers[store_key] = worker
                    self.__logger.debug(f"added in dicts [{store_identifier}]")
                    return worker
                else:
                    self.__logger.debug(f"exists in dicts [{store_identifier}]")
                    return self.__workers[store_key]
        except Exception as e:
            if store_key in self.__workers:
                self.__workers.pop(store_key)
            raise e

    def __get_store_unique_key(self, store_identifier: str, storage_type: StorageType) -> str:
        if storage_type == StorageType.LOCAL:
            return IdentifierConverter.hash_path(store_identifier)
        elif storage_type.is_remote_file_based:
            local_path = IdentifierConverter.map_url_to_local_path(
                local_cache_path=self.__local_cache_path,
                url=store_identifier,
                store_name=StoreCoreConfig.get_store_name(store_identifier, storage_type)
            )
            return IdentifierConverter.hash_path(local_path)

    def __get_file_size_limit_according_to_available_memory(self) -> int:
        available_memory = SysUtils.get_available_memory_in_bytes()
        if available_memory is None:
            available_memory = 0
        return max(
            available_memory * PROPORTION_OF_AVAILABLE_MEMORY_FOR_SIZE_LIMIT,
            self.__shared_config.max_file_size
        )
