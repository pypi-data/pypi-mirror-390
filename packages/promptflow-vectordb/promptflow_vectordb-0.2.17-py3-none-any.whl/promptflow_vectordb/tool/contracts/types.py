from enum import Enum


class StoreType(str, Enum):
    LOCALFAISS = 'Local Store with FAISS'
    BLOBFAISS = 'Blob Store with FAISS'
    AMLDATASTOREFAISS = 'AML DataStore with FAISS'
    GITHUBFAISS = 'GitHub store with FAISS'
    HTTPFAISS = 'Http store with FAISS'
    DBSERVICE = 'DB Service'
    COGNITIVESEARCH = 'Cognitive Search'
    QDRANT = 'Qdrant'
    WEAVIATE = 'Weaviate'
    PINECONE = 'Pinecone'
    MLINDEX = 'ML Index'

    @property
    def is_file_based(self):
        return self in [
            StoreType.LOCALFAISS,
            StoreType.BLOBFAISS,
            StoreType.AMLDATASTOREFAISS,
            StoreType.GITHUBFAISS,
            StoreType.HTTPFAISS
        ]

    @property
    def is_db_service_based(self):
        return self in [
            StoreType.DBSERVICE,
            StoreType.COGNITIVESEARCH,
            StoreType.QDRANT,
            StoreType.WEAVIATE,
            StoreType.PINECONE
        ]
