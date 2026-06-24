import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from app.schemas.rag import RagSearchResult


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
VECTOR_INDEX_PATH = DATA_DIR / "rag_vector_index.json"
VECTOR_INDEX_SCHEMA_VERSION = 1
EMBEDDING_MODEL_NAME = "local-hashed-token-v1"
EMBEDDING_DIMENSION = 512
DEFAULT_SCORE_THRESHOLD = 0.08
MAX_TOP_K = 20

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "because",
    "by",
    "can",
    "for",
    "from",
    "has",
    "in",
    "is",
    "it",
    "may",
    "of",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "with",
    "without",
}


class RagVectorStoreUnavailable(Exception):
    pass


def write_vector_index(
    documents: list[dict[str, Any]],
    path: Path = VECTOR_INDEX_PATH,
) -> dict[str, Any]:
    index = build_vector_index(documents)
    path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(index, file, ensure_ascii=False, indent=2)

    temp_path.replace(path)

    return index


def build_vector_index(documents: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": VECTOR_INDEX_SCHEMA_VERSION,
        "embedding_model": EMBEDDING_MODEL_NAME,
        "embedding_dimension": EMBEDDING_DIMENSION,
        "documents": [
            {
                "document_id": document["document_id"],
                "source_type": document["source_type"],
                "source_name": document["source_name"],
                "title": document["title"],
                "content": document["content"],
                "metadata": document.get("metadata", {}),
                "terms": tokenize(build_searchable_text(document)),
                "embedding": embed_text(build_searchable_text(document)),
            }
            for document in documents
        ],
    }


def load_vector_documents(path: Path = VECTOR_INDEX_PATH) -> tuple[dict[str, Any], ...]:
    try:
        with path.open(encoding="utf-8") as file:
            index = json.load(file)
    except OSError as exc:
        raise RagVectorStoreUnavailable("RAG vector index is not available.") from exc
    except json.JSONDecodeError as exc:
        raise RagVectorStoreUnavailable("RAG vector index is invalid.") from exc

    validate_vector_index(index)
    return tuple(index["documents"])


def validate_vector_index(index: dict[str, Any]) -> None:
    if index.get("schema_version") != VECTOR_INDEX_SCHEMA_VERSION:
        raise RagVectorStoreUnavailable("RAG vector index schema version is unsupported.")
    if index.get("embedding_model") != EMBEDDING_MODEL_NAME:
        raise RagVectorStoreUnavailable("RAG vector index embedding model is unsupported.")
    if index.get("embedding_dimension") != EMBEDDING_DIMENSION:
        raise RagVectorStoreUnavailable("RAG vector index dimension is unsupported.")
    if not isinstance(index.get("documents"), list):
        raise RagVectorStoreUnavailable("RAG vector index documents are invalid.")


def search_vector_index(
    *,
    query_text: str,
    query_bundle: dict[str, Any] | None = None,
    source_types: set[str],
    top_k: int,
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
) -> list[RagSearchResult]:
    query_terms = tokenize(query_text)
    query_embedding = embed_text(query_text)
    if not query_embedding:
        return []

    scored_results = []
    for document in load_vector_documents():
        if source_types and document["source_type"] not in source_types:
            continue

        if not set(query_terms).intersection(document.get("terms", [])):
            continue

        score = calculate_cosine_score(query_embedding, document.get("embedding", []))
        score = round(
            min(0.99, score + calculate_metadata_boost(query_terms, document, query_bundle)),
            4,
        )
        if score < score_threshold:
            continue

        scored_results.append(
            RagSearchResult(
                document_id=document["document_id"],
                source_type=document["source_type"],
                source_name=document["source_name"],
                title=document["title"],
                content=document["content"],
                score=score,
                metadata=document.get("metadata", {}),
            )
        )

    scored_results.sort(key=lambda item: item.score, reverse=True)
    return scored_results[:normalize_top_k(top_k)]


def calculate_metadata_boost(
    query_terms: list[str],
    document: dict[str, Any],
    query_bundle: dict[str, Any] | None = None,
) -> float:
    metadata = document.get("metadata", {})
    query_set = set(query_terms)
    boost = 0.0

    if query_set.intersection(tokenize(str(metadata.get("target_label", "")))):
        boost += 0.09
    if query_set.intersection(tokenize(str(metadata.get("dsi_name", "")))):
        boost += 0.03
    if query_set.intersection(tokenize(str(document.get("title", "")))):
        boost += 0.02

    if document.get("source_type") == "idisk":
        boost += calculate_idisk_query_bundle_boost(metadata, query_bundle or {})

    return boost


