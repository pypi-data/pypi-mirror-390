import ast
import datetime
import uuid
import numbers
from typing import List
from dataclasses import dataclass, fields


class CommonUtils:

    @staticmethod
    def is_number_list(obj: object):
        return isinstance(obj, List) and all(isinstance(x, numbers.Number) for x in obj)

    @staticmethod
    def try_get_number_list(input: object) -> list:
        try:
            if CommonUtils.is_number_list(input):
                return input
            vector = ast.literal_eval(input)
            if CommonUtils.is_number_list(vector):
                return vector
        except Exception:
            pass
        return None

    @staticmethod
    def generate_timestamp_based_unique_id() -> str:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        guid = str(uuid.uuid4()).replace("-", "")
        unique_key = f"{timestamp}_{guid}"
        return unique_key

    @staticmethod
    def get_utc_now_standard_format_with_zone() -> str:
        return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @staticmethod
    def get_package_name_to_level(package: str, level: int = 1) -> str:
        try:
            package_parts = package.split('.')
            if len(package_parts) <= level:
                return package
            return '.'.join(package_parts[:level])
        except Exception:
            return 'Unknown Package'


@dataclass
class HashableDataclass:

    def to_tuple(self):
        data_tuple = tuple(getattr(self, field.name) for field in fields(self))
        return data_tuple
