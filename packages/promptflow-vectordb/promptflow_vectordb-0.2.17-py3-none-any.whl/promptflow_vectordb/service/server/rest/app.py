import argparse
import logging
import uuid
from http import HTTPStatus


from flask import Flask, request

from ....core.contracts.exceptions import (
    UserErrorException,
    SystemErrorException,
    FileSizeExceededException,
    FileNotFoundException,
    RemoteResourceAuthenticationException
)
from ....core.contracts import StorageType, LoggingConfig, StoreEntryType, StoreStage, StoreOperation
from ....core.logging.utils import LoggingUtils
from ...contracts import LoadRequestObj, ResultMessage, SearchRequestObj
from ...contracts import StoreServiceEventNames, StoreServiceCustomDimensions
from ...contracts import RequestType, HttpCustomHeaders
from ..utils.store_request_manager import StoreRequestManager


app = Flask(__name__)


@app.route(f"/{RequestType.LOAD}", methods=["POST"])
def load():
    try:
        request.path
        request_id = request.headers.get(HttpCustomHeaders.REQUEST_ID)
        scope_context = {
            StoreServiceCustomDimensions.EMBEDDING_SERVICE_REQUEST_TYPE: RequestType.LOAD,
            StoreServiceCustomDimensions.EMBEDDING_SERVICE_REQUEST_ID: request_id
        }

        @LoggingUtils.log_event(
            package_name=__package__,
            event_name=StoreServiceEventNames.HANDLE_REST_REQUEST,
            scope_context=scope_context,
            store_stage=StoreStage.INITIALIZATION,
            logger=logger,
            flush=True
        )
        def do_load():
            request_json = request.get_json()
            obj = LoadRequestObj(**request_json)

            manager.load(
                store_identifier=obj.store_identifier,
                storage_type=StorageType(obj.storage_type),
                credential=obj.credential
            )

        do_load()

        return ResultMessage.STORE_LOADED, HTTPStatus.OK
    except FileNotFoundException as e:
        return e.to_json(), HTTPStatus.NOT_FOUND
    except FileSizeExceededException as e:
        return e.to_json(), HTTPStatus.REQUEST_ENTITY_TOO_LARGE
    except RemoteResourceAuthenticationException as e:
        return e.to_json(), e.http_status_code
    except UserErrorException as e:
        return e.to_json(), HTTPStatus.BAD_REQUEST
    except SystemErrorException as e:
        return e.to_json(), HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception as e:
        return SystemErrorException(str(e)), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route(f"/{RequestType.SEARCH}", methods=["POST"])
def search():
    try:
        request_id = request.headers.get(HttpCustomHeaders.REQUEST_ID)
        scope_context = {
            StoreServiceCustomDimensions.EMBEDDING_SERVICE_REQUEST_TYPE: RequestType.SEARCH,
            StoreServiceCustomDimensions.EMBEDDING_SERVICE_REQUEST_ID: request_id
        }

        @LoggingUtils.log_event(
            package_name=__package__,
            event_name=StoreServiceEventNames.HANDLE_REST_REQUEST,
            scope_context=scope_context,
            store_stage=StoreStage.SEARVING,
            store_operation=StoreOperation.SEARCH,
            logger=logger,
            flush=True
        )
        def do_search():
            request_json = request.get_json()
            obj = SearchRequestObj(**request_json)

            res = manager.search_by_embedding(
                store_identifier=obj.store_identifier,
                storage_type=StorageType(obj.storage_type),
                query_embedding=obj.query_embedding,
                top_k=obj.top_k,
                credential=obj.credential
            )
            return res, HTTPStatus.OK

        return do_search()

    except FileNotFoundException as e:
        return e.to_json(), HTTPStatus.NOT_FOUND
    except FileSizeExceededException as e:
        return e.to_json(), HTTPStatus.REQUEST_ENTITY_TOO_LARGE
    except RemoteResourceAuthenticationException as e:
        return e.to_json(), e.http_status_code
    except UserErrorException as e:
        return e.to_json(), HTTPStatus.BAD_REQUEST
    except SystemErrorException as e:
        return e.to_json(), HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception as e:
        return SystemErrorException(str(e)), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route(f"/{RequestType.CLEAR}", methods=["POST"])
def clear():
    try:
        request_id = request.headers.get(HttpCustomHeaders.REQUEST_ID)
        scope_context = {
            StoreServiceCustomDimensions.EMBEDDING_SERVICE_REQUEST_TYPE: RequestType.CLEAR,
            StoreServiceCustomDimensions.EMBEDDING_SERVICE_REQUEST_ID: request_id
        }

        @LoggingUtils.log_event(
            package_name=__package__,
            event_name=StoreServiceEventNames.HANDLE_REST_REQUEST,
            scope_context=scope_context,
            store_stage=StoreStage.SEARVING,
            store_operation=StoreOperation.CLEAR,
            logger=logger,
            flush=True
        )
        def do_clear():
            manager.clear()
            return ResultMessage.STORES_CLEARED, HTTPStatus.OK

        return do_clear()
    except SystemErrorException as e:
        return e.to_json(), HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception as e:
        return SystemErrorException(str(e)), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route(f"/{RequestType.METADATA}", methods=["GET"])
def metadata():
    try:
        active_stores_count = manager.get_job_workers_count()
        searching_tasks_count = manager.get_searching_tasks_count()

        res = {
            "active_stores_count": active_stores_count,
            "searching_tasks_count": searching_tasks_count
        }

        return res, HTTPStatus.OK
    except SystemErrorException as e:
        return e.to_json(), HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception as e:
        return SystemErrorException(str(e)), HTTPStatus.INTERNAL_SERVER_ERROR


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_file_size", type=int, required=True)
    parser.add_argument("--local_cache_path", type=str, required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--app_insights_key", type=str, required=False, default=None)
    args = parser.parse_args()

    entry_name = 'EmbeddingRestService'
    handlers = [LoggingUtils.create_stream_handler(entry_name)]

    if args.app_insights_key:
        app_insights_handler = LoggingUtils.create_azure_log_handler(
            connection_string=args.app_insights_key,
            entry_type=StoreEntryType.SERVER,
            entry_name=entry_name
        )
        handlers.append(app_insights_handler)

    logging_config = LoggingConfig(
        log_handlers=handlers,
        log_level=logging.INFO
    )

    global logger
    logger = LoggingUtils.sdk_logger(__package__, logging_config)
    logger.update_telemetry_context(
        {
            StoreServiceCustomDimensions.SERVER_INSTANCE_ID: str(uuid.uuid4())
        }
    )

    global manager
    manager = StoreRequestManager(
        local_cache_path=args.local_cache_path,
        default_max_file_size=args.max_file_size,
        logging_config=logging_config
    )

    app.run(port=args.port)


if __name__ == "__main__":
    main()
