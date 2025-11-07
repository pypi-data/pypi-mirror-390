from enum import Enum


class AgentType(str, Enum):
    FILEBASED = 'FileBased'
    RESTCLIENTBASED = 'RestClientBased'
    COGNITIVESEARCHBASED = 'CognitiveSearchBased'
    QDRANTBASED = 'QdrantBased'
    WEAVIATEBASED = 'WeaviateBased'
    PINECONECLIENTBASED = 'PineconeClientBased'
    MILVUSCLIENTBASED = 'MilvusClientBased'
