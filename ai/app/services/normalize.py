from app.schemas.normalize import (
    AdditionalTerm,
    NormalizeRequest,
    NormalizeResponse,
    NormalizedGoal,
    NormalizedInput,
    NormalizedItem,
)

TERM_MAP = {
    "피로": "fatigue",
    "수면": "sleep",
    "항응고제": "anticoagulant",
    "알레르기": "allergy",
    "심장 두근거림": "palpitations",
}


def normalize_text(name: str) -> tuple[str, float]:
    return TERM_MAP.get(name, name.lower().replace(" ", "_")), 0.95 if name in TERM_MAP else 0.6


def normalize(payload: NormalizeRequest) -> NormalizeResponse:
    goals = []
    for goal in payload.health_goals:
        name_en, confidence = normalize_text(goal.name)
        goals.append(
            NormalizedGoal(
                code=goal.code,
                name_ko=goal.name,
                name_en=name_en,
                priority=goal.priority or 1,
                confidence=confidence,
            )
        )

    medications = [
        NormalizedItem(code=item.code, name_ko=item.name, name_en=normalize_text(item.name)[0], confidence=normalize_text(item.name)[1])
        for item in payload.medications
    ]

    special_conditions = [
        NormalizedItem(code=item.code, name_ko=item.name, name_en=normalize_text(item.name)[0], confidence=normalize_text(item.name)[1])
        for item in payload.special_conditions
    ]

    additional_terms = []
    if payload.additional_notes and "두근" in payload.additional_notes:
        additional_terms.append(AdditionalTerm(text_ko="심장 두근거림", text_en="palpitations", confidence=0.88))

    search_queries = []
    goal_terms = [goal.name_en for goal in goals]
    if goal_terms:
        search_queries.append(" ".join(goal_terms + ["supplements"]))

    for term in additional_terms:
        search_queries.append(f"{term.text_en} supplement precautions")

    for medication in medications:
        search_queries.append(f"{medication.name_en} supplement precautions")

    return NormalizeResponse(
        normalized_input=NormalizedInput(
            health_goals=goals,
            medications=medications,
            special_conditions=special_conditions,
            additional_terms=additional_terms,
        ),
        search_queries=search_queries,
    )