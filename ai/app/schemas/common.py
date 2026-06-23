from pydantic import BaseModel, Field


class ErrorDetails(BaseModel):
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: ErrorDetails = Field(default_factory=ErrorDetails)


class Citation(BaseModel):
    source_type: str
    source_name: str | None = None
    document_id: str


class GuardrailResult(BaseModel):
    is_allowed: bool
    risk_level: str