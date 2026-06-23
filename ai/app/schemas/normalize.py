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


class NormalizedItem(BaseModel):
    code: str
    name_ko: str
    name_en: str
    confidence: float


class AdditionalTerm(BaseModel):
    text_ko: str
    text_en: str
    confidence: float


class NormalizedInput(BaseModel):
    health_goals: list[NormalizedGoal]
    medications: list[NormalizedItem]
    special_conditions: list[NormalizedItem]
    additional_terms: list[AdditionalTerm] = Field(default_factory=list)


class ClarificationQuestion(BaseModel):
    code: str
    message: str


class NormalizeResponse(BaseModel):
    normalized_input: NormalizedInput
    search_queries: list[str]
    needs_clarification: bool = False
    questions: list[ClarificationQuestion] = Field(default_factory=list)