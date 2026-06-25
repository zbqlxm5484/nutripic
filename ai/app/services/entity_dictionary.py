import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
IHERB_CATEGORY_URL_TEMPLATE = "https://kr.iherb.com/c/supplements?cids={cid}"

IHERB_CATEGORY_OVERRIDES = {
    "magnesium": {
        "cid": "1805",
        "category_name": "미네랄",
    },
    "vitamin_c": {
        "cid": "1849",
        "category_name": "비타민 C",
    },
    "vitamin_d": {
        "cid": "1835",
        "category_name": "비타민 D",
    },
    "zinc": {
        "cid": "1857",
        "category_name": "미네랄",
    },
    "omega3": {
        "cid": "100826",
        "category_name": "피쉬 오일 & 오메가",
    },
    "omega_3": {
        "cid": "100826",
        "category_name": "피쉬 오일 & 오메가",
    },
    "omega_3_fatty_acids": {
        "cid": "100826",
        "category_name": "피쉬 오일 & 오메가",
    },
}

FALLBACK_TERMS = [
    {
        "normalized_name": "fatigue",
        "term_type": "condition",
        "ko": ["피로"],
        "en": ["fatigue"],
        "source_ids": {"mfds": ["피로개선"]},
        "source_types": ["mfds"],
        "confidence": 0.95,
    },
    {
        "normalized_name": "sleep",
        "term_type": "condition",
        "ko": ["수면"],
        "en": ["sleep"],
        "source_ids": {"mfds": ["수면질 개선"]},
        "source_types": ["mfds"],
        "confidence": 0.95,
    },
    {
        "normalized_name": "anticoagulant",
        "term_type": "drug",
        "ko": ["항응고제"],
        "en": ["anticoagulant"],
        "source_ids": {},
        "source_types": [],
        "confidence": 0.95,
    },
    {
        "normalized_name": "allergy",
        "term_type": "condition",
        "ko": ["알레르기"],
        "en": ["allergy"],
        "source_ids": {},
        "source_types": [],
        "confidence": 0.95,
    },
    {
        "normalized_name": "palpitations",
        "term_type": "adverse_reaction",
        "ko": ["심장 두근거림"],
        "en": ["palpitations"],
        "source_ids": {},
        "source_types": [],
        "confidence": 0.88,
    },
]


def normalize_key(value: str) -> str:
    lowered = value.lower()
    lowered = re.sub(r"\([^)]*\)", "", lowered)
    lowered = re.sub(r"[^0-9a-z가-힣]+", "_", lowered)
    return re.sub(r"_+", "_", lowered).strip("_")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


@lru_cache(maxsize=1)
def load_terms() -> list[dict[str, Any]]:
    terms = read_jsonl(DATA_DIR / "normalized_terms.jsonl")
    return terms or FALLBACK_TERMS


@lru_cache(maxsize=1)
def alias_index() -> dict[str, list[dict[str, Any]]]:
    index = {}
    for term in load_terms():
        aliases = [
            term["normalized_name"],
            *term.get("ko", []),
            *term.get("en", []),
        ]
        for alias in aliases:
            key = normalize_key(alias)
            if key:
                index.setdefault(key, []).append(term)
    return index


def match_term(value: str, expected_types: set[str] | None = None) -> dict[str, Any] | None:
    key = normalize_key(value)
    terms = alias_index().get(key, [])
    for term in terms:
        if not expected_types or term["term_type"] in expected_types:
            return term
    return None


@lru_cache(maxsize=1)
def iherb_mapping_index() -> dict[str, dict[str, str]]:
    index = {
        normalized_name: build_iherb_mapping(mapping["cid"], mapping["category_name"])
        for normalized_name, mapping in IHERB_CATEGORY_OVERRIDES.items()
    }

    for term in load_terms():
        if term.get("term_type") != "ingredient":
            continue

        cids = term.get("source_ids", {}).get("iherb") or []
        if not cids:
            continue

        normalized_name = term.get("normalized_name")
        category_name = first_text(term.get("ko")) or first_text(term.get("en")) or normalized_name
        if normalized_name and normalized_name not in index:
            index[normalized_name] = build_iherb_mapping(cids[0], category_name)

    return index


def first_text(values: list[str] | None) -> str | None:
    return values[0] if values else None


def build_iherb_mapping(cid: str, category_name: str) -> dict[str, str]:
    return {
        "iherb_url": IHERB_CATEGORY_URL_TEMPLATE.format(cid=cid),
        "iherb_category_name": category_name,
    }


def iherb_mapping_for(normalized_name: str | None) -> dict[str, str] | None:
    if not normalized_name:
        return None
    return iherb_mapping_index().get(normalized_name)


def english_name(term: dict[str, Any], fallback: str) -> str:
    if term.get("name_en"):
        return term["name_en"]
    names = term.get("en") or []
    return normalize_key(names[0]).replace("_", " ") if names else term.get("normalized_name", fallback)


def source_ids_for(terms: list[dict[str, Any]], source: str) -> list[str]:
    ids = []
    for term in terms:
        ids.extend(term.get("source_ids", {}).get(source, []))
    return sorted(set(ids))


def build_rag_query_bundle(
    goals: list[dict[str, Any]],
    medications: list[dict[str, Any]],
    special_conditions: list[dict[str, Any]],
    additional_terms: list[dict[str, Any]],
) -> dict[str, Any]:
    conditions = [*goals, *special_conditions]
    safety_terms = [*medications, *special_conditions, *additional_terms]
    ingredient_terms = [term for term in [*goals, *additional_terms] if term.get("term_type") == "ingredient"]

    text_queries = []
    goal_names = [english_name(term, term["normalized_name"]) for term in goals]
    if goal_names:
        text_queries.append(" ".join([*goal_names, "supplements"]))

    for term in safety_terms:
        text_queries.append(f"{english_name(term, term['normalized_name'])} supplement precautions")

    return {
        "idisk": {
            "ingredient_ids": source_ids_for(ingredient_terms, "idisk"),
            "condition_ids": source_ids_for(conditions, "idisk"),
            "drug_ids": source_ids_for(medications, "idisk"),
            "relation_targets": [
                "is_effective_for",
                "interacts_with",
                "has_adverse_reaction",
            ],
        },
        "mfds": {
            "ingredient_names": source_ids_for(ingredient_terms, "mfds"),
            "functional_categories": source_ids_for(conditions, "mfds"),
        },
        "iherb": {
            "ingredient_ids": source_ids_for(ingredient_terms, "iherb"),
        },
        "text_queries": text_queries,
    }
