import csv
import json
import os
import re
from pathlib import Path
from typing import Any

from app.services.rag_vector_store import VECTOR_INDEX_PATH, write_vector_index


PROJECT_ROOT = Path(__file__).resolve().parents[3]

RAW_DATA_DIR = PROJECT_ROOT / "ai_data"
IDISK_DIR = RAW_DATA_DIR / "iDISK"
OUTPUT_PATH = PROJECT_ROOT / "ai" / "app" / "data" / "rag_documents.json"

FUNCTIONAL_INGREDIENT_SOURCE_NAME = "건강기능식품 기능성원료 인정현황"
IDISK_SOURCE_NAME = "iDISK"
SUPPLEMENT_EVIDENCE_SOURCE_NAME = "SnakeOil supplement evidence score"
SNAKEOIL_SOURCE_FILE_NAME = "Balloon Race_ SnakeOil supplements_ Public - Visualisation Data.csv"


def build_rag_documents() -> list[dict[str, Any]]:
    documents = []

    documents.extend(build_idisk_interaction_documents())
    documents.extend(build_idisk_disease_documents())
    documents.extend(build_idisk_side_effect_documents())
    documents.extend(build_functional_ingredient_documents())
    documents.extend(build_supplement_evidence_documents())

    return deduplicate_documents(documents)


def build_idisk_interaction_documents() -> list[dict[str, Any]]:
    path = IDISK_DIR / "dsi_d.csv"
    dsi_entities = load_entity_map(RAW_DATA_DIR / "DSI.csv")
    drug_entities = load_entity_map(RAW_DATA_DIR / "D.csv")
    documents = []

    for row in read_csv(path):
        dsi_id = row.get("DSI", "").strip()
        target_id = row.get("D", "").strip()
        relation = row.get("Relation", "").strip()
        source = row.get("Source", "").strip()
        rating = row.get("Interaction Rating", "").strip()
        description = row.get("Source_Description", "").strip()

        if not dsi_id or not target_id:
            continue

        dsi_entity = dsi_entities.get(dsi_id, {})
        target_entity = drug_entities.get(target_id, {})
        dsi_name = get_entity_name(dsi_entity, dsi_id)
        target_label = get_entity_name(target_entity, extract_idisk_target_label(description, target_id))
        content = build_idisk_content(
            relationship_type="interaction",
            dsi_id=dsi_id,
            dsi_name=dsi_name,
            dsi_common_names=get_entity_aliases(dsi_entity),
            relation=relation,
            target_type="drug_or_target",
            target_id=target_id,
            target_label=target_label,
            target_aliases=get_entity_aliases(target_entity),
            source=source,
            rating=rating,
            description=description,
            dsi_background=dsi_entity.get("Background", ""),
            dsi_safety=dsi_entity.get("Safety", ""),
        )

        documents.append(
            {
                "document_id": f"idisk_interaction_{normalize_id(dsi_id)}_{normalize_id(target_id)}",
                "source_type": "idisk",
                "source_name": IDISK_SOURCE_NAME,
                "title": f"iDISK interaction: {dsi_name} with {target_label}",
                "content": content,
                "metadata": {
                    "dataset": "dsi_d",
                    "dsi_id": dsi_id,
                    "dsi_name": dsi_name,
                    "dsi_cui": dsi_entity.get("CUI", ""),
                    "dsi_common_names": get_entity_aliases(dsi_entity),
                    "target_id": target_id,
                    "target_type": "drug_or_target",
                    "target_label": target_label,
                    "target_cui": target_entity.get("CUI", ""),
                    "target_aliases": get_entity_aliases(target_entity),
                    "relation": relation,
                    "relation_label": "interacts with",
                    "source": source,
                    "interaction_rating": rating,
                    "source_description": description,
                    "keywords": extract_keywords(content),
                },
            }
        )

    return documents


