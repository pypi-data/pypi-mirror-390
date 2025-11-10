class UnsplashClientException(Exception):
    def __init__(self, message: str, query: str | None = None) -> None:
        self.query = query
        super().__init__(message)


class UnsplashTimeoutException(UnsplashClientException):
    pass


class UnsplashAuthenticationException(UnsplashClientException):
    pass


class UnsplashRateLimitException(UnsplashClientException):
    def __init__(
        self, message: str, query: str | None = None, retry_after: int | None = None
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message, query)


class UnsplashNotFoundException(UnsplashClientException):
    pass


class UnsplashServerException(UnsplashClientException):
    def __init__(
        self, message: str, query: str | None = None, status_code: int | None = None
    ) -> None:
        self.status_code = status_code
        super().__init__(message, query)


class UnsplashClientException(UnsplashClientException):
    def __init__(
        self, message: str, query: str | None = None, status_code: int | None = None
    ) -> None:
        self.status_code = status_code
        super().__init__(message, query)


class UnsplashValidationException(UnsplashClientException):
    pass
