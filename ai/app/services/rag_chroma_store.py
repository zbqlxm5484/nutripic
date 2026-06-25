from pathlib import Path
from typing import Any

from app.core.config import settings
from app.schemas.rag import RagSearchResult
from app.services.rag_vector_store import (
    DEFAULT_SCORE_THRESHOLD,
    MAX_TOP_K,
    RagVectorStoreUnavailable,
    build_searchable_text,
    embed_text,
    normalize_top_k,
)


def write_chroma_index(documents: list[dict[str, Any]]) -> None:
    collection = reset_collection()

    ids = [document["document_id"] for document in documents]
    collection.add(
        ids=ids,
        documents=[document["content"] for document in documents],
        embeddings=[embed_text_as_dense(build_searchable_text(document)) for document in documents],
        metadatas=[build_chroma_metadata(document) for document in documents],
    )


def search_chroma_index(
    *,
    query_text: str,
    source_types: set[str],
    top_k: int,
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
) -> list[RagSearchResult]:
    query_embedding = embed_text_as_dense(query_text)
    if not any(query_embedding):
        return []

    collection = get_collection()
    where = build_where_filter(source_types)
    query_kwargs: dict[str, Any] = {
        "query_embeddings": [query_embedding],
        "n_results": min(normalize_top_k(top_k), MAX_TOP_K),
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        query_kwargs["where"] = where

    try:
        raw_results = collection.query(**query_kwargs)
    except Exception as exc:
        raise RagVectorStoreUnavailable("Chroma query failed.") from exc

    return parse_chroma_results(raw_results, score_threshold)


def get_collection():
    client = get_client()
    try:
        return client.get_or_create_collection(
            settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
    except Exception as exc:
        raise RagVectorStoreUnavailable("Chroma collection is not available.") from exc


def reset_collection():
    client = get_client()
    try:
        try:
            client.delete_collection(settings.chroma_collection_name)
        except Exception:
            pass
        return client.get_or_create_collection(
            settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
    except Exception as exc:
        raise RagVectorStoreUnavailable("Chroma collection could not be reset.") from exc


def get_client():
    try:
        import chromadb
    except ImportError as exc:
        raise RagVectorStoreUnavailable("chromadb is not installed.") from exc

    try:
        persist_dir = Path(settings.chroma_persist_dir)
        return chromadb.PersistentClient(path=str(persist_dir))
    except Exception as exc:
        raise RagVectorStoreUnavailable("Chroma client is not available.") from exc


def build_chroma_metadata(document: dict[str, Any]) -> dict[str, Any]:
    metadata = document.get("metadata", {})
    chroma_metadata = {
        "document_id": document["document_id"],
        "source_type": document["source_type"],
        "source_name": document["source_name"],
        "title": document["title"],
    }

    for key, value in metadata.items():
        if value is None:
            continue
        if isinstance(value, str | int | float | bool):
            chroma_metadata[key] = value
        elif isinstance(value, list):
            chroma_metadata[key] = ", ".join(str(item) for item in value)
        elif isinstance(value, dict):
            chroma_metadata[key] = str(value)
        else:
            chroma_metadata[key] = str(value)

    return chroma_metadata


def build_where_filter(source_types: set[str]) -> dict[str, Any]:
    if not source_types:
        return {}
    if len(source_types) == 1:
        return {"source_type": next(iter(source_types))}

    return {"source_type": {"$in": sorted(source_types)}}


def parse_chroma_results(
    raw_results: dict[str, Any],
    score_threshold: float,
) -> list[RagSearchResult]:
    ids = raw_results.get("ids", [[]])[0]
    documents = raw_results.get("documents", [[]])[0]
    metadatas = raw_results.get("metadatas", [[]])[0]
    distances = raw_results.get("distances", [[]])[0]

    results = []
    for document_id, content, metadata, distance in zip(ids, documents, metadatas, distances):
        score = distance_to_score(distance)
        if score < score_threshold:
            continue

        metadata = metadata or {}
        results.append(
            RagSearchResult(
                document_id=metadata.get("document_id", document_id),
                source_type=metadata.get("source_type", ""),
                source_name=metadata.get("source_name", ""),
                title=metadata.get("title", ""),
                content=content or "",
                score=score,
                metadata={key: value for key, value in metadata.items() if key not in {"document_id", "source_type", "source_name", "title"}},
            )
        )

    return results


def distance_to_score(distance: float | int | None) -> float:
    if distance is None:
        return 0.0

    return round(max(0.0, min(0.99, 1.0 - float(distance))), 4)


def embed_text_as_dense(text: str) -> list[float]:
    dense = [0.0] * 512
    for index, weight in embed_text(text):
        dense[int(index)] = float(weight)

    return dense
