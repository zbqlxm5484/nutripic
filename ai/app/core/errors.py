from fastapi import Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(self, status_code: int, error_code: str, message: str, request_id: str | None = None):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.request_id = request_id


def create_error_body(error_code: str, message: str, request_id: str | None = None):
    return {
        "error_code": error_code,
        "message": message,
        "details": {
            "request_id": request_id,
        },
    }


async def api_error_handler(request: Request, exc: ApiError):
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_body(
            error_code=exc.error_code,
            message=exc.message,
            request_id=exc.request_id,
        ),
    )


def raise_api_error(status_code: int, error_code: str, message: str, request_id: str | None = None):
    raise ApiError(
        status_code=status_code,
        error_code=error_code,
        message=message,
        request_id=request_id,
    )
