from promptflow.exceptions import (
    SystemErrorException,
    UserErrorException,
    ErrorTarget
)
from ...core.contracts.exceptions import (
    EmbeddingStoreException,
    ErrorType
)
from ...core.utils.common_utils import CommonUtils


class PromptflowExceptionErrorCodeGenerator:

    def __init__(
        self,
        embeddingstore_exception: Exception
    ):
        self._embeddingstore_exception = embeddingstore_exception
        self._error_codes = self._generate_error_codes()

    @property
    def error_codes(self):
        return self._error_codes

    def _generate_error_codes(self):

        if isinstance(self._embeddingstore_exception, EmbeddingStoreException):
            embeddingstore_error_codes = self._embeddingstore_exception.error_codes
            if self._embeddingstore_exception.error_type == ErrorType.USER_ERROR:
                base_promptflow_exception = UserErrorException()
            else:
                base_promptflow_exception = SystemErrorException()
            if len(embeddingstore_error_codes) > 0:
                error_codes = base_promptflow_exception.error_codes + embeddingstore_error_codes[1:]
            else:
                error_codes = base_promptflow_exception.error_codes
        else:
            base_promptflow_exception = SystemErrorException()
            error_codes = base_promptflow_exception.error_codes

        return error_codes


class PromptflowVectorDBSystemErrorException(
    PromptflowExceptionErrorCodeGenerator,
    SystemErrorException
):

    def __init__(
        self,
        embeddingstore_exception: Exception
    ):
        SystemErrorException.__init__(
            self,
            message=str(embeddingstore_exception),
            target=ErrorTarget.TOOL,
            module=CommonUtils.get_package_name_to_level(
                package=__package__,
                level=1
            )
        )
        PromptflowExceptionErrorCodeGenerator.__init__(self, embeddingstore_exception)

        if isinstance(embeddingstore_exception, EmbeddingStoreException):
            self.__class__.__name__ = embeddingstore_exception._exception_class_name
        else:
            self.__class__.__name__ = embeddingstore_exception.__class__.__name__


class PromptflowVectorDBUserErrorException(
    PromptflowExceptionErrorCodeGenerator,
    UserErrorException
):

    def __init__(
        self,
        embeddingstore_exception: Exception
    ):
        UserErrorException.__init__(
            self,
            message=str(embeddingstore_exception),
            target=ErrorTarget.TOOL,
            module=CommonUtils.get_package_name_to_level(
                package=__package__,
                level=1
            )
        )
        PromptflowExceptionErrorCodeGenerator.__init__(self, embeddingstore_exception)

        if isinstance(embeddingstore_exception, EmbeddingStoreException):
            self.__class__.__name__ = embeddingstore_exception._exception_class_name
        else:
            self.__class__.__name__ = embeddingstore_exception.__class__.__name__


class PromptflowExceptionConverter:

    @staticmethod
    def convert(
        embeddingstore_exception: Exception
    ):
        if (
            isinstance(embeddingstore_exception, EmbeddingStoreException)
            and embeddingstore_exception.error_type == ErrorType.USER_ERROR
        ):
            return PromptflowVectorDBUserErrorException(
                embeddingstore_exception
            )
        else:
            return PromptflowVectorDBSystemErrorException(
                embeddingstore_exception
            )
