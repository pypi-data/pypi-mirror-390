from dataclasses import dataclass


@dataclass
class Secret:

    name: str = None
    is_resolved: bool = False

    def __init__(self, name: str):
        self.name = name
        self.__value = None
        self.is_resolved = False

    def get_value(self):
        return self.__value

    def resolve(self, value: str = None):
        self.is_resolved = True
        if value is None:
            self.__value = self.name
        else:
            self.__value = value

    def __str__(self):
        return self.get_value() or ''