def build_idisk_disease_documents() -> list[dict[str, Any]]:
    path = IDISK_DIR / "dsi_dis.csv"
    dsi_entities = load_entity_map(RAW_DATA_DIR / "DSI.csv")
    disease_entities = load_entity_map(RAW_DATA_DIR / "Dis.csv")
    documents = []

    for row in read_csv(path):
        dsi_id = row.get("DSI", "").strip()
        disease_id = row.get("Dis", "").strip()
        relation = row.get("Relation", "").strip()
        source = row.get("Source", "").strip()
        rating = row.get("Effectiveness Rating", "").strip()
        description = row.get("Source_Description", "").strip()

        if not dsi_id or not disease_id:
            continue

        dsi_entity = dsi_entities.get(dsi_id, {})
        disease_entity = disease_entities.get(disease_id, {})
        dsi_name = get_entity_name(dsi_entity, dsi_id)
        disease_label = get_entity_name(disease_entity, disease_id)
        content = build_idisk_content(
            relationship_type="effectiveness",
            dsi_id=dsi_id,
            dsi_name=dsi_name,
            dsi_common_names=get_entity_aliases(dsi_entity),
            relation=relation,
            target_type="disease_or_condition",
            target_id=disease_id,
            target_label=disease_label,
            target_aliases=get_entity_aliases(disease_entity),
            source=source,
            rating=rating,
            description=description,
            dsi_background=dsi_entity.get("Background", ""),
            dsi_safety=dsi_entity.get("Safety", ""),
        )

        documents.append(
            {
                "document_id": f"idisk_disease_{normalize_id(dsi_id)}_{normalize_id(disease_id)}",
                "source_type": "idisk",
                "source_name": IDISK_SOURCE_NAME,
                "title": f"iDISK effectiveness: {dsi_name} for {disease_label}",
                "content": content,
                "metadata": {
                    "dataset": "dsi_dis",
                    "dsi_id": dsi_id,
                    "dsi_name": dsi_name,
                    "dsi_cui": dsi_entity.get("CUI", ""),
                    "dsi_common_names": get_entity_aliases(dsi_entity),
                    "disease_id": disease_id,
                    "target_type": "disease_or_condition",
                    "target_label": disease_label,
                    "target_cui": disease_entity.get("CUI", ""),
                    "target_aliases": get_entity_aliases(disease_entity),
                    "relation": relation,
                    "relation_label": "is effective for",
                    "source": source,
                    "effectiveness_rating": rating,
                    "source_description": description,
                    "keywords": extract_keywords(content),
                },
            }
        )

    return documents


def build_idisk_side_effect_documents() -> list[dict[str, Any]]:
    path = IDISK_DIR / "dsi_ss.csv"
    dsi_entities = load_entity_map(RAW_DATA_DIR / "DSI.csv")
    side_effect_entities = load_entity_map(RAW_DATA_DIR / "SS.csv")
    documents = []

    for row in read_csv(path):
        dsi_id = row.get("DSI", "").strip()
        side_effect_id = row.get("SS", "").strip()
        relation = row.get("Relation", "").strip()
        source = row.get("Source", "").strip()

        if not dsi_id or not side_effect_id:
            continue

        dsi_entity = dsi_entities.get(dsi_id, {})
        side_effect_entity = side_effect_entities.get(side_effect_id, {})
        dsi_name = get_entity_name(dsi_entity, dsi_id)
        side_effect_label = get_entity_name(side_effect_entity, side_effect_id)
        content = build_idisk_content(
            relationship_type="adverse_reaction",
            dsi_id=dsi_id,
            dsi_name=dsi_name,
            dsi_common_names=get_entity_aliases(dsi_entity),
            relation=relation,
            target_type="side_effect",
            target_id=side_effect_id,
            target_label=side_effect_label,
            target_aliases=get_entity_aliases(side_effect_entity),
            source=source,
            rating="",
            description="",
            dsi_background=dsi_entity.get("Background", ""),
            dsi_safety=dsi_entity.get("Safety", ""),
        )

        documents.append(
            {
                "document_id": f"idisk_side_effect_{normalize_id(dsi_id)}_{normalize_id(side_effect_id)}",
                "source_type": "idisk",
                "source_name": IDISK_SOURCE_NAME,
                "title": f"iDISK adverse reaction: {dsi_name} with {side_effect_label}",
                "content": content,
                "metadata": {
                    "dataset": "dsi_ss",
                    "dsi_id": dsi_id,
                    "dsi_name": dsi_name,
                    "dsi_cui": dsi_entity.get("CUI", ""),
                    "dsi_common_names": get_entity_aliases(dsi_entity),
                    "side_effect_id": side_effect_id,
                    "target_type": "side_effect",
                    "target_label": side_effect_label,
                    "target_cui": side_effect_entity.get("CUI", ""),
                    "target_aliases": get_entity_aliases(side_effect_entity),
                    "relation": relation,
                    "relation_label": "has adverse reaction",
                    "source": source,
                    "keywords": extract_keywords(content),
                },
            }
        )

    return documents


