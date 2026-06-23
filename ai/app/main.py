from fastapi import FastAPI

from app.api.routes import guardrails, normalize
from app.core.errors import ApiError, api_error_handler

app = FastAPI(title="Neutripic AI Server")
app.add_exception_handler(ApiError, api_error_handler)

app.include_router(guardrails.router, prefix="/internal/ai/v1")
app.include_router(normalize.router, prefix="/internal/ai/v1")
