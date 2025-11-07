from dataclasses import dataclass, asdict
from typing import List, Union


@dataclass
class SearchResultEntity:
    text: str = None
    vector: List[float] = None
    score: float = None
    original_entity: dict = None
    metadata: Union[dict, str] = None
    additional_fields: dict = None

    def as_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(dict_object: dict):
        return SearchResultEntity(**dict_object)


@dataclass
class SearchResultDocument:
    page_content: str = None
    score: float = None
    metadata: Union[dict, str] = None
    additional_fields: dict = None
