from app.core.config import settings
from app.core.errors import raise_api_error
from app.schemas.rag import RagSearchRequest, RagSearchResponse
from app.services.rag_chroma_store import search_chroma_index
from app.services.rag_vector_store import (
    RagVectorStoreUnavailable,
    search_vector_index,
)


def search_rag(payload: RagSearchRequest) -> RagSearchResponse:
    try:
        results = search_selected_backend(
            query_text=" ".join(payload.search_queries),
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

    return RagSearchResponse(results=results)


def search_selected_backend(*, query_text: str, source_types: set[str], top_k: int):
    if settings.rag_vector_backend == "chroma":
        return search_chroma_index(
            query_text=query_text,
            source_types=source_types,
            top_k=top_k,
        )

    if settings.rag_vector_backend == "local_json":
        return search_vector_index(
            query_text=query_text,
            source_types=source_types,
            top_k=top_k,
        )

    raise RagVectorStoreUnavailable("Unsupported RAG vector backend.")
