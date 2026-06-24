from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import Citation, GuardrailResult


class NormalizedGoal(BaseModel):
    code: str
    name_ko: str
    name_en: str
    priority: int
    confidence: float | None = None


class NormalizedItem(BaseModel):
    code: str
    name_ko: str
    name_en: str
    confidence: float | None = None


class AdditionalTerm(BaseModel):
    text_ko: str
    text_en: str
    confidence: float | None = None


class ReportNormalizedInput(BaseModel):
    age: int
    gender: str
    health_goals: list[NormalizedGoal]
    medications: list[NormalizedItem] = Field(default_factory=list)
    special_conditions: list[NormalizedItem] = Field(default_factory=list)
    additional_notes: str | None = None
    additional_terms: list[AdditionalTerm] = Field(default_factory=list)


class RagContext(BaseModel):
    document_id: str
    source_type: str
    title: str
    content: str
    source_name: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReportGenerateRequest(BaseModel):
    request_id: str
    user_id: int
    normalized_input: ReportNormalizedInput
    rag_contexts: list[RagContext] = Field(default_factory=list)


class InputSummary(BaseModel):
    age: int
    gender: str
    health_goals: list[str]
    medications: list[str]
    special_conditions: list[str]
    additional_notes: str | None = None


class RecommendedIngredient(BaseModel):
    name_ko: str
    name_en: str
    normalized_name: str
    reason: str
    expected_effects: list[str] = Field(default_factory=list)
    recommended_dosage: str
    side_effects: list[str] = Field(default_factory=list)
    precautions: list[str] = Field(default_factory=list)


class ReportGenerateResponse(BaseModel):
    status: str
    title: str
    input_summary: InputSummary
    recommended_ingredients: list[RecommendedIngredient]
    lifestyle_tips: list[str] = Field(default_factory=list)
    disclaimer: str
    citations: list[Citation] = Field(default_factory=list)
    guardrail_result: GuardrailResult