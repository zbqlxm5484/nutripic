import csv
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


CSV_PATH = Path(__file__).resolve().parents[3] / "ai_data" / "iherb_category_ingredients.csv"

NOISE_TERMS = [
    "고시형 원료로 전환",
    "고시형원료로전환",
    "고시형 원료",
    "고시형원료",
    "추출물",
    "농축액",
    "분말",
    "건조",
    "가열처리",
    "균사체",
    "정제물",
    "보충제",
]

MANUAL_ALIASES = {
    "동양 인삼": ["ginseng", "panax_ginseng", "인삼", "홍삼"],
    "영지버섯": ["reishi", "reishi_mushroom", "영지버섯 균사체"],
    "클로렐라": ["chlorella", "클로렐라 고시형 원료로 전환"],
    "오메가3 피쉬 오일": ["omega3", "omega_3", "omega_3_fatty_acids", "fish_oil"],
    "칼슘 & 마그네슘": ["magnesium", "마그네슘"],
    "피콜린산 아연": ["zinc", "아연"],
    "비타민 C": ["vitamin_c"],
    "비타민 D": ["vitamin_d"],
}


@dataclass(frozen=True)
class IherbIngredient:
    canonical_name: str
    ingredient_name_ko: str
    iherb_category_name: str
    iherb_url: str
    aliases: tuple[str, ...]


def normalize_key(value: str | None) -> str:
    if not value:
        return ""

    text = value.lower()
    text = re.sub(r"\([^)]*\)", " ", text)
    for term in NOISE_TERMS:
        text = text.replace(term.lower(), " ")
    text = re.sub(r"[^0-9a-z\uac00-\ud7a3]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def simplified_key(value: str | None) -> str:
    key = normalize_key(value)
    for term in NOISE_TERMS:
        key = key.replace(normalize_key(term), "")
    return re.sub(r"_+", "_", key).strip("_")


def should_use_iherb_canonical(existing_normalized_name: str | None, raw_name: str | None) -> bool:
    if not existing_normalized_name:
        return True

    existing_key = normalize_key(existing_normalized_name)
    if re.fullmatch(r"[a-z0-9_]+", existing_key) and not any(
        (term_key := normalize_key(term)) and term_key in existing_key
        for term in NOISE_TERMS
    ):
        return False

    raw_key = normalize_key(raw_name)
    if existing_key == raw_key:
        return True

    if re.search(r"[\uac00-\ud7a3]", existing_normalized_name):
        return True

    return any(
        (term_key := normalize_key(term)) and term_key in existing_key
        for term in NOISE_TERMS
    )


@lru_cache(maxsize=1)
def load_iherb_ingredients() -> tuple[IherbIngredient, ...]:
    if not CSV_PATH.exists():
        return ()

    ingredients = []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            ingredient_name = (row.get("성분") or "").strip()
            category_name = (row.get("카테고리") or "").strip()
            url = (row.get("url") or "").strip()
            if not ingredient_name or not url:
                continue

            aliases = build_aliases(ingredient_name)
            ingredients.append(
                IherbIngredient(
                    canonical_name=normalize_key(ingredient_name),
                    ingredient_name_ko=ingredient_name,
                    iherb_category_name=category_name,
                    iherb_url=url,
                    aliases=tuple(aliases),
                )
            )

    return tuple(ingredients)


@lru_cache(maxsize=1)
def alias_index() -> dict[str, IherbIngredient]:
    index = {}
    for ingredient in load_iherb_ingredients():
        for alias in ingredient.aliases:
            key = normalize_key(alias)
            if key and key not in index:
                index[key] = ingredient
    return index


def build_aliases(ingredient_name: str) -> list[str]:
    aliases = [ingredient_name]

    no_parentheses = re.sub(r"\([^)]*\)", "", ingredient_name).strip()
    if no_parentheses:
        aliases.append(no_parentheses)

    if "," in ingredient_name:
        aliases.append(ingredient_name.split(",", 1)[0].strip())

    if "&" in ingredient_name:
        aliases.extend(part.strip() for part in ingredient_name.split("&") if part.strip())

    simplified = simplified_key(ingredient_name)
    if simplified:
        aliases.append(simplified)

    aliases.extend(MANUAL_ALIASES.get(ingredient_name, []))
    return dedupe_preserve_order(aliases)


def match_iherb_ingredient(*names: str | None) -> IherbIngredient | None:
    keys = [normalize_key(name) for name in names if name]
    keys.extend(simplified_key(name) for name in names if name)

    index = alias_index()
    for key in keys:
        if key in index:
            return index[key]

    for key in keys:
        if not key:
            continue
        match = conservative_partial_match(key)
        if match:
            return match

    return None


def conservative_partial_match(key: str) -> IherbIngredient | None:
    candidates = []
    for alias_key, ingredient in alias_index().items():
        if len(alias_key) < 3:
            continue
        if alias_key in key or key in alias_key:
            candidates.append((len(alias_key), ingredient))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
