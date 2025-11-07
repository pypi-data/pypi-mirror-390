from ....core.logging.utils import LoggingUtils
from ....core.contracts import LoggingMessageTemplate
from ....core.contracts.exceptions import UnsupportedFeatureException
from ...contracts import StoreServiceConfig
from ...contracts import AgentType
from .agent import Agent


class UnsupportedAgentTypeException(UnsupportedFeatureException):
    pass


class AgentFactory:

    @staticmethod
    def get_agent(config: StoreServiceConfig) -> Agent:

        agent: Agent = None

        if config.agent_type == AgentType.FILEBASED:
            from .file_based_agent import FileBasedAgent
            agent = FileBasedAgent(config)
        elif config.agent_type == AgentType.RESTCLIENTBASED:
            from .rest_based_agent import RestBasedAgent
            agent = RestBasedAgent(config)
        elif config.agent_type == AgentType.COGNITIVESEARCHBASED:
            from .cog_search_client import CogSearchClient
            agent = CogSearchClient(config)
        elif config.agent_type == AgentType.QDRANTBASED:
            from .qdrant_client import QdrantClient
            agent = QdrantClient(config)
        elif config.agent_type == AgentType.WEAVIATEBASED:
            from .weaviate_client import WeaviateClient
            agent = WeaviateClient(config)
        elif config.agent_type == AgentType.PINECONECLIENTBASED:
            from .pinecone_client import PineconeClient
            agent = PineconeClient(config)
        elif config.agent_type == AgentType.MILVUSCLIENTBASED:
            from .milvus_client import MilvusClient
            agent = MilvusClient(config)
        else:
            raise UnsupportedAgentTypeException(
                f"The {config.agent_type} has not been implemented yet."
            )

        LoggingUtils.sdk_logger(__package__, config).info(
            LoggingMessageTemplate.COMPONENT_INITIALIZED.format(
                component_name=Agent.__name__,
                instance_type=agent.__class__.__name__
            )
        )

        return agent
