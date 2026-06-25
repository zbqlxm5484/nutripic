from typing import Any

from pydantic import BaseModel, Field


class CodeNamePriority(BaseModel):
    code: str
    name: str
    priority: int | None = None


class CodeName(BaseModel):
    code: str
    name: str


class NormalizeRequest(BaseModel):
    request_id: str
    age: int
    gender: str
    health_goals: list[CodeNamePriority]
    medications: list[CodeName] = Field(default_factory=list)
    special_conditions: list[CodeName] = Field(default_factory=list)
    additional_notes: str | None = None


class NormalizedGoal(BaseModel):
    code: str
    name_ko: str
    name_en: str
    priority: int
    confidence: float
    normalized_name: str | None = None
    term_type: str | None = None
    source_ids: dict[str, list[str]] = Field(default_factory=dict)


class NormalizedItem(BaseModel):
    code: str
    name_ko: str
    name_en: str
    confidence: float
    normalized_name: str | None = None
    term_type: str | None = None
    source_ids: dict[str, list[str]] = Field(default_factory=dict)


class AdditionalTerm(BaseModel):
    text_ko: str
    text_en: str
    confidence: float
    normalized_name: str | None = None
    term_type: str | None = None
    source_ids: dict[str, list[str]] = Field(default_factory=dict)


class NormalizedInput(BaseModel):
    health_goals: list[NormalizedGoal]
    medications: list[NormalizedItem]
    special_conditions: list[NormalizedItem]
    additional_terms: list[AdditionalTerm] = Field(default_factory=list)


class ClarificationQuestion(BaseModel):
    code: str
    message: str


class RagQueryBundle(BaseModel):
    idisk: dict[str, Any] = Field(default_factory=dict)
    mfds: dict[str, Any] = Field(default_factory=dict)
    iherb: dict[str, Any] = Field(default_factory=dict)
    text_queries: list[str] = Field(default_factory=list)


class NormalizeResponse(BaseModel):
    normalized_input: NormalizedInput
    search_queries: list[str]
    rag_query_bundle: RagQueryBundle = Field(default_factory=RagQueryBundle)
    needs_clarification: bool = False
    questions: list[ClarificationQuestion] = Field(default_factory=list)
