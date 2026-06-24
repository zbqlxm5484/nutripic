import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.schemas.rag import RagSearchRequest, RagSearchResponse, RagSearchResult

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "rag_documents.json"
DEFAULT_SCORE_THRESHOLD = 0.1
MAX_TOP_K = 20


def search_rag(payload: RagSearchRequest) -> RagSearchResponse:
    source_types = set(payload.filters.source_types or [])
    top_k = normalize_top_k(payload.filters.top_k)
    query_terms = tokenize(" ".join(payload.search_queries))

    scored_results = []

    for document in load_documents():
        if source_types and document.source_type not in source_types:
            continue

        score = calculate_keyword_score(query_terms, document)
        if score < DEFAULT_SCORE_THRESHOLD:
            continue

        scored_results.append(document.model_copy(update={"score": score}))

    scored_results.sort(key=lambda item: item.score, reverse=True)

    return RagSearchResponse(results=scored_results[:top_k])


@lru_cache
def load_documents() -> tuple[RagSearchResult, ...]:
    with DATA_PATH.open(encoding="utf-8") as file:
        raw_documents = json.load(file)

    return tuple(
        RagSearchResult(
            document_id=document["document_id"],
            source_type=document["source_type"],
            source_name=document["source_name"],
            title=document["title"],
            content=document["content"],
            score=0.0,
            metadata=document.get("metadata", {}),
        )
        for document in raw_documents
    )


def calculate_keyword_score(query_terms: list[str], document: RagSearchResult) -> float:
    if not query_terms:
        return 0.0

    searchable_terms = tokenize(build_searchable_text(document))
    if not searchable_terms:
        return 0.0

    searchable_set = set(searchable_terms)
    matched_terms = [term for term in query_terms if term in searchable_set]
    if not matched_terms:
        return 0.0

    coverage_score = len(set(matched_terms)) / len(set(query_terms))
    density_score = len(matched_terms) / max(len(searchable_terms), 1)

    return round(min(0.95, 0.2 + coverage_score * 0.65 + density_score * 0.1), 4)


def build_searchable_text(document: RagSearchResult) -> str:
    metadata = document.metadata
    parts = [
        document.document_id,
        document.source_type,
        document.source_name,
        document.title,
        document.content,
        metadata.get("ingredient_name_ko", ""),
        metadata.get("ingredient_name_en", ""),
        metadata.get("normalized_name", ""),
        *as_text_list(metadata.get("keywords", [])),
        *as_text_list(metadata.get("symptoms", [])),
        *as_text_list(metadata.get("related_ingredients", [])),
        *as_text_list(metadata.get("expected_effects", [])),
        *as_text_list(metadata.get("precautions", [])),
    ]
    return " ".join(part for part in parts if part)


def as_text_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]

    if value:
        return [str(value)]

    return []


def tokenize(text: str) -> list[str]:
    normalized = (
        text.lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace("/", " ")
        .replace(",", " ")
        .replace(".", " ")
        .replace("(", " ")
        .replace(")", " ")
    )
    return [term for term in normalized.split() if term]


def normalize_top_k(top_k: int) -> int:
    if top_k < 1:
        return 1

    return min(top_k, MAX_TOP_K)
