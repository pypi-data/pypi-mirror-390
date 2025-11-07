import json
import os
from typing import List, Union
import tempfile

from .adapter import Adapter
from .ml_index_connection_handlers import ConnectionHandlerFactory, ConnectionHandler
from ..common_index_lookup_utils.constants import APIVersion
from ..contracts import StoreType
from ..contracts.telemetry import StoreToolEventNames
from ..contracts.config import VectorSearchToolConfig
from ..contracts.ui_config import VectorSearchToolUIConfig
from ..contracts.ml_index_yaml_config import MLIndexYamlConfig, EmbeddingsSection, IndexSection, MLIndexSectionBase
from ..contracts.ml_index_yaml_config import MLIndexKind, MLIndexEmbeddingKind
from ..utils.yaml_parser import YamlParser
from ..utils.pf_runtime_utils import PromptflowRuntimeUtils
from ...core.logging.utils import LoggingUtils
from ...core.utils.path_utils import PathUtils
from ...core.utils.common_utils import CommonUtils
from ...core.remote_client import RemoteClient
from ...core.contracts import StoreCoreConfig, EmbeddingModelType, SearchResultEntity
from ...core.contracts import Secret, OpenAIApiType
from ...core.contracts.exceptions import (
    MissingInputException,
    InvalidInputException
)
from ...core.embeddings import EmbeddingFactory
from ...core.contracts.exceptions import InvalidStoreIdentifierException
from ...service.client.embeddingstore_client import EmbeddingStoreClient
from ...service.contracts import StoreServiceConfig


ML_INDEX_CONFIG_FILE_NAME = "MLIndex"

SUPPORTED_FAISS_METHOD = 'flatl2'
SUPPORTED_FAISS_ENGINE = 'langchain'

ACS_API_VERSION = APIVersion.ACSApiVersion

METADATA_JSON_TYPE_SUFFIX = 'json_string'


class InvalidVectorIndexPathException(InvalidStoreIdentifierException):
    pass


class MissingFieldInMLIndexException(MissingInputException):
    pass


class InvalidFieldInMLIndexException(InvalidInputException):
    pass


