from http import HTTPStatus

HttpRetryableStatusCodes = [HTTPStatus.REQUEST_TIMEOUT,
                            HTTPStatus.TOO_MANY_REQUESTS,
                            HTTPStatus.BAD_GATEWAY,
                            HTTPStatus.SERVICE_UNAVAILABLE,
                            HTTPStatus.GATEWAY_TIMEOUT]


class EmbeddingSearchRetryableError(Exception):
    pass
