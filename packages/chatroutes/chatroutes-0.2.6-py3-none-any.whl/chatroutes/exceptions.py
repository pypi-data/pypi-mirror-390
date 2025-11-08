from typing import Any, Optional


class ChatRoutesError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        code: Optional[str] = None,
        details: Optional[Any] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details


class AuthenticationError(ChatRoutesError):
    def __init__(self, message: str = "Authentication failed", details: Optional[Any] = None):
        super().__init__(message, 401, "AUTHENTICATION_ERROR", details)


class RateLimitError(ChatRoutesError):
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Any] = None
    ):
        super().__init__(message, 429, "RATE_LIMIT_EXCEEDED", details)
        self.retry_after = retry_after


class ValidationError(ChatRoutesError):
    def __init__(self, message: str = "Validation failed", details: Optional[Any] = None):
        super().__init__(message, 400, "VALIDATION_ERROR", details)


class NotFoundError(ChatRoutesError):
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(message, 404, "NOT_FOUND", details)


class ServerError(ChatRoutesError):
    def __init__(self, message: str = "Internal server error", details: Optional[Any] = None):
        super().__init__(message, 500, "SERVER_ERROR", details)


class NetworkError(ChatRoutesError):
    def __init__(self, message: str = "Network request failed", details: Optional[Any] = None):
        super().__init__(message, 0, "NETWORK_ERROR", details)