def build_idisk_content(
    *,
    relationship_type: str,
    dsi_id: str,
    dsi_name: str,
    dsi_common_names: list[str],
    relation: str,
    target_type: str,
    target_id: str,
    target_label: str,
    target_aliases: list[str],
    source: str,
    rating: str,
    description: str,
    dsi_background: str,
    dsi_safety: str,
) -> str:
    parts = [
        f"iDISK relationship type: {relationship_type}.",
        f"Supplement ingredient ID: {dsi_id}.",
        f"Supplement ingredient name: {dsi_name}.",
        f"Relation: {relation}.",
        f"Target type: {target_type}.",
        f"Target ID: {target_id}.",
        f"Target label: {target_label}.",
    ]

    if dsi_common_names:
        parts.append(f"Supplement aliases: {', '.join(dsi_common_names[:12])}.")
    if target_aliases:
        parts.append(f"Target aliases: {', '.join(target_aliases[:12])}.")
    if source:
        parts.append(f"Evidence source: {source}.")
    if rating:
        parts.append(f"Rating: {rating}.")
    if description:
        parts.append(f"Source description: {description}")
    if dsi_background:
        parts.append(f"Ingredient background: {truncate_text(dsi_background, 900)}")
    if dsi_safety:
        parts.append(f"Ingredient safety: {truncate_text(dsi_safety, 500)}")

    return " ".join(parts)


def extract_idisk_target_label(description: str, fallback: str) -> str:
    if not description:
        return fallback

    label = description.split(":", 1)[0].strip()
    if not label or len(label) > 120:
        return fallback

    return label


def load_entity_map(path: Path) -> dict[str, dict[str, str]]:
    return {
        row["iDISK_ID"].strip(): row
        for row in read_csv(path)
        if row.get("iDISK_ID", "").strip()
    }


def get_entity_name(entity: dict[str, str], fallback: str) -> str:
    for key in ["Name", "MSKCC_Name", "NHP_Name", "DSLD_Name", "NM_Name"]:
        value = clean_text(entity.get(key, ""))
        if value:
            return split_aliases(value)[0]

    return fallback


def get_entity_aliases(entity: dict[str, str]) -> list[str]:
    aliases = []
    for key in ["Name", "Common Names", "MSKCC_Name", "NHP_Name", "DSLD_Name", "NM_Name"]:
        for alias in split_aliases(entity.get(key, "")):
            if alias not in aliases:
                aliases.append(alias)

    return aliases


def split_aliases(value: str) -> list[str]:
    if not value:
        return []

    return [
        clean_text(item).rstrip(":")
        for item in re.split(r"[|;]", value)
        if clean_text(item).rstrip(":")
    ]


def truncate_text(value: str, max_length: int) -> str:
    text = clean_text(value)
    if len(text) <= max_length:
        return text

    return f"{text[:max_length].rstrip()}..."

