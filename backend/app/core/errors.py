import logging
from dataclasses import dataclass

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


@dataclass
class ErrorCode:
    AUTH_ERROR: str = "auth_error"
    VALIDATION_ERROR: str = "validation_error"
    RESOURCE_ERROR: str = "resource_error"
    SYSTEM_ERROR: str = "system_error"


class AppError(Exception):
    def __init__(self, message: str, code: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


def _error_payload(message: str, code: str) -> dict[str, str]:
    return {"error_code": code, "message": message}


def register_error_handlers(app: FastAPI, logger: logging.Logger) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "request.app_error",
            extra={"extra_fields": {"error_code": exc.code, "message": exc.message}},
        )
        return JSONResponse(
            status_code=exc.status_code, content=_error_payload(exc.message, exc.code)
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning(
            "request.validation_error",
            extra={
                "extra_fields": {
                    "error_code": ErrorCode.VALIDATION_ERROR,
                    "details": str(exc.errors()),
                }
            },
        )
        return JSONResponse(
            status_code=422,
            content=_error_payload(
                "Request validation failed.", ErrorCode.VALIDATION_ERROR
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "request.unexpected_error",
            extra={
                "extra_fields": {
                    "error_code": ErrorCode.SYSTEM_ERROR,
                    "exception_type": type(exc).__name__,
                }
            },
        )
        return JSONResponse(
            status_code=500,
            content=_error_payload(
                "Internal server error. Please retry later.", ErrorCode.SYSTEM_ERROR
            ),
        )
