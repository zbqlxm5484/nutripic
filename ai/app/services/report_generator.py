import re

from app.schemas.common import Citation, GuardrailResult
from app.schemas.reports import (
    ClarificationQuestion,
    InputSummary,
    RecommendedIngredient,
    ReportGenerateRequest,
    ReportGenerateResponse,
)
from app.services.guardrails import filter_valid_citations
from app.services.iherb_dictionary import match_iherb_ingredient, should_use_iherb_canonical
from app.services.llm_generation import generate_report_with_llm

DEFAULT_DISCLAIMER = "질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요."
SUITABILITY_DISCLAIMER = (
    "추천 적합도는 사용자의 입력 조건, 근거 자료, 주의사항을 종합한 우선순위 점수이며, "
    "효과 발생 확률이나 의학적 진단을 의미하지 않습니다."
)

# RAG metadata에서 위험 신호를 나타내는 필드
RISK_METADATA_FIELDS = ["precautions", "drugs", "conditions", "contraindications", "side_effects"]
STRONG_RISK_METADATA_FIELDS = ["contraindications", "drug_interactions"]
FUNCTIONAL_INGREDIENT_SOURCE_NAME = "건강기능식품 기능성원료 인정현황"

LIFESTYLE_TIPS_BY_GOAL = {
    "fatigue": [
        "기상 시간과 취침 시간을 일정하게 유지해 피로 회복 리듬을 안정적으로 관리해 보세요.",
        "끼니를 거르기보다 단백질과 복합 탄수화물이 포함된 식사를 규칙적으로 챙겨 보세요.",
    ],
    "immunity": [
        "수면 부족은 컨디션 관리에 영향을 줄 수 있으므로 충분한 수면 시간을 확보해 보세요.",
        "손 씻기와 실내 환기처럼 기본 위생 습관을 꾸준히 유지해 보세요.",
    ],
    "eye_health": [
        "화면을 오래 볼 때는 주기적으로 먼 곳을 보며 눈의 긴장을 풀어 주세요.",
        "실내가 건조하다면 습도와 조명을 조절해 눈의 피로를 줄여 보세요.",
    ],
    "gut_health": [
        "식이섬유가 있는 채소, 과일, 통곡물을 식사에 꾸준히 포함해 보세요.",
        "장 컨디션을 보기 위해 식사 시간과 배변 리듬을 일정하게 유지해 보세요.",
    ],
    "sleep": [
        "잠들기 전 스마트폰과 밝은 화면 노출을 줄여 수면 준비 시간을 만들어 보세요.",
        "늦은 오후 이후 카페인 섭취를 줄이고 취침 시간을 일정하게 유지해 보세요.",
    ],
    "skin_health": [
        "수분 섭취와 보습 루틴을 꾸준히 유지해 피부 컨디션 변화를 관찰해 보세요.",
        "자외선 노출이 많은 날에는 차단과 휴식을 함께 챙겨 보세요.",
    ],
    "body_fat": [
        "식사량을 급격히 줄이기보다 단백질을 포함한 균형 잡힌 식사를 유지해 보세요.",
        "유산소 운동과 근력 운동을 함께 계획해 체성분 변화를 꾸준히 확인해 보세요.",
    ],
    "bone_health": [
        "무리하지 않는 범위에서 걷기와 근력 운동처럼 뼈에 자극을 주는 활동을 해 보세요.",
        "햇빛 노출과 칼슘이 포함된 식사를 함께 점검해 보세요.",
    ],
    "blood_sugar": [
        "식후 가벼운 걷기처럼 혈당 관리에 도움이 되는 활동을 생활화해 보세요.",
        "단 음료와 정제 탄수화물 섭취 빈도를 줄이고 식사 구성을 기록해 보세요.",
    ],
}


def generate_report(payload: ReportGenerateRequest) -> ReportGenerateResponse:
    clarification_response = build_strong_risk_clarification(payload)
    if clarification_response:
        return clarification_response

    fallback_response = build_template_report(payload)
    response = generate_report_with_llm(payload, fallback_response)
    return response


