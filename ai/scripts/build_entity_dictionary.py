import csv
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
AI_DATA_DIR = ROOT_DIR / "ai_data"
IDISK_DIR = AI_DATA_DIR / "iDISK"
OUTPUT_DIR = ROOT_DIR / "ai" / "app" / "data" / "processed"

MFDS_SOURCE = "mfds"
IDISK_SOURCE = "idisk"
IHERB_SOURCE = "iherb"
SEED_SOURCE = "seed"

KO_EN_SEEDS = {
    "마그네슘": "magnesium",
    "셀레늄": "selenium",
    "셀렌": "selenium",
    "셀레늄 (또는 셀렌)": "selenium",
    "아연": "zinc",
    "칼슘": "calcium",
    "비타민 C": "vitamin_c",
    "비타민 D": "vitamin_d",
    "비타민 E": "vitamin_e",
    "비타민 K": "vitamin_k",
    "루테인": "lutein",
    "프로바이오틱스": "probiotics",
    "홍삼": "red_ginseng",
    "인삼": "ginseng",
    "테아닌": "theanine",
    "L-테아닌": "l_theanine",
    "밀크씨슬": "milk_thistle",
    "코엔자임Q10": "coenzyme_q10",
    "오메가-3 지방산": "omega_3_fatty_acids",
    "피로": "fatigue",
    "피로개선": "fatigue",
    "수면": "sleep",
    "수면질 개선": "sleep_quality",
    "눈 건강": "eye_health",
    "장 건강": "gut_health",
    "면역": "immune_support",
    "피부건강": "skin_health",
    "혈행개선": "blood_circulation",
    "항응고제": "anticoagulants",
    "알레르기": "allergy",
    "심장 두근거림": "palpitations",
}


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        yield from csv.DictReader(file)


def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def clean_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def split_aliases(value: str | None) -> list[str]:
    cleaned = clean_text(value)
    if not cleaned:
        return []
    pieces = re.split(r"\s*\|\s*|<br\s*/?>|;|\n", cleaned)
    return [piece.strip(" .:-") for piece in pieces if piece.strip(" .:-")]


def split_ingredient_list(value: str | None) -> list[str]:
    cleaned = re.sub(r"<br\s*/?>", ",", value or "")
    cleaned = re.sub(r"\([^)]*인정취소[^)]*\)", "", cleaned)
    pieces = re.split(r",|ㆍ|·|\n", cleaned)
    return [re.sub(r"\s+", " ", piece).strip(" .") for piece in pieces if piece.strip(" .")]


def make_normalized_name(name: str) -> str:
    seeded = KO_EN_SEEDS.get(name)
    if seeded:
        return seeded

    cleaned = name.lower()
    cleaned = re.sub(r"\([^)]*\)", "", cleaned)
    cleaned = re.sub(r"[^0-9a-z가-힣]+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned


def language_of(term: str) -> str:
    return "ko" if re.search(r"[가-힣]", term) else "en"


def empty_term(normalized_name: str, term_type: str):
    return {
        "normalized_name": normalized_name,
        "term_type": term_type,
        "ko": [],
        "en": [],
        "source_ids": defaultdict(list),
        "source_types": set(),
        "confidence": 1.0,
    }


def add_term(terms, name, term_type, source, source_id=None, aliases=None, confidence=1.0):
    name = clean_text(name)
    if not name:
        return

    all_aliases = [name, *(aliases or [])]
    normalized_name = make_normalized_name(name)
    for alias in all_aliases:
        seeded = KO_EN_SEEDS.get(alias)
        if seeded:
            normalized_name = seeded
            break

    term = terms.setdefault((term_type, normalized_name), empty_term(normalized_name, term_type))
    term["confidence"] = min(term["confidence"], confidence)
    term["source_types"].add(source)
    if source_id and source_id not in term["source_ids"][source]:
        term["source_ids"][source].append(source_id)

    for alias in all_aliases:
        alias = clean_text(alias)
        if not alias:
            continue
        bucket = "ko" if language_of(alias) == "ko" else "en"
        if alias not in term[bucket]:
            term[bucket].append(alias)


def parse_idisk_entities(terms):
    entity_specs = [
        ("DSI.csv", "ingredient"),
        ("D.csv", "drug"),
        ("Dis.csv", "condition"),
        ("SS.csv", "adverse_reaction"),
        ("DSP.csv", "product"),
    ]
    entity_dir = IDISK_DIR / "entity"
    for file_name, term_type in entity_specs:
        for row in read_csv(entity_dir / file_name):
            aliases = []
            for column in ["Common Names", "NHP_Name", "DSLD_Name", "MSKCC_Name", "NM_Name"]:
                aliases.extend(split_aliases(row.get(column)))
            add_term(
                terms,
                row.get("Name"),
                term_type,
                IDISK_SOURCE,
                row.get("iDISK_ID"),
                aliases=aliases,
            )


def parse_iherb_entities(terms):
    path = AI_DATA_DIR / "iherb_category_ingredients.csv"
    for row in read_csv(path):
        source_id = row.get("cids")
        add_term(
            terms,
            row.get("성분"),
            "ingredient",
            IHERB_SOURCE,
            source_id,
            confidence=0.85,
        )


def parse_mfds_entities(terms):
    path = AI_DATA_DIR / "건기식_원료.md"
    current_function = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line:
            continue

        columns = [re.sub(r"<br\s*/?>", " ", column).strip() for column in line.strip("|").split("|")]
        if not columns or columns[0] in {"번호", "구 분"}:
            continue

        if len(columns) == 5 and columns[0].isdigit():
            current_function = clean_text(columns[1])
            ingredient_column = columns[3]
            for ingredient in split_ingredient_list(ingredient_column):
                add_term(
                    terms,
                    ingredient,
                    "ingredient",
                    MFDS_SOURCE,
                    ingredient,
                    confidence=0.9,
                )
            if current_function:
                add_term(terms, current_function, "condition", MFDS_SOURCE, current_function, confidence=0.9)

        if len(columns) >= 6 and columns[0].isdigit():
            ingredient = clean_text(columns[1])
            if ingredient and ingredient != current_function:
                add_term(
                    terms,
                    ingredient,
                    "ingredient",
                    MFDS_SOURCE,
                    ingredient,
                    aliases=[columns[3]],
                )


def add_seed_terms(terms):
    seed_specs = [
        ("피로", "condition", ["fatigue", "tiredness"]),
        ("수면", "condition", ["sleep", "sleep quality", "insomnia"]),
        ("눈 건강", "condition", ["eye health"]),
        ("장 건강", "condition", ["gut health", "digestive health"]),
        ("면역", "condition", ["immune support", "immunity"]),
        ("피부건강", "condition", ["skin health"]),
        ("혈행개선", "condition", ["blood circulation"]),
        ("항응고제", "drug", ["anticoagulants", "blood thinners"]),
        ("알레르기", "condition", ["allergy"]),
        ("심장 두근거림", "adverse_reaction", ["palpitations"]),
    ]
    for name, term_type, aliases in seed_specs:
        add_term(terms, name, term_type, SEED_SOURCE, aliases=aliases, confidence=0.95)


def build_entity_links(terms):
    links = []
    for term in terms.values():
        source_ids = {source: sorted(ids) for source, ids in term["source_ids"].items()}
        links.append(
            {
                "normalized_name": term["normalized_name"],
                "term_type": term["term_type"],
                "source_ids": source_ids,
                "source_types": sorted(term["source_types"]),
            }
        )
    return sorted(links, key=lambda row: (row["term_type"], row["normalized_name"]))


def build_idisk_relations():
    entity_dir = IDISK_DIR / "entity"
    relation_dir = IDISK_DIR / "relationship"

    dsi_names = {row["iDISK_ID"]: row["Name"] for row in read_csv(entity_dir / "DSI.csv")}
    drug_names = {row["iDISK_ID"]: row["Name"] for row in read_csv(entity_dir / "D.csv")}
    disease_names = {row["iDISK_ID"]: row["Name"] for row in read_csv(entity_dir / "Dis.csv")}
    side_effect_names = {row["iDISK_ID"]: row["Name"] for row in read_csv(entity_dir / "SS.csv")}

    relations = {
        dsi_id: {
            "dsi_id": dsi_id,
            "ingredient_name": name,
            "drugs": [],
            "conditions": [],
            "adverse_reactions": [],
        }
        for dsi_id, name in dsi_names.items()
    }

    for row in read_csv(relation_dir / "dsi_d.csv"):
        relation = relations.setdefault(row["DSI"], {"dsi_id": row["DSI"], "ingredient_name": dsi_names.get(row["DSI"], ""), "drugs": [], "conditions": [], "adverse_reactions": []})
        relation["drugs"].append(
            {
                "drug_id": row["D"],
                "drug_name": drug_names.get(row["D"], ""),
                "relation": row["Relation"],
                "source": row["Source"],
                "description": clean_text(row.get("Source_Description")),
            }
        )

    for row in read_csv(relation_dir / "dsi_dis.csv"):
        relation = relations.setdefault(row["DSI"], {"dsi_id": row["DSI"], "ingredient_name": dsi_names.get(row["DSI"], ""), "drugs": [], "conditions": [], "adverse_reactions": []})
        relation["conditions"].append(
            {
                "condition_id": row["Dis"],
                "condition_name": disease_names.get(row["Dis"], ""),
                "relation": row["Relation"],
                "source": row["Source"],
                "rating": row.get("Effectiveness Rating") or None,
                "description": clean_text(row.get("Source_Description")),
            }
        )

    for row in read_csv(relation_dir / "dsi_ss.csv"):
        relation = relations.setdefault(row["DSI"], {"dsi_id": row["DSI"], "ingredient_name": dsi_names.get(row["DSI"], ""), "drugs": [], "conditions": [], "adverse_reactions": []})
        relation["adverse_reactions"].append(
            {
                "side_effect_id": row["SS"],
                "side_effect_name": side_effect_names.get(row["SS"], ""),
                "relation": row["Relation"],
                "source": row["Source"],
            }
        )

    return sorted(relations.values(), key=lambda row: row["dsi_id"])


def serializable_terms(terms):
    rows = []
    for term in terms.values():
        rows.append(
            {
                "normalized_name": term["normalized_name"],
                "term_type": term["term_type"],
                "ko": sorted(term["ko"]),
                "en": sorted(term["en"]),
                "source_ids": {source: sorted(ids) for source, ids in term["source_ids"].items()},
                "source_types": sorted(term["source_types"]),
                "confidence": term["confidence"],
            }
        )
    return sorted(rows, key=lambda row: (row["term_type"], row["normalized_name"]))


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    terms = {}
    parse_idisk_entities(terms)
    parse_mfds_entities(terms)
    parse_iherb_entities(terms)
    add_seed_terms(terms)

    write_jsonl(OUTPUT_DIR / "normalized_terms.jsonl", serializable_terms(terms))
    write_jsonl(OUTPUT_DIR / "entity_links.jsonl", build_entity_links(terms))
    write_jsonl(OUTPUT_DIR / "idisk_relations.jsonl", build_idisk_relations())


if __name__ == "__main__":
    main()
