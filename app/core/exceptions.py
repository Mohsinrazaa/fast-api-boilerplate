from typing import Any, Dict

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def http_exception_handler(request: Request, exc: StarletteHTTPException):
    payload: Dict[str, Any] = {
        "detail": exc.detail,
        "status_code": exc.status_code,
        "request_id": getattr(request.state, "request_id", None),
    }
    return JSONResponse(status_code=exc.status_code, content=payload)


def validation_exception_handler(request: Request, exc):
    payload = {
        "detail": exc.errors() if hasattr(exc, "errors") else str(exc),
        "status_code": 422,
        "request_id": getattr(request.state, "request_id", None),
    }
    return JSONResponse(status_code=422, content=payload)


def generic_exception_handler(request: Request, exc: Exception):
    payload = {
        "detail": "Internal Server Error",
        "status_code": 500,
        "request_id": getattr(request.state, "request_id", None),
    }
    return JSONResponse(status_code=500, content=payload)


