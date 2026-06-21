import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Setup logger for recording exceptions in production logging stdout/files
logger = logging.getLogger("app.exceptions")

class AppException(Exception):
    """
    Base domain exception class.
    Decoupled from HTTP framework layers.
    """
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)

class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=400, detail=detail)

class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(status_code=401, detail=detail)

class ForbiddenException(AppException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=403, detail=detail)

class ValidationException(AppException):
    def __init__(self, detail: str = "Unprocessable entity validation failure"):
        super().__init__(status_code=422, detail=detail)

def setup_exception_handlers(app: FastAPI) -> None:
    """
    Hooks global exception handlers into the FastAPI application.
    Ensures consistent structured JSON error responses.
    """
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        # Log warnings for business exception events
        logger.warning(
            f"Business exception on {request.method} {request.url.path}: "
            f"Status {exc.status_code} - {exc.detail}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Log details of validation mismatches
        logger.info(
            f"Request validation failure on {request.method} {request.url.path}: "
            f"{exc.errors()}"
        )
        # Parse Pydantic validation errors into a clean client-facing details array
        errors = [
            {"loc": " -> ".join(map(str, err["loc"])), "msg": err["msg"], "type": err["type"]}
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "errors": errors
            }
        )

    @app.exception_handler(Exception)
    async def global_unhandled_exception_handler(request: Request, exc: Exception):
        # Critical logs for unexpected system exceptions (e.g. DB connectivity drops, OSError)
        logger.error(
            f"Unhandled system error on {request.method} {request.url.path}: {str(exc)}",
            exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Please try again later."}
        )
