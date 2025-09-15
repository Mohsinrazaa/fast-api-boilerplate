from typing import Any, Optional
from fastapi.responses import JSONResponse

def success_response(message: str = "Success", data: Optional[Any] = None, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "message": message,
            "status_code": status_code,
            "data": data,
        },
    )
def error_response(message: str = "Error", status_code: int = 400, data: Optional[Any] = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "message": message,
            "status_code": status_code,
            "data": data,
        },
    )