def build_template_report(payload: ReportGenerateRequest) -> ReportGenerateResponse:
    normalized_input = payload.normalized_input
    primary_goal = normalized_input.health_goals[0].name_ko if normalized_input.health_goals else "건강 관리"

    ingredients = build_recommended_ingredients(payload)
    citations = build_citations(payload)

    return ReportGenerateResponse(
        status="completed",
        title=f"{primary_goal} 개선을 위한 성분 리포트",
        input_summary=InputSummary(
            age=normalized_input.age,
            gender=normalized_input.gender,
            health_goals=[goal.name_ko for goal in normalized_input.health_goals],
            medications=[item.name_ko for item in normalized_input.medications],
            special_conditions=[item.name_ko for item in normalized_input.special_conditions],
            additional_notes=normalized_input.additional_notes,
        ),
        recommended_ingredients=ingredients,
        lifestyle_tips=build_lifestyle_tips(normalized_input),
        disclaimer=build_disclaimer(),
        citations=citations,
        guardrail_result=GuardrailResult(is_allowed=True, risk_level="low"),
    )


def build_recommended_ingredients(payload: ReportGenerateRequest) -> list[RecommendedIngredient]:
    functional_contexts = [
        context for context in payload.rag_contexts if context.source_type == "functional_ingredient"
    ]
    active_functional_contexts = [
        context for context in functional_contexts if not is_cancelled_functional_ingredient(context)
    ]

    if functional_contexts and not active_functional_contexts:
        return []

    if not active_functional_contexts:
        return [
            RecommendedIngredient(
                name_ko="마그네슘",
                name_en="Magnesium",
                normalized_name="magnesium",
                reason="피로와 수면 관리에 관련된 근거가 검색되어 후보로 선정했습니다.",
                recommendation_score=72,
                score_label="보통",
                score_reasons=[
                    "건강 목표와 관련된 기본 후보 성분입니다.",
                    "개인 조건에 따른 추가 확인이 필요할 수 있습니다.",
                ],
                caution_level="medium",
                expected_effects=["정상적인 근육 기능 유지"],
                recommended_dosage="기능성원료 인정현황의 일일섭취량 범위를 따르세요.",
                side_effects=["설사", "복부 불편감"],
                precautions=["신장 질환이 있는 경우 전문가와 상담하세요."],
            )
        ]

    # RAG score 내림차순 + 건강 목표 우선순위 오름차순으로 정렬
    # rag_contexts에 score 필드가 없을 수 있으므로 안전하게 처리
    goal_priority_map = {
        goal.name_en.lower(): goal.priority
        for goal in payload.normalized_input.health_goals
    }

    def sort_key(context):
        score = context.metadata.get("score", 0.0)
        # title/content 기반으로 목표 우선순위 찾기
        title_lower = context.title.lower()
        min_priority = min(
            (p for term, p in goal_priority_map.items() if term in title_lower),
            default=999,
        )
        return (-score, min_priority)

    sorted_contexts = sorted(active_functional_contexts, key=sort_key)

    # 약물/특이사항 이름 집합 구성 (위험 신호 탐지용)
    medication_names = {item.name_en.lower() for item in payload.normalized_input.medications}
    condition_names = {item.name_en.lower() for item in payload.normalized_input.special_conditions}
    risk_terms = medication_names | condition_names

    ingredients = []
    for context in sorted_contexts:
        metadata = context.metadata
        raw_ingredient_name = metadata.get("ingredient_name_ko") or context.title
        iherb_ingredient = match_iherb_ingredient(
            raw_ingredient_name,
            metadata.get("normalized_name"),
            metadata.get("ingredient_name_en"),
            context.title,
        )
        ingredient_name = clean_ingredient_display_name(raw_ingredient_name)
        existing_normalized_name = metadata.get("normalized_name")
        if iherb_ingredient:
            use_iherb_canonical = should_use_iherb_canonical(
                existing_normalized_name,
                raw_ingredient_name,
            )
            if use_iherb_canonical:
                ingredient_name = iherb_ingredient.ingredient_name_ko
                existing_normalized_name = iherb_ingredient.canonical_name

        precautions = as_list(metadata.get("precautions"), [DEFAULT_DISCLAIMER])
        expected_effects = extract_expected_effects(metadata)

        # 약물/질환 위험 신호 탐지 및 precautions 보강
        warning_signals = _detect_risk_signals(metadata, risk_terms)
        for signal in warning_signals:
            warning_msg = f"[주의] {signal}"
            if warning_msg not in precautions:
                precautions.append(warning_msg)

        suitability = calculate_recommendation_suitability(
            context=context,
            metadata=metadata,
            warning_signals=warning_signals,
            has_user_risk_terms=bool(risk_terms),
        )

        ingredients.append(
            RecommendedIngredient(
                name_ko=ingredient_name,
                name_en=metadata.get("ingredient_name_en") or ingredient_name,
                normalized_name=existing_normalized_name or context.title.lower().replace(" ", "_"),
                reason=build_readable_recommendation_reason(
                    ingredient_name=ingredient_name,
                    goal_names=[goal.name_ko for goal in payload.normalized_input.health_goals],
                    functional_component=metadata.get("functional_component"),
                    recommendation_score=suitability["score"],
                    warning_signals=warning_signals,
                ),
                recommendation_score=suitability["score"],
                score_label=suitability["label"],
                score_reasons=suitability["reasons"],
                caution_level=suitability["caution_level"],
                expected_effects=expected_effects,
                recommended_dosage=metadata.get(
                    "daily_dosage",
                    "기능성원료 인정현황의 일일섭취량 범위를 따르세요.",
                ),
                side_effects=as_list(metadata.get("side_effects")),
                precautions=precautions,
            )
        )

    return ingredients


def calculate_recommendation_suitability(
    *,
    context,
    metadata: dict,
    warning_signals: list[str],
    has_user_risk_terms: bool,
) -> dict:
    rag_score = float(metadata.get("score", 0.65) or 0.0)
    score = 55 + round(min(max(rag_score, 0.0), 1.0) * 30)
    reasons = []

    if has_functional_evidence(metadata):
        score += 8
        reasons.append("건강 목표와 관련된 기능성 근거가 확인되었습니다.")
    else:
        reasons.append("관련 근거는 있으나 기능성 설명 확인이 필요합니다.")

    if warning_signals:
        penalty = min(45, 25 + (len(warning_signals) - 1) * 10)
        score -= penalty
        reasons.append("선택한 약물 또는 특이사항과 관련된 주의 신호가 있습니다.")
    elif has_user_risk_terms:
        score -= 8
        reasons.append("복용 약 또는 특이사항을 고려해 보수적으로 평가했습니다.")
    else:
        score += 5
        reasons.append("선택한 약물/특이사항과 큰 충돌 신호가 없습니다.")

    score = max(0, min(95, score))
    return {
        "score": score,
        "label": score_label(score),
        "reasons": reasons,
        "caution_level": caution_level(score, warning_signals),
    }


def score_label(score: int) -> str:
    if score >= 80:
        return "높음"
    if score >= 60:
        return "보통"
    if score >= 40:
        return "주의 필요"
    return "낮음"


def caution_level(score: int, warning_signals: list[str]) -> str:
    if warning_signals or score < 60:
        return "high" if score < 40 else "medium"
    return "low"


def build_disclaimer() -> str:
    return f"{DEFAULT_DISCLAIMER} {SUITABILITY_DISCLAIMER}"


def build_lifestyle_tips(normalized_input) -> list[str]:
    tips = []
    for goal in sorted(normalized_input.health_goals, key=lambda item: item.priority):
        goal_tips = LIFESTYLE_TIPS_BY_GOAL.get(goal.code) or LIFESTYLE_TIPS_BY_GOAL.get(goal.name_en)
        if goal_tips:
            tips.extend(goal_tips)

    if normalized_input.medications or normalized_input.special_conditions:
        tips.append("복용 중인 약이나 특이사항이 있다면 새 성분을 추가하기 전 전문가와 상담해 주세요.")

    if not tips:
        tips = [
            "수면, 식사, 활동량을 일정하게 유지하며 컨디션 변화를 기록해 보세요.",
            "무리한 변화보다 꾸준히 지킬 수 있는 생활 습관을 먼저 정해 보세요.",
        ]

    return dedupe_preserve_order(tips)[:5]


def extract_expected_effects(metadata: dict) -> list[str]:
    effects = as_list(metadata.get("expected_effects"))
    if effects:
        return effects

    functional_claims = as_list(metadata.get("functional_claims"))
    if functional_claims:
        return functional_claims

    return ["기능성 근거 확인 필요"]


def has_functional_evidence(metadata: dict) -> bool:
    return bool(as_list(metadata.get("expected_effects")) or as_list(metadata.get("functional_claims")))


def is_cancelled_functional_ingredient(context) -> bool:
    metadata = context.metadata
    values = [
        context.title,
        metadata.get("ingredient_name_ko"),
        metadata.get("normalized_name"),
    ]
    return any(has_cancelled_approval_marker(value) for value in values)


def has_cancelled_approval_marker(value) -> bool:
    text = str(value or "").replace(" ", "")
    return "인정취소" in text


def build_readable_recommendation_reason(
    *,
    ingredient_name: str,
    goal_names: list[str],
    functional_component: str | None,
    recommendation_score: int,
    warning_signals: list[str],
) -> str:
    goal_text = ", ".join(goal_names[:2]) if goal_names else "선택한 건강 목표"
    component = clean_functional_component(functional_component)

    if recommendation_score >= 80:
        if component:
            reason = f"{ingredient_name}의 {component}은 {goal_text}에 도움줄 수 있어 추천드립니다."
        else:
            reason = f"{ingredient_name}은 {goal_text}에 도움줄 수 있어 추천드립니다."
    elif recommendation_score >= 60:
        if component:
            reason = f"{ingredient_name}의 {component}은 {goal_text}와 관련이 있어 추천 후보로 제안드립니다."
        else:
            reason = f"{ingredient_name}은 {goal_text}와 관련이 있어 추천 후보로 제안드립니다."
    else:
        reason = f"{ingredient_name}은 {goal_text}와의 관련성이 제한적이어서 보조 후보로만 참고해 주세요."

    if warning_signals:
        reason += " 다만 입력하신 복용약과 특이사항을 고려해 적합성은 보수적으로 평가했습니다."

    return reason


def clean_functional_component(value: str | None) -> str:
    components = as_list(value)
    if not components:
        return ""

    component = components[0].strip()
    if not component or component == "-":
        return ""

    return component


def build_recommendation_reason(
    *,
    ingredient_name: str,
    goal_names: list[str],
    expected_effects: list[str],
    warning_signals: list[str],
) -> str:
    goal_text = ", ".join(goal_names[:2]) if goal_names else "선택한 건강 목표"
    effect_text = expected_effects[0] if expected_effects else "관련 기능성"
    reason = f"{ingredient_name}은(는) {goal_text} 목표와 관련해 '{effect_text}' 근거가 확인되어 추천 후보로 선정했습니다."

    if warning_signals:
        reason += " 다만 선택한 약물 또는 특이사항과 관련된 주의 신호가 있어 보수적으로 평가했습니다."

    return reason


def clean_ingredient_display_name(name: str) -> str:
    text = str(name).strip()
    converted_target = re.search(
        r"\([^)]*고시된\s*원료로\s*전환\s*[:：]\s*([^)]*)\)",
        text,
    )
    if converted_target:
        target = converted_target.group(1).strip()
        return target.split(",")[0].strip() or text

    cleaned = re.sub(
        r"\s*\([^)]*고시된\s*원료로\s*전환[^)]*\)",
        "",
        text,
    ).strip()
    return cleaned or text


