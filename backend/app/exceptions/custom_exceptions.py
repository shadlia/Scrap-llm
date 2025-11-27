from fastapi import status


class BaseCustomException(Exception):
    """Base exception for all custom exceptions"""

    def __init__(
        self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(BaseCustomException):
    """Exception raised when a resource is not found"""

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class ValidationException(BaseCustomException):
    """Exception raised when validation fails"""

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class UnauthorizedException(BaseCustomException):
    """Exception raised when authentication fails"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class CrawlingException(BaseCustomException):
    """Exception raised when crawling fails"""

    def __init__(self, url: str, message: str):
        super().__init__(
            f"Failed to crawl {url}: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class FilteringException(BaseCustomException):
    """Exception raised when URL filtering fails"""

    def __init__(self, message: str):
        super().__init__(
            f"Failed to filter URLs: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class ExtractionException(BaseCustomException):
    """Exception raised when product extraction fails"""

    def __init__(self, url: str, message: str):
        super().__init__(
            f"Failed to extract product from {url}: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class TaskQueueException(BaseCustomException):
    """Exception raised when task queue operations fail"""

    def __init__(self, task_type: str, message: str):
        super().__init__(
            f"Failed to queue {task_type} task: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class StorageException(BaseCustomException):
    """Exception raised when Redis storage operations fail"""

    def __init__(self, operation: str, message: str):
        super().__init__(
            f"Storage operation '{operation}' failed: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class BackendNotificationException(BaseCustomException):
    """Exception raised when notifying the backend fails"""

    def __init__(self, deal_id: str, message: str):
        super().__init__(
            f"Failed to notify backend for deal {deal_id}: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class EmptyResultException(BaseCustomException):
    """Exception raised when no results are found"""

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)
