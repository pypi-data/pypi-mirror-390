from dataclasses import dataclass, asdict, field, is_dataclass
from typing import List

from ...core.contracts import StorageType


@dataclass
class RequestObj:
    def add(self, key: str, value: str):
        self.__dict__[key] = value

    def update(self, kvs: dict):
        if kvs is not None:
            self.__dict__.update(kvs)

    def as_dict(self):
        dict_obj = {}

        for key in self.__dict__:
            if is_dataclass(self.__dict__[key]):
                dict_obj[key] = asdict(self.__dict__[key])
            else:
                dict_obj[key] = self.__dict__[key]

        return dict_obj

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __contains__(self, key: str):
        return key in self.__dict__


@dataclass
class LoadRequestObj(RequestObj):
    store_identifier: str = None
    storage_type: StorageType = StorageType.LOCAL
    credential: str = None


@dataclass
class SearchRequestObj(LoadRequestObj):
    query_embedding: List[float] = None
    top_k: int = 5


@dataclass
class CognitiveSearchVectorObj(RequestObj):
    value: List[float] = None
    fields: str = None
    k: int = 5


@dataclass
class CognitiveSearchRequestObj(RequestObj):
    vectors: List[CognitiveSearchVectorObj] = None


@dataclass
class QdrantRequestObj(RequestObj):
    vector: List[float] = None
    filter: dict = None
    params: dict = None
    with_vectors: bool = True
    with_payload: bool = True
    limit: int = 5


@dataclass
class WeaviateRequestObj(RequestObj):
    class_name: str = None
    vector: List[float] = None
    limit: int = 1
    text_field: str = None
    additional_fields: List[str] = field(
        default_factory=lambda: ["certainty", "distance", "vector"]
    )
    graphql_pattern = """{{
              Get{{
                {class_name}(
                  nearVector: {{
                    vector:  {vector}
                  }}
                  limit: {limit}
                ){{
                  {text_field}
                  _additional {{
                    {additional_fields}
                  }}
                }}
              }}
            }}
            """

    def to_body(self):
        graphql = self.graphql_pattern.format(
            class_name=self.class_name,
            vector=str(self.vector),
            text_field=self.text_field if self.text_field is not None else "",
            limit=self.limit,
            additional_fields=str.join(" ", self.additional_fields),
        )
        body = {"query": graphql}
        return body


@dataclass
class PineconeSearchRequestObj(RequestObj):
    vector: List[float] = None
    namespace: str = None
    topK: int = 5
    includeMetadata: bool = None
    includeValues: bool = True


@dataclass
class MilvusSearchRequestObj(RequestObj):
    collectionName: str = None
    limit: int = 5
    vector: List[float] = None
    outputFields: List[str] = None
