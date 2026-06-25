from typing import Any

from pydantic import BaseModel, Field


class RagSearchFilters(BaseModel):
    source_types: list[str] = Field(default_factory=list)
    top_k: int = 8


class RagSearchRequest(BaseModel):
    request_id: str
    search_queries: list[str]
    rag_query_bundle: dict[str, Any] = Field(default_factory=dict)
    filters: RagSearchFilters = Field(default_factory=RagSearchFilters)


class RagSearchResult(BaseModel):
    document_id: str
    source_type: str
    source_name: str
    title: str
    content: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagSearchResponse(BaseModel):
    results: list[RagSearchResult] = Field(default_factory=list)
    needs_clarification: bool = False
    low_rag_score: bool = False