from fastapi import Header

from app.core.config import settings
from app.core.errors import raise_api_error


def verify_internal_api_key(
    x_internal_api_key: str | None = Header(default=None, alias="X-Internal-Api-Key"),
    x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
):
    if x_internal_api_key != settings.ai_internal_api_key:
        raise_api_error(
            status_code=401,
            error_code="internal_authentication_failed",
            message="서버 간 인증에 실패했습니다.",
            request_id=x_request_id,
        )

    return x_request_id