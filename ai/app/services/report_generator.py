from app.schemas.common import Citation, GuardrailResult
from app.schemas.reports import (
    InputSummary,
    RecommendedIngredient,
    ReportGenerateRequest,
    ReportGenerateResponse,
)

DEFAULT_DISCLAIMER = "질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요."


def generate_report(payload: ReportGenerateRequest) -> ReportGenerateResponse:
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
                reason="피로와 수면 관리에 관련된 근거가 검색되어 후보로 선정되었습니다.",
                expected_effects=["정상적인 근육 기능 유지"],
                recommended_dosage="기능성원료 인정현황의 일일섭취량 범위를 따르세요.",
                side_effects=["설사", "복부 불편감"],
                precautions=["신장 질환이 있는 경우 전문가와 상담하세요."],
            )
        ]

    ingredients = []

    for context in functional_contexts:
        metadata = context.metadata
        ingredients.append(
            RecommendedIngredient(
                name_ko=metadata.get("ingredient_name_ko", context.title),
                name_en=metadata.get("ingredient_name_en", context.title),
                normalized_name=metadata.get("normalized_name", context.title.lower().replace(" ", "_")),
                reason="사용자 입력과 RAG 검색 결과를 바탕으로 관련 성분 후보로 선정되었습니다.",
                expected_effects=metadata.get("expected_effects", ["기능성 근거 확인 필요"]),
                recommended_dosage=metadata.get(
                    "daily_dosage",
                    "기능성원료 인정현황의 일일섭취량 범위를 따르세요.",
                ),
                side_effects=metadata.get("side_effects", []),
                precautions=metadata.get("precautions", [DEFAULT_DISCLAIMER]),
            )
        )

    return ingredients


def build_citations(payload: ReportGenerateRequest) -> list[Citation]:
    citations = []

    for context in payload.rag_contexts:
        citations.append(
            Citation(
                source_type=context.source_type,
                source_name=context.source_name,
                document_id=context.document_id,
            )
        )

    return citations