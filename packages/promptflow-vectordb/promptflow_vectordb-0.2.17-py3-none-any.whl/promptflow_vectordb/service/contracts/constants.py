class RequestType:
    LOAD = 'load'
    SEARCH = 'search'
    CLEAR = 'clear'
    METADATA = 'metadata'


class HttpCustomHeaders:
    REQUEST_ID = 'X-Request-ID'


class ErrorMessage:
    STORE_NOT_FOUND = 'store with the given identifier can not be found'
    FILE_SIZE_EXCEEDED = 'the store exceeds the size limit and can not be loaded'
    INVALID_VECTOR_SEARCH_INPUT = 'invalid input for vector search'
    AUTHENTICATION_FAILED = 'authentication failed for accessing the remote store'
    INTERNAL_SERVER_ERROR = 'internal server error'


class ResultMessage:
    STORE_LOADED = 'store loaded successfully'
    STORES_CLEARED = 'stores cleared successfully'