def build_functional_ingredient_documents() -> list[dict[str, Any]]:
    path = RAW_DATA_DIR / "건기식_원료.md"
    documents = []

    if not path.exists():
        return documents

    text = read_text_with_fallback(path)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    current_section = ""
    current_claim = ""
    headers: list[str] = []

    for index, line in enumerate(lines):
        if line.startswith("#"):
            heading = clean_heading(line)
            if line.startswith("#####"):
                current_claim = heading
            elif line.startswith("####"):
                current_section = heading
                current_claim = ""
            elif line.startswith("###"):
                current_section = heading
                current_claim = ""
            continue

        if not is_possible_markdown_row(line):
            continue

        cells = split_markdown_row(line)
        if is_separator_row(cells):
            continue

        if is_header_row(cells):
            headers = [normalize_header(cell) for cell in cells]
            continue

        if not is_functional_ingredient_header(headers):
            continue

        row = build_row_map(headers, cells)
        title = get_first_value(row, ["영양소", "원료", "원료명"])
        if not title or title in ["총 계", "총계"]:
            continue

        functional_claims = split_text_items(row.get("기능성내용", "") or current_claim)
        daily_dosage = row.get("일일섭취량", "")
        daily_dosage_structured = parse_daily_dosage(daily_dosage)
        precautions = split_text_items(row.get("섭취시주의사항", ""))
        precaution_tags = tag_precautions(precautions)
        functional_component = row.get("기능지표성분", "")
        normalized_name = normalize_name(title)
        content = build_functional_ingredient_content(
            title=title,
            functional_claims=functional_claims,
            functional_component=functional_component,
            daily_dosage=daily_dosage,
            daily_dosage_structured=daily_dosage_structured,
            precautions=precautions,
            precaution_tags=precaution_tags,
            current_section=current_section,
            current_claim=current_claim,
            approval_number=row.get("인정번호", ""),
            approval_grade=row.get("인정등급", ""),
        )

        documents.append(
            {
                "document_id": f"functional_ingredient_{normalized_name}_{index}",
                "source_type": "functional_ingredient",
                "source_name": FUNCTIONAL_INGREDIENT_SOURCE_NAME,
                "title": title,
                "content": content,
                "metadata": {
                    "row_index": index,
                    "ingredient_name_ko": title,
                    "ingredient_name_en": None,
                    "normalized_name": normalized_name,
                    "functional_claims": functional_claims,
                    "functional_component": functional_component,
                    "daily_dosage": daily_dosage,
                    "daily_dosage_structured": daily_dosage_structured,
                    "precautions": precautions,
                    "precaution_tags": precaution_tags,
                    "approval_number": row.get("인정번호", ""),
                    "approval_grade": row.get("인정등급", ""),
                    "section": current_section,
                    "claim_category": current_claim,
                    "keywords": extract_keywords(content),
                },
            }
        )

    return documents


def is_possible_markdown_row(line: str) -> bool:
    if not line.startswith("|"):
        return False

    return line.count("|") >= 3


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip("|").split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return all(cell and set(cell) <= {"-"} for cell in cells)


def is_header_row(cells: list[str]) -> bool:
    return bool(cells and normalize_header(cells[0]) == "번호")


def is_functional_ingredient_header(headers: list[str]) -> bool:
    return any(header in headers for header in ["영양소", "원료", "원료명"])


def build_row_map(headers: list[str], cells: list[str]) -> dict[str, str]:
    row = {}

    for index, header in enumerate(headers):
        if not header:
            continue

        value = clean_text(cells[index]) if index < len(cells) else ""
        row[header] = value

    return row


def get_first_value(row: dict[str, str], keys: list[str]) -> str:
    for key in keys:
        value = row.get(key, "")
        if value:
            return value

    return ""


