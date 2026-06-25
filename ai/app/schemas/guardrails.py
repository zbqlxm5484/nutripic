from pydantic import BaseModel, Field

from app.schemas.common import Citation


class InputGuardrailRequest(BaseModel):
    request_id: str
    user_id: int
    task_type: str
    input_text: str
    structured_input: dict = Field(default_factory=dict)


class GuardrailQuestion(BaseModel):
    code: str
    message: str


class InputGuardrailResponse(BaseModel):
    is_allowed: bool
    risk_level: str
    blocked_reason: str | None = None
    safe_message: str | None = None
    needs_clarification: bool = False
    questions: list[GuardrailQuestion] = Field(default_factory=list)


class OutputGuardrailRequest(BaseModel):
    request_id: str
    task_type: str
    content: str
    citations: list[Citation] = Field(default_factory=list)


class OutputGuardrailResponse(BaseModel):
    is_allowed: bool
    risk_level: str
    blocked_reason: str | None = None
    safe_message: str | None = None
    required_fixes: list[str] = Field(default_factory=list)