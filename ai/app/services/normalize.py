from app.schemas.normalize import (
    AdditionalTerm,
    ClarificationQuestion,
    NormalizeRequest,
    NormalizeResponse,
    NormalizedGoal,
    NormalizedInput,
    NormalizedItem,
)
from app.services.entity_dictionary import build_rag_query_bundle, match_term

TERM_MAP = {
    "피로": "fatigue",
    "수면": "sleep",
    "항응고제": "anticoagulant",
    "알레르기": "allergy",
    "심장 두근거림": "palpitations",
}

CONFIDENCE_THRESHOLD = 0.7  # 이 값 미만이면 needs_clarification 반환


def normalize_text(name: str, expected_types: set[str] | None = None) -> tuple[str, float, dict | None]:
    term = match_term(name, expected_types)
    if term:
        name_en = TERM_MAP.get(name, (term.get("en") or [term["normalized_name"]])[0])
        return name_en.lower().replace(" ", "_"), term.get("confidence", 0.9), term

    return TERM_MAP.get(name, name.lower().replace(" ", "_")), 0.95 if name in TERM_MAP else 0.6, None


def source_ids(term: dict | None) -> dict[str, list[str]]:
    if not term:
        return {}
    return term.get("source_ids", {})


def normalized_name(term: dict | None, fallback: str) -> str:
    return term["normalized_name"] if term else fallback


def normalize(payload: NormalizeRequest) -> NormalizeResponse:
    goals = []
    for goal in payload.health_goals:
        name_en, confidence, term = normalize_text(goal.name, {"condition", "ingredient"})
        goals.append(
            NormalizedGoal(
                code=goal.code,
                name_ko=goal.name,
                name_en=name_en,
                priority=goal.priority or 1,
                confidence=confidence,
                normalized_name=normalized_name(term, name_en),
                term_type=term.get("term_type") if term else "condition",
                source_ids=source_ids(term),
            )
        )

    medications = [
        normalize_item(item, {"drug"})
        for item in payload.medications
    ]

    special_conditions = [
        normalize_item(item, {"condition", "adverse_reaction"})
        for item in payload.special_conditions
    ]

    additional_terms = []
    if payload.additional_notes and "두근" in payload.additional_notes:
        name_en, confidence, term = normalize_text("심장 두근거림", {"adverse_reaction"})
        additional_terms.append(
            AdditionalTerm(
                text_ko="심장 두근거림",
                text_en=name_en,
                confidence=confidence,
                normalized_name=normalized_name(term, name_en),
                term_type=term.get("term_type") if term else "adverse_reaction",
                source_ids=source_ids(term),
            )
        )

    query_terms = [dump_model(model) for model in goals]
    medication_terms = [dump_model(model) for model in medications]
    condition_terms = [dump_model(model) for model in special_conditions]
    additional_query_terms = [
        {
            "normalized_name": term.normalized_name or term.text_en,
            "term_type": term.term_type,
            "en": [term.text_en],
            "source_ids": term.source_ids,
        }
        for term in additional_terms
    ]
    rag_query_bundle = build_rag_query_bundle(
        query_terms,
        medication_terms,
        condition_terms,
        additional_query_terms,
    )
    search_queries = rag_query_bundle["text_queries"]

    clarification_questions = _build_confidence_clarification_questions(
        goals, medications, special_conditions
    )
    if clarification_questions:
        return NormalizeResponse(
            normalized_input=NormalizedInput(
                health_goals=goals,
                medications=medications,
                special_conditions=special_conditions,
                additional_terms=additional_terms,
            ),
            search_queries=search_queries,
            rag_query_bundle=rag_query_bundle,
            needs_clarification=True,
            questions=clarification_questions,
        )

    return NormalizeResponse(
        normalized_input=NormalizedInput(
            health_goals=goals,
            medications=medications,
            special_conditions=special_conditions,
            additional_terms=additional_terms,
        ),
        search_queries=search_queries,
        rag_query_bundle=rag_query_bundle,
        needs_clarification=False,
        questions=[],
    )


def normalize_item(item, expected_types: set[str]) -> NormalizedItem:
    name_en, confidence, term = normalize_text(item.name, expected_types)
    return NormalizedItem(
        code=item.code,
        name_ko=item.name,
        name_en=name_en,
        confidence=confidence,
        normalized_name=normalized_name(term, name_en),
        term_type=term.get("term_type") if term else next(iter(expected_types)),
        source_ids=source_ids(term),
    )


def dump_model(model) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def _build_confidence_clarification_questions(
    goals: list,
    medications: list,
    special_conditions: list,
) -> list[ClarificationQuestion]:
    """
    confidence 임계값 미만인 항목이 있으면 사용자에게 확인 질문을 생성한다.
    """
    questions = []

    for goal in goals:
        if goal.confidence < CONFIDENCE_THRESHOLD:
            questions.append(
                ClarificationQuestion(
                    code="low_confidence_health_goal",
                    message=f"'{goal.name_ko}' 건강 목표를 정확히 이해하지 못했습니다. 조금 더 구체적으로 설명해 주시겠어요?",
                )
            )

    for med in medications:
        if med.confidence < CONFIDENCE_THRESHOLD:
            questions.append(
                ClarificationQuestion(
                    code="low_confidence_medication",
                    message=f"'{med.name_ko}' 복용 약물을 정확히 파악하지 못했습니다. 약물 이름을 다시 한번 확인해 주시겠어요?",
                )
            )

    for cond in special_conditions:
        if cond.confidence < CONFIDENCE_THRESHOLD:
            questions.append(
                ClarificationQuestion(
                    code="low_confidence_special_condition",
                    message=f"'{cond.name_ko}' 특이사항을 정확히 이해하지 못했습니다. 조금 더 자세히 설명해 주시겠어요?",
                )
            )

    return questions
