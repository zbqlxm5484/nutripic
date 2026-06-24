from pydantic import BaseModel, Field

from app.schemas.common import Citation, GuardrailResult


class ReportIngredientContext(BaseModel):
    name_ko: str
    name_en: str
    normalized_name: str
    precautions: list[str] = Field(default_factory=list)


class ReportContext(BaseModel):
    title: str
    recommended_ingredients: list[ReportIngredientContext] = Field(default_factory=list)
    disclaimer: str


class ChatMessage(BaseModel):
    content: str


class RecentMessage(BaseModel):
    role: str
    content: str


class ChatRespondRequest(BaseModel):
    request_id: str
    user_id: int
    report_id: int
    report_context: ReportContext
    message: ChatMessage
    recent_messages: list[RecentMessage] = Field(default_factory=list)


class ChatRespondResponse(BaseModel):
    content: str
    citations: list[Citation] = Field(default_factory=list)
    guardrail_result: GuardrailResult