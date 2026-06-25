from typing import Any

from app.core.config import settings
from app.core.errors import raise_api_error
from app.schemas.rag import RagSearchRequest, RagSearchResponse
from app.services.rag_chroma_store import search_chroma_index
from app.services.rag_vector_store import (
    RagVectorStoreUnavailable,
    search_vector_index,
)

RAG_MIN_SCORE = 0.5  # 이 값 미만의 최고점수이면 needs_clarification 반환


def search_rag(payload: RagSearchRequest) -> RagSearchResponse:
    try:
        results = search_selected_backend(
            query_text=" ".join(payload.search_queries),
            query_bundle=payload.rag_query_bundle,
            source_types=set(payload.filters.source_types or []),
            top_k=payload.filters.top_k,
        )
    except RagVectorStoreUnavailable:
        raise_api_error(
            status_code=503,
            error_code="rag_service_unavailable",
            message="RAG 검색 인덱스를 사용할 수 없습니다.",
            request_id=payload.request_id,
        )

    rag_response = RagSearchResponse(results=results)
    _annotate_rag_quality(rag_response)
    return rag_response


def _annotate_rag_quality(response: RagSearchResponse) -> None:
    """
    검색 결과 품질을 평가해 needs_clarification 여부를 표시한다.
    결과가 없거나 최고 score가 RAG_MIN_SCORE 미만이면 True를 설정한다.
    """
    if not response.results:
        response.needs_clarification = True
        response.low_rag_score = True
        return

    max_score = max(r.score for r in response.results)
    if max_score < RAG_MIN_SCORE:
        response.needs_clarification = True
        response.low_rag_score = True
    else:
        response.needs_clarification = False
        response.low_rag_score = False


def search_selected_backend(
    *,
    query_text: str,
    query_bundle: dict[str, Any],
    source_types: set[str],
    top_k: int,
):
    if settings.rag_vector_backend == "chroma":
        return search_chroma_index(
            query_text=query_text,
            source_types=source_types,
            top_k=top_k,
        )

    if settings.rag_vector_backend == "local_json":
        return search_vector_index(
            query_text=query_text,
            query_bundle=query_bundle,
            source_types=source_types,
            top_k=top_k,
        )

    raise RagVectorStoreUnavailable("Unsupported RAG vector backend.")