class MLIndexAdapter(Adapter):

    def __init__(self, ui_config: VectorSearchToolUIConfig):
        self.__logging_config = ui_config.logging_config
        self.__logger = LoggingUtils.sdk_logger(__package__, self.__logging_config)

        self.__collection : str = None
        self.__vector_field : str = None
        self.__text_field : str = None

        self.__load_ml_index(ui_config.path)
        config = self.__generate_store_config()

        self.__store = EmbeddingStoreClient(config)
        self.__embedder = EmbeddingFactory.get_embedding(config)

    def load(self):
        self.__store.load()

    def search(
        self,
        query: Union[List[float], str],
        top_k: int = 5,
        **kwargs
    ) -> List[dict]:

        vector = CommonUtils.try_get_number_list(query)
        if vector is None:
            vector = self.__embed_question(str(query))

        obj_list = self.__store.search_by_embedding(
            query_embedding=vector,
            top_k=top_k,
            collection=self.__collection,
            text_field=self.__text_field,
            vector_field=self.__vector_field
        )

        return [self.__set_entity_metadata(obj).as_dict() for obj in obj_list]

    @LoggingUtils.log_event(__package__, StoreToolEventNames.EMBED_QUESTION)
    def __embed_question(self, question: str) -> List[float]:
        return self.__embedder.embed(question)

    @LoggingUtils.log_event(__package__, StoreToolEventNames.LOAD_MLINDEX)
    def __load_ml_index(self, url: str):

        is_aml_asset = False
        is_data_store = False
        is_blob = False

        if PathUtils.is_data_asset_url(url):
            is_aml_asset = True
            self.__store_type = StoreType.AMLDATASTOREFAISS
        elif PathUtils.is_data_store_url(url):
            is_data_store = True
            self.__store_type = StoreType.AMLDATASTOREFAISS
        elif PathUtils.is_blob_storage_url(url):
            is_blob = True
            self.__store_type = StoreType.BLOBFAISS
        else:
            raise InvalidVectorIndexPathException(
                f"Invalid path for Vector Index: {url}"
            )

        self.__remote_store_path = url

        if is_aml_asset:
            from ...core.utils.aml_helpers import AmlHelpers, AmlAgent
            asset_info = AmlHelpers.parse_data_asset_url(url)
            aml_agent = AmlAgent(asset_info)
            ml_index = aml_agent.client.data.get(
                asset_info.asset_name,
                version=asset_info.version,
                label=asset_info.label
            )
            self.__remote_store_path = ml_index.path

        remote_config_path = os.path.join(self.__remote_store_path, ML_INDEX_CONFIG_FILE_NAME)

        with tempfile.TemporaryDirectory() as temp_folder:

            remote_client: RemoteClient = None
            if is_aml_asset or is_data_store:
                from ...core.remote_client.aml_data_store_client import AMLDataStoreClient
                remote_client = AMLDataStoreClient(
                    url=remote_config_path,
                    local_path=temp_folder
                )
            elif is_blob:
                credential = PromptflowRuntimeUtils.get_credential_if_blob_is_on_workspace_default_storage(
                    blob_url=remote_config_path
                )
                from ...core.remote_client.azure_blob_client import AzureBlobClient
                remote_client = AzureBlobClient(
                    url=remote_config_path,
                    local_path=temp_folder,
                    credential=credential
                )

            remote_client.download()
            local_config_path = os.path.join(temp_folder, ML_INDEX_CONFIG_FILE_NAME)
            self.__ml_index: MLIndexYamlConfig = YamlParser.load_to_dataclass(MLIndexYamlConfig, local_config_path)

    def __generate_store_config(self) -> StoreServiceConfig:
        store_service_config = self.__parse_index_section(self.__ml_index.index)

        try:
            self.__parse_embedding_section(self.__ml_index.embeddings, store_service_config)
        except Exception:
            store_service_config.model_type = EmbeddingModelType.NONE

        return store_service_config

    def __parse_embedding_section(self, embeddings_section: EmbeddingsSection, store_service_config: StoreCoreConfig):

        model_type = EmbeddingModelType.NONE
        model_api_base = None
        model_api_key = None
        model_api_version = None
        model_name = None

        if embeddings_section.kind != MLIndexEmbeddingKind.OPENAI:
            raise InvalidFieldInMLIndexException(
                f"Embedding kind: {embeddings_section.kind} is not valid"
            )

        if embeddings_section.connection is None:
            raise MissingFieldInMLIndexException(
                "Embedding connection is not specified in MLIndex"
            )

        connection_handler = ConnectionHandlerFactory.get_connection_handler(
            embeddings_section.connection_type
        )

        model_api_base = self.__get_api_base(
            connection_handler=connection_handler,
            section=embeddings_section
        )

        model_api_version = self.__get_api_version(
            connection_handler=connection_handler,
            section=embeddings_section
        )

        key_str = self.__get_api_key(
            connection_handler=connection_handler,
            section=embeddings_section
        )
        model_api_key = Secret(key_str)

        api_type = self.__get_embedding_api_type(
            connection_handler=connection_handler,
            section=embeddings_section
        )
        if api_type == OpenAIApiType.AZURE:
            model_type = EmbeddingModelType.AOAI
            model_name = embeddings_section.deployment
        elif api_type == OpenAIApiType.OPENAI:
            model_type = EmbeddingModelType.OPENAI
            model_name = embeddings_section.model

        store_service_config.model_type = model_type
        store_service_config.model_api_base = model_api_base
        store_service_config.model_api_key = model_api_key
        store_service_config.model_api_version = model_api_version
        store_service_config.model_name = model_name

    def __parse_index_section(self, index_section: IndexSection) -> StoreServiceConfig:

        store_path = None
        url = None
        api_version = None
        secret = None

        if index_section.kind == MLIndexKind.FAISS:
            if index_section.engine is not None:
                is_engine_supported = SUPPORTED_FAISS_ENGINE in str(index_section.engine).lower()
                if not is_engine_supported:
                    raise InvalidFieldInMLIndexException(
                        f"engine type {index_section.engine} is not valid for FAISS index"
                    )

            if index_section.method is not None:
                is_method_supported = SUPPORTED_FAISS_METHOD in str(index_section.method).lower()
                if not is_method_supported:
                    raise InvalidFieldInMLIndexException(
                        f"method {index_section.method} is not valid"
                    )

            store_type = self.__store_type
            url = self.__remote_store_path

        elif index_section.kind == MLIndexKind.ACS:

            if index_section.connection is None:
                raise MissingFieldInMLIndexException(
                    "Index connection is not specified"
                )

            store_type = StoreType.COGNITIVESEARCH

            connection_handler = ConnectionHandlerFactory.get_connection_handler(
                index_section.connection_type
            )
            api_key = self.__get_api_key(
                connection_handler=connection_handler,
                section=index_section
            )
            api_base = self.__get_api_base(
                connection_handler=connection_handler,
                section=index_section
            )
            api_version = self.__get_api_version(
                connection_handler=connection_handler,
                section=index_section
            )
            if api_version is None:
                api_version = ACS_API_VERSION

            url = api_base
            self.__collection = index_section.index
            secret = api_key

            if index_section.field_mapping:
                self.__text_field = index_section.field_mapping.content
                self.__vector_field = index_section.field_mapping.embedding
        else:
            raise InvalidFieldInMLIndexException(
                f"Index kind {index_section.kind} is not valid"
            )

        search_tool_config = VectorSearchToolConfig(
            store_type=store_type,
            store_path=store_path,
            url=url,
            api_version=api_version,
            secret=secret,
            logging_config=self.__logging_config
        )

        return search_tool_config.generate_store_service_config()

    def __set_entity_metadata(self, entity: SearchResultEntity) -> SearchResultEntity:

        if self.__ml_index.index.kind != MLIndexKind.ACS or (self.__ml_index.index.field_mapping is None):
            return entity

        metadata_field = self.__ml_index.index.field_mapping.metadata
        if metadata_field is None:
            return entity
        if metadata_field.endswith(METADATA_JSON_TYPE_SUFFIX):
            entity.metadata = json.loads(entity.original_entity[metadata_field])
        else:
            entity.metadata = entity.original_entity[metadata_field]

        return entity

    @staticmethod
    def __get_embedding_api_type(
            connection_handler: ConnectionHandler,
            section: EmbeddingsSection
    ) -> OpenAIApiType:
        api_type = connection_handler.get_api_type(section.connection)
        if api_type is None:
            api_type = section.api_type
        return OpenAIApiType.from_str(api_type)

    @staticmethod
    def __get_api_key(
        connection_handler: ConnectionHandler,
        section: MLIndexSectionBase
    ) -> str:
        return connection_handler.get_key(section.connection)

    @staticmethod
    def __get_api_base(
        connection_handler: ConnectionHandler,
        section: MLIndexSectionBase
    ) -> str:
        api_base = connection_handler.get_api_base(section.connection)
        if api_base is None:
            api_base = section.api_base
        if api_base is None:
            api_base = section.endpoint
        return api_base

    @staticmethod
    def __get_api_version(
        connection_handler: ConnectionHandler,
        section: MLIndexSectionBase
    ) -> str:
        api_version = connection_handler.get_api_version(section.connection)
        if api_version is None:
            api_version = section.api_version
        return api_version
