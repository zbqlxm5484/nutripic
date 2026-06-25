from app.schemas.common import Citation, GuardrailResult
from app.schemas.reports import (
    ClarificationQuestion,
    InputSummary,
    RecommendedIngredient,
    ReportGenerateRequest,
    ReportGenerateResponse,
)
from app.services.guardrails import filter_valid_citations
from app.services.llm_generation import generate_report_with_llm

DEFAULT_DISCLAIMER = "질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요."

# RAG metadata에서 위험 신호를 나타내는 필드
RISK_METADATA_FIELDS = ["precautions", "drugs", "conditions", "contraindications", "side_effects"]
STRONG_RISK_METADATA_FIELDS = ["contraindications", "drug_interactions"]


def generate_report(payload: ReportGenerateRequest) -> ReportGenerateResponse:
    clarification_response = build_strong_risk_clarification(payload)
    if clarification_response:
        return clarification_response

    fallback_response = build_template_report(payload)
    return generate_report_with_llm(payload, fallback_response)


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
        lifestyle_tips=[
            "수면 시간을 일정하게 유지하세요.",
            "카페인 섭취 시간과 양을 조절해 보세요.",
        ],
        disclaimer=DEFAULT_DISCLAIMER,
        citations=citations,
        guardrail_result=GuardrailResult(is_allowed=True, risk_level="low"),
    )


def build_recommended_ingredients(payload: ReportGenerateRequest) -> list[RecommendedIngredient]:
    functional_contexts = [
        context for context in payload.rag_contexts if context.source_type == "functional_ingredient"
    ]

    if not functional_contexts:
        return [
            RecommendedIngredient(
                name_ko="마그네슘",
                name_en="Magnesium",
                normalized_name="magnesium",
                reason="피로와 수면 관리에 관련된 근거가 검색되어 후보로 선정했습니다.",
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

    sorted_contexts = sorted(functional_contexts, key=sort_key)

    # 약물/특이사항 이름 집합 구성 (위험 신호 탐지용)
    medication_names = {item.name_en.lower() for item in payload.normalized_input.medications}
    condition_names = {item.name_en.lower() for item in payload.normalized_input.special_conditions}
    risk_terms = medication_names | condition_names

    ingredients = []
    for context in sorted_contexts:
        metadata = context.metadata
        precautions = list(metadata.get("precautions", [DEFAULT_DISCLAIMER]))

        # 약물/질환 위험 신호 탐지 및 precautions 보강
        warning_signals = _detect_risk_signals(metadata, risk_terms)
        for signal in warning_signals:
            warning_msg = f"[주의] {signal}"
            if warning_msg not in precautions:
                precautions.append(warning_msg)

        ingredients.append(
            RecommendedIngredient(
                name_ko=ingredient_name,
                name_en=metadata.get("ingredient_name_en") or ingredient_name,
                normalized_name=metadata.get("normalized_name") or context.title.lower().replace(" ", "_"),
                reason="사용자 입력과 RAG 검색 결과를 바탕으로 관련 성분 후보로 선정했습니다.",
                expected_effects=metadata.get("expected_effects", ["기능성 근거 확인 필요"]),
                recommended_dosage=metadata.get(
                    "daily_dosage",
                    "기능성원료 인정현황의 일일섭취량 범위를 따르세요.",
                ),
                side_effects=metadata.get("side_effects", []),
                precautions=precautions,
            )
        )

    return ingredients


def _detect_risk_signals(metadata: dict, risk_terms: set[str]) -> list[str]:
    """
    RAG metadata의 drugs, conditions, precautions 등에서
    복용 약물/특이사항과 교차하는 위험 신호를 탐지한다.
    """
    signals = []
    for field in RISK_METADATA_FIELDS:
        field_values = metadata.get(field, [])
        if isinstance(field_values, str):
            field_values = [field_values]
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
        disclaimer=DEFAULT_DISCLAIMER,
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
    # RAG context에 실제 존재하는 document_id만 허용
    allowed_ids = {context.document_id for context in payload.rag_contexts}

    all_citations = [
        Citation(
            source_type=context.source_type,
            source_name=context.source_name,
            document_id=context.document_id,
        )
        for context in payload.rag_contexts
    ]

    return filter_valid_citations(all_citations, allowed_ids)
