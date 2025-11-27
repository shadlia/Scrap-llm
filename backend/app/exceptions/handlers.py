from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .custom_exceptions import (
    BaseCustomException,
    NotFoundException,
    ValidationException,
    UnauthorizedException,
    CrawlingException,
    FilteringException,
    ExtractionException,
    TaskQueueException,
    StorageException,
    BackendNotificationException,
    EmptyResultException,
)


async def custom_exception_handler(request: Request, exc: BaseCustomException):
    """Generic handler for all custom exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
                "code": exc.status_code,
                "path": str(request.url),
            }
        },
    )


def setup_exception_handlers(app: FastAPI):
    """Register all exception handlers"""
    # Register handlers for each custom exception type
    app.add_exception_handler(BaseCustomException, custom_exception_handler)
    app.add_exception_handler(NotFoundException, custom_exception_handler)
    app.add_exception_handler(ValidationException, custom_exception_handler)
    app.add_exception_handler(UnauthorizedException, custom_exception_handler)
    app.add_exception_handler(CrawlingException, custom_exception_handler)
    app.add_exception_handler(FilteringException, custom_exception_handler)
    app.add_exception_handler(ExtractionException, custom_exception_handler)
    app.add_exception_handler(TaskQueueException, custom_exception_handler)
    app.add_exception_handler(StorageException, custom_exception_handler)
    app.add_exception_handler(BackendNotificationException, custom_exception_handler)
    app.add_exception_handler(EmptyResultException, custom_exception_handler)

    # Add handler for unhandled exceptions
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": "An unexpected error occurred",
                    "type": "UnhandledException",
                    "code": 500,
                    "path": str(request.url),
                    "detail": str(exc) if app.debug else None,
                }
            },
        )