def build_functional_ingredient_content(
    *,
    title: str,
    functional_claims: list[str],
    functional_component: str,
    daily_dosage: str,
    daily_dosage_structured: dict[str, Any] | None,
    precautions: list[str],
    precaution_tags: list[str],
    current_section: str,
    current_claim: str,
    approval_number: str,
    approval_grade: str,
) -> str:
    parts = [f"원료명: {title}"]

    if current_section:
        parts.append(f"분류: {current_section}")
    if current_claim:
        parts.append(f"기능성 분류: {current_claim}")
    if functional_claims:
        parts.append(f"기능성 내용: {', '.join(functional_claims)}")
    if functional_component:
        parts.append(f"기능성분: {functional_component}")
    if daily_dosage:
        parts.append(f"일일섭취량: {daily_dosage}")
    if daily_dosage_structured:
        dosage_range = format_daily_dosage_structured(daily_dosage_structured)
        if dosage_range:
            parts.append(f"구조화된 일일섭취량: {dosage_range}")
    if precautions:
        parts.append(f"섭취 시 주의사항: {', '.join(precautions)}")
    if precaution_tags:
        parts.append(f"주의 태그: {', '.join(precaution_tags)}")
    if approval_number:
        parts.append(f"인정번호: {approval_number}")
    if approval_grade:
        parts.append(f"인정등급: {approval_grade}")

    return " ".join(parts)


def parse_daily_dosage(value: str) -> dict[str, Any] | None:
    if not value or value == "-":
        return None

    normalized = clean_text(value)
    match = re.search(
        r"(?P<min>\d+(?:\.\d+)?)\s*[~～-]\s*(?P<max>\d+(?:\.\d+)?)\s*(?P<unit>[a-zA-Zμ㎍가-힣/-]+)",
        normalized,
    )
    if match:
        return {
            "raw": normalized,
            "min_value": parse_number(match.group("min")),
            "max_value": parse_number(match.group("max")),
            "unit": normalize_unit(match.group("unit")),
        }

    single_match = re.search(
        r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>[a-zA-Zμ㎍가-힣/-]+)\s*(?:이상|이하|초과|미만)?",
        normalized,
    )
    if single_match:
        qualifier = extract_dosage_qualifier(normalized)
        parsed_value = parse_number(single_match.group("value"))
        result: dict[str, Any] = {
            "raw": normalized,
            "unit": normalize_unit(single_match.group("unit")),
        }
        if qualifier in ["이상", "초과"]:
            result["min_value"] = parsed_value
            result["max_value"] = None
        elif qualifier in ["이하", "미만"]:
            result["min_value"] = None
            result["max_value"] = parsed_value
        else:
            result["min_value"] = parsed_value
            result["max_value"] = parsed_value
        if qualifier:
            result["qualifier"] = qualifier
        return result

    return {"raw": normalized, "min_value": None, "max_value": None, "unit": None}


def parse_number(value: str) -> float:
    return float(value.replace(",", ""))


def normalize_unit(value: str) -> str:
    unit = value.strip()
    unit = unit.replace("㎍", "μg")
    return unit


def extract_dosage_qualifier(value: str) -> str | None:
    for qualifier in ["이상", "이하", "초과", "미만"]:
        if qualifier in value:
            return qualifier

    return None


def format_daily_dosage_structured(value: dict[str, Any]) -> str:
    unit = value.get("unit")
    min_value = value.get("min_value")
    max_value = value.get("max_value")
    if min_value is not None and max_value is not None and min_value != max_value:
        return f"{min_value:g}~{max_value:g} {unit}".strip()
    if min_value is not None and max_value is not None:
        return f"{min_value:g} {unit}".strip()
    if min_value is not None:
        return f"{min_value:g} {unit} 이상".strip()
    if max_value is not None:
        return f"{max_value:g} {unit} 이하".strip()

    return ""


def tag_precautions(precautions: list[str]) -> list[str]:
    tag_rules = [
        ("medication_caution", ["의약품", "약물", "복용", "치료제", "항응고제"]),
        ("pregnancy_caution", ["임산부", "임신", "수유", "수유부"]),
        ("disease_consultation", ["질환", "질병", "환자", "전문의", "의사", "상담"]),
        ("allergy_caution", ["알레르기", "과민반응"]),
        ("overdose_caution", ["과다", "과량"]),
        ("children_caution", ["어린이", "영유아", "소아"]),
        ("gastrointestinal_caution", ["위장", "소화", "설사", "구토"]),
    ]

    text = " ".join(precautions)
    tags = []
    for tag, keywords in tag_rules:
        if any(keyword in text for keyword in keywords):
            tags.append(tag)

    return tags


