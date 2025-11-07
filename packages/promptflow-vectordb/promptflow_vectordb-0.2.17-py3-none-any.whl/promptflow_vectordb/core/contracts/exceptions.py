from abc import ABC, abstractproperty
from http import HTTPStatus
from typing import List, Any, Dict
from enum import Enum


class ErrorType(str, Enum):
    SYSTEM_ERROR = "SystemError"
    USER_ERROR = "UserError"
    UNKNOWN = "Unknown"


class EmbeddingStoreException(Exception, ABC):

    def __init__(
        self,
        message: str = "",
        inner_exception: Exception = None
    ):
        self._message = str(message)
        self._inner_exception = inner_exception
        self._error_codes = self._generate_error_code()
        self._exception_class_name = self.__class__.__name__
        super().__init__(self._message)

    @property
    def message(self) -> str:
        if self._message:
            return self._message

        return self.__class__.__name__

    @abstractproperty
    def error_type(self) -> ErrorType:
        pass

    @property
    def inner_exception(self) -> Any:
        return self._inner_exception or self.__cause__

    def __str__(self):
        return self.message

    @property
    def error_codes(self) -> List[str]:
        return self._error_codes

    def to_json(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "error_codes": self.error_codes,
            "exception_class_name": self.__class__.__name__
        }

    @classmethod
    def from_json(cls, json_obj: Dict[str, Any]):
        obj = cls(
            message=json_obj.get("message")
        )
        obj._error_codes = json_obj.get("error_codes")
        obj._exception_class_name = json_obj.get("exception_class_name")
        return obj

    def _generate_error_code(self):
        result = []
        for clz in self.__class__.__mro__:
            if clz is EmbeddingStoreException:
                break
            result.append(clz.__name__)
        result.reverse()
        return result


class UserErrorException(EmbeddingStoreException):
    """Exception raised when invalid or unsupported inputs are provided."""

    @property
    def error_type(self) -> ErrorType:
        return ErrorType.USER_ERROR


class SystemErrorException(EmbeddingStoreException):
    """Exception raised when service error is triggered."""

    @property
    def error_type(self) -> ErrorType:
        return ErrorType.SYSTEM_ERROR


class UnknownErrorException(EmbeddingStoreException):
    """Exception raised when unknown error is triggered."""

    @property
    def error_type(self) -> ErrorType:
        return ErrorType.UNKNOWN


class MissingRunningContextException(SystemErrorException):
    pass


class FileSizeExceededException(UserErrorException):
    pass


class FileNotFoundException(UserErrorException):
    pass


class UnsupportedFeatureException(UserErrorException):
    pass


class InvalidInputException(UserErrorException):
    pass


class MissingInputException(UserErrorException):
    pass


class MissingConfigException(MissingInputException):
    pass


class InvalidStoreIdentifierException(InvalidInputException):
    pass


class AuthenticationException(UserErrorException):
    pass


class RemoteResourceAuthenticationException(AuthenticationException):
    def __init__(self, message=None, http_status_code=None):
        super().__init__(message)
        self.http_status_code = http_status_code

    @staticmethod
    def is_http_authentication_failure(http_status_code: HTTPStatus):
        return http_status_code in [
            HTTPStatus.UNAUTHORIZED,
            HTTPStatus.FORBIDDEN
        ]
