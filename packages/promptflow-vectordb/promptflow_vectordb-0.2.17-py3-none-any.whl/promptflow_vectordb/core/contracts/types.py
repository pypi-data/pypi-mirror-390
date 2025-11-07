from enum import Enum


class StorageType(str, Enum):
    INMEMORY = 'InMemory'
    LOCAL = 'Local'
    BLOBSTORAGE = 'BlobStorage'
    AMLDATASTORE = 'AMLDataStore'
    HTTP = 'HTTP'
    GITHUBFOLDER = 'GithubFolder'
    DBSERVICE = 'DBService'

    @property
    def is_remote_file_based(self):
        return self in [
            StorageType.BLOBSTORAGE,
            StorageType.AMLDATASTORE,
            StorageType.HTTP,
            StorageType.GITHUBFOLDER
        ]


class IndexType(str, Enum):
    FLATL2 = "FlatL2"


class EngineType(str, Enum):
    LANGCHAIN = "LangChain"


class EmbeddingModelType(str, Enum):
    NONE = "None"
    OPENAI = "OpenAI"
    AOAI = "AOAI"
    CUSTOMIZED = "Customized"


class OpenAIApiType(str, Enum):
    AZURE = "azure"
    OPENAI = "openai"

    @staticmethod
    def from_str(label: str):
        if label.lower() == "azure":
            return OpenAIApiType.AZURE
        elif label.lower() in ("open_ai", "openai"):
            return OpenAIApiType.OPENAI
        else:
            raise ValueError(
                (
                    "The API type provided is invalid.",
                    "Please select one of the supported API types: 'azure', 'openai', 'open_ai'"
                )
            )


class SecretSourceType(str, Enum):
    PLAIN = "Plain"
    AKV = "AzureKeyVault"
    ENV = "EnvironmentVariables"