def split_text_items(value: str) -> list[str]:
    if not value or value == "-":
        return []

    return [
        item
        for item in (clean_text(item) for item in re.split(r"<br\s*/?>", value))
        if item and item != "-"
    ]


def clean_heading(line: str) -> str:
    return clean_text(line.lstrip("#").strip())


def normalize_header(value: str) -> str:
    header = clean_text(value)
    header = re.sub(r"\s+", "", header)
    header = header.replace("(지표)", "지표")

    aliases = {
        "기능성내용": "기능성내용",
        "기능지표성분": "기능지표성분",
        "일일섭취량": "일일섭취량",
        "섭취시주의사항": "섭취시주의사항",
    }

    return aliases.get(header, header)


def build_supplement_evidence_documents() -> list[dict[str, Any]]:
    path = RAW_DATA_DIR / SNAKEOIL_SOURCE_FILE_NAME
    documents = []

    for index, row in enumerate(read_csv(path)):
        supplement_name = clean_text(row.get("name", ""))
        score = parse_evidence_score(row.get("primaryvalue", ""))
        source_id = clean_text(row.get("ID", ""))

        if not supplement_name or score is None:
            continue

        condition = clean_text(row.get("subcategory", ""))
        category = clean_text(row.get("category", ""))
        substance_type = clean_text(row.get("type", ""))
        alternative_name = clean_text(row.get("alternativename", ""))
        notes = clean_text(row.get("notes", ""))
        source_links = collect_source_links(row)
        evidence_label = evidence_score_label(score)
        normalized_name = normalize_name(supplement_name)
        document_id = (
            f"supplement_evidence_{normalize_id(source_id)}"
            if source_id
            else f"supplement_evidence_{normalized_name}_{index}"
        )
        content = build_supplement_evidence_content(
            supplement_name=supplement_name,
            alternative_name=alternative_name,
            condition=condition,
            category=category,
            substance_type=substance_type,
            score=score,
            evidence_label=evidence_label,
            notes=notes,
            source_links=source_links,
        )

        documents.append(
            {
                "document_id": document_id,
                "source_type": "supplement_evidence",
                "source_name": SUPPLEMENT_EVIDENCE_SOURCE_NAME,
                "title": f"{supplement_name} evidence for {condition}",
                "content": content,
                "metadata": {
                    "row_index": index,
                    "source_file": SNAKEOIL_SOURCE_FILE_NAME,
                    "source_id": source_id,
                    "supplement_name": supplement_name,
                    "alternative_name": alternative_name,
                    "normalized_name": normalized_name,
                    "condition": condition,
                    "category": category,
                    "substance_type": substance_type,
                    "evidence_score": score,
                    "evidence_label": evidence_label,
                    "is_harmful": score == 0,
                    "is_low_evidence": score in [1, 2],
                    "is_promising_or_better": score >= 4,
                    "highlight": clean_text(row.get("highlight", "")),
                    "popularity": clean_text(row.get("metric_001", "")),
                    "search_term": clean_text(row.get("searchterm", "")),
                    "notes": notes,
                    "source_names": clean_text(row.get("", "")),
                    "source_links": source_links,
                    "usage_policy": "risk_and_evidence_reference_only",
                    "keywords": extract_keywords(content),
                },
            }
        )

    return documents