def as_list(value, fallback=None) -> list[str]:
    if value is None:
        return list(fallback or [])
    if isinstance(value, list):
        return [str(item) for item in value if item not in [None, ""]]
    if isinstance(value, str):
        return [value] if value else list(fallback or [])
    return [str(value)]


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen = set()
    unique = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        unique.append(value)
    return unique


def _detect_risk_signals(metadata: dict, risk_terms: set[str]) -> list[str]:
    """
    RAG metadata의 drugs, conditions, precautions 등에서
    복용 약물/특이사항과 교차하는 위험 신호를 탐지한다.
    """
    signals = []
    for field in RISK_METADATA_FIELDS:
        field_values = as_list(metadata.get(field))
        for value in field_values:
            value_lower = value.lower()
            for term in risk_terms:
                if term in value_lower or value_lower in term:
                    signals.append(value)
                    break
    return signals


def build_strong_risk_clarification(payload: ReportGenerateRequest) -> ReportGenerateResponse | None:
    medication_names = {item.name_en.lower() for item in payload.normalized_input.medications}
    condition_names = {item.name_en.lower() for item in payload.normalized_input.special_conditions}
    risk_terms = medication_names | condition_names
    if not risk_terms:
        return None

    for context in payload.rag_contexts:
        metadata = context.metadata
        signals = _detect_risk_signals(
            {field: metadata.get(field, []) for field in STRONG_RISK_METADATA_FIELDS},
            risk_terms,
        )
        if signals:
            return build_clarification_report_response(payload, signals[0])

    return None


def build_clarification_report_response(
    payload: ReportGenerateRequest,
    signal: str,
) -> ReportGenerateResponse:
    normalized_input = payload.normalized_input
    primary_goal = normalized_input.health_goals[0].name_ko if normalized_input.health_goals else "건강 관리"

    return ReportGenerateResponse(
        status="needs_clarification",
        title=f"{primary_goal} 리포트 추가 확인 필요",
        input_summary=InputSummary(
            age=normalized_input.age,
            gender=normalized_input.gender,
            health_goals=[goal.name_ko for goal in normalized_input.health_goals],
            medications=[item.name_ko for item in normalized_input.medications],
            special_conditions=[item.name_ko for item in normalized_input.special_conditions],
            additional_notes=normalized_input.additional_notes,
        ),
        recommended_ingredients=[],
        lifestyle_tips=[],
        disclaimer=build_disclaimer(),
        citations=[],
        guardrail_result=GuardrailResult(is_allowed=True, risk_level="medium"),
        questions=[
            ClarificationQuestion(
                code="strong_risk_signal",
                message=(
                    f"복용 약 또는 특이사항과 관련된 강한 주의 신호가 확인되었습니다: {signal} "
                    "현재 상태와 복용 정보를 더 구체적으로 확인한 뒤 성분 추천을 진행해 주세요."
                ),
            )
        ],
    )


def build_citations(payload: ReportGenerateRequest) -> list[Citation]:
    # 화면에는 출처 종류만 중복 없이 노출한다.
    citations = []
    seen_sources = set()
    for context in payload.rag_contexts:
        source_name = normalized_source_name(context.source_type, context.source_name)
        if not source_name or source_name in seen_sources:
            continue
        seen_sources.add(source_name)
        citations.append(
            Citation(
                source_type=context.source_type,
                source_name=source_name,
                document_id=context.document_id,
            )
        )

    allowed_ids = {context.document_id for context in payload.rag_contexts}
    return filter_valid_citations(citations, allowed_ids)


def normalized_source_name(source_type: str, source_name: str | None) -> str | None:
    if source_type == "idisk":
        return "iDISK"
    if source_type == "functional_ingredient":
        return FUNCTIONAL_INGREDIENT_SOURCE_NAME
    if source_name in {"iDISK", FUNCTIONAL_INGREDIENT_SOURCE_NAME}:
        return source_name
    return None