def calculate_idisk_query_bundle_boost(
    metadata: dict[str, Any],
    query_bundle: dict[str, Any],
) -> float:
    idisk_bundle = query_bundle.get("idisk") or {}
    boost = 0.0

    if metadata.get("dsi_id") in as_string_set(idisk_bundle.get("ingredient_ids", [])):
        boost += 0.12
    if metadata.get("disease_id") in as_string_set(idisk_bundle.get("condition_ids", [])):
        boost += 0.12
    if metadata.get("target_id") in as_string_set(idisk_bundle.get("drug_ids", [])):
        boost += 0.12
    if metadata.get("relation") in as_string_set(idisk_bundle.get("relation_targets", [])):
        boost += 0.05

    return boost


def as_string_set(value: Any) -> set[str]:
    if isinstance(value, list):
        return {str(item) for item in value}
    if value:
        return {str(value)}

    return set()


def calculate_cosine_score(
    query_embedding: list[list[float]],
    document_embedding: list[list[float]],
) -> float:
    query_weights = {int(index): weight for index, weight in query_embedding}
    document_weights = {int(index): weight for index, weight in document_embedding}

    score = sum(
        weight * document_weights.get(index, 0.0)
        for index, weight in query_weights.items()
    )
    return round(min(0.99, score), 4)


def embed_text(text: str) -> list[list[float]]:
    terms = tokenize(text)
    if not terms:
        return []

    term_counts = Counter(terms)
    buckets: dict[int, float] = {}
    for term, count in term_counts.items():
        bucket = stable_hash(term) % EMBEDDING_DIMENSION
        buckets[bucket] = buckets.get(bucket, 0.0) + 1.0 + math.log(count)

    norm = math.sqrt(sum(weight * weight for weight in buckets.values()))
    if norm == 0:
        return []

    return [
        [index, round(weight / norm, 6)]
        for index, weight in sorted(buckets.items())
    ]


def stable_hash(value: str) -> int:
    result = 2166136261
    for char in value:
        result ^= ord(char)
        result = (result * 16777619) % (2**32)

    return result


def build_searchable_text(document: dict[str, Any]) -> str:
    metadata = document.get("metadata", {})
    title = document.get("title", "")
    dsi_name = metadata.get("dsi_name", "")
    target_label = metadata.get("target_label", "")
    parts = [
        document.get("document_id", ""),
        document.get("source_type", ""),
        document.get("source_name", ""),
        title,
        title,
        title,
        dsi_name,
        dsi_name,
        target_label,
        target_label,
        target_label,
        metadata.get("relation_label", ""),
        document.get("content", ""),
        metadata.get("ingredient_name_ko", ""),
        metadata.get("ingredient_name_en", ""),
        metadata.get("normalized_name", ""),
        metadata.get("functional_component", ""),
        str(metadata.get("daily_dosage", "")),
        str(metadata.get("daily_dosage_structured", "")),
        metadata.get("supplement_name", ""),
        metadata.get("alternative_name", ""),
        metadata.get("condition", ""),
        metadata.get("category", ""),
        metadata.get("evidence_label", ""),
        metadata.get("notes", ""),
        *as_text_list(metadata.get("dsi_common_names", [])),
        *as_text_list(metadata.get("target_aliases", [])),
        *as_text_list(metadata.get("keywords", [])),
        *as_text_list(metadata.get("symptoms", [])),
        *as_text_list(metadata.get("related_ingredients", [])),
        *as_text_list(metadata.get("expected_effects", [])),
        *as_text_list(metadata.get("functional_claims", [])),
        *as_text_list(metadata.get("precautions", [])),
        *as_text_list(metadata.get("precaution_tags", [])),
    ]
    return " ".join(part for part in parts if part)


def as_text_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]

    if value:
        return [str(value)]

    return []


def tokenize(text: str) -> list[str]:
    normalized = text.lower()
    normalized = re.sub(r"[_\-/,.(){}\[\]:;|]+", " ", normalized)
    terms = re.findall(r"[a-z0-9가-힣][a-z0-9가-힣_+-]{1,}", normalized)

    return [term for term in terms if term not in STOPWORDS]


def normalize_top_k(top_k: int) -> int:
    if top_k < 1:
        return 1

    return min(top_k, MAX_TOP_K)