def build_supplement_evidence_content(
    *,
    supplement_name: str,
    alternative_name: str,
    condition: str,
    category: str,
    substance_type: str,
    score: int,
    evidence_label: str,
    notes: str,
    source_links: list[str],
) -> str:
    parts = [
        f"Supplement evidence reference only: {supplement_name}.",
        "This document is not a recommendation candidate source.",
        f"Evidence score: {score} ({evidence_label}).",
    ]

    if alternative_name:
        parts.append(f"Alternative name: {alternative_name}.")
    if condition:
        parts.append(f"Claim or condition: {condition}.")
    if category:
        parts.append(f"Category: {category}.")
    if substance_type:
        parts.append(f"Substance type: {substance_type}.")
    if notes:
        parts.append(f"Evidence notes: {notes}")
    if source_links:
        parts.append(f"Source links: {' '.join(source_links[:5])}")

    return " ".join(parts)


def parse_evidence_score(value: str) -> int | None:
    cleaned = clean_text(value)
    if not re.fullmatch(r"\d+", cleaned):
        return None

    score = int(cleaned)
    if score < 0 or score > 6:
        return None

    return score


def evidence_score_label(score: int) -> str:
    labels = {
        0: "harmful",
        1: "no_evidence",
        2: "slight_evidence",
        3: "conflicting_or_moderate",
        4: "promising",
        5: "good",
        6: "strong",
    }
    return labels[score]


def collect_source_links(row: dict[str, str]) -> list[str]:
    links = []
    for key in ["link", "firstsource", "secondsource", "thirdsource"]:
        for item in re.split(r"[\r\n,]+", row.get(key, "")):
            value = clean_text(item)
            if value.startswith("http") and value not in links:
                links.append(value)

    return links

def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []

    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def read_text_with_fallback(path: Path) -> str:
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]

    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    return path.read_text(encoding="utf-8", errors="ignore")


def extract_keywords(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z가-힣0-9][A-Za-z가-힣0-9_-]{1,}", text.lower())

    stopwords = {
        "with",
        "from",
        "this",
        "that",
        "because",
        "source",
        "relation",
        "and",
        "the",
        "for",
        "are",
        "can",
        "may",
    }

    keywords = []
    for word in words:
        if word in stopwords:
            continue
        if word not in keywords:
            keywords.append(word)

    return keywords[:30]


def normalize_id(value: str) -> str:
    return value.strip().lower()


def normalize_name(value: str) -> str:
    normalized = clean_text(value).lower()
    normalized = re.sub(r"[^a-zA-Z0-9가-힣]+", "_", normalized)
    normalized = normalized.strip("_")

    return normalized or "unknown"


def clean_text(value: str) -> str:
    return (
        value.replace("<br>", " ")
        .replace("<br/>", " ")
        .replace("<br />", " ")
        .replace("&nbsp;", " ")
        .strip()
    )


def deduplicate_documents(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []

    for document in documents:
        document_id = document["document_id"]

        if document_id in seen:
            continue

        seen.add(document_id)
        result.append(document)

    return result

def write_rag_documents() -> list[dict[str, Any]]:
    documents = build_rag_documents()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    temp_path = OUTPUT_PATH.with_suffix(f"{OUTPUT_PATH.suffix}.tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(documents, file, ensure_ascii=False, indent=2)

    temp_path.replace(OUTPUT_PATH)
    write_vector_index(documents, VECTOR_INDEX_PATH)
    if get_rag_vector_backend() == "chroma":
        from app.services.rag_chroma_store import write_chroma_index

        write_chroma_index(documents)

    return documents


def get_rag_vector_backend() -> str:
    return os.environ.get("RAG_VECTOR_BACKEND", "local_json")


if __name__ == "__main__":
    documents = write_rag_documents()
    print(f"wrote {len(documents)} RAG documents to {OUTPUT_PATH}")
    print(f"wrote RAG vector index to {VECTOR_INDEX_PATH}")
    if get_rag_vector_backend() == "chroma":
        chroma_persist_dir = os.environ.get("CHROMA_PERSIST_DIR", "app/data/chroma")
        chroma_collection_name = os.environ.get("CHROMA_COLLECTION_NAME", "rag_documents")
        print(f"wrote RAG Chroma collection to {chroma_persist_dir}/{chroma_collection_name}")
