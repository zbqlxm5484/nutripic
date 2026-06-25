from app.schemas.chat import ChatRespondRequest, ChatRespondResponse
from app.schemas.common import Citation, GuardrailResult
from app.services.llm_generation import generate_chat_with_llm

DEFAULT_SAFE_MESSAGE = "의학적 진단, 처방, 약물 변경은 제공할 수 없습니다. 질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요."

HIGH_RISK_CHAT_KEYWORDS = [
    "진단",
    "처방",
    "복용량",
    "약 중단",
    "수술",
    "치료",
]


def respond_chat(payload: ChatRespondRequest) -> ChatRespondResponse:
    fallback_response = build_template_chat_response(payload)
    return generate_chat_with_llm(payload, fallback_response)


def build_template_chat_response(payload: ChatRespondRequest) -> ChatRespondResponse:
    message = payload.message.content

    if is_high_risk_question(message):
        return ChatRespondResponse(
            content=DEFAULT_SAFE_MESSAGE,
            citations=[],
            guardrail_result=GuardrailResult(is_allowed=True, risk_level="high"),
        )

    ingredient = find_related_ingredient(payload)

    if ingredient:
        content = (
            f"{ingredient.name_ko}({ingredient.name_en})에 대한 질문으로 이해했습니다. "
            "일반적으로 건강기능식품 성분은 개인의 상태, 복용 중인 약, 제품 형태에 따라 섭취 방법이 달라질 수 있습니다. "
            f"특히 {', '.join(ingredient.precautions) if ingredient.precautions else '주의사항을 확인해야 합니다.'} "
            "질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요."
        )

        citations = [
            Citation(
                source_type="functional_ingredient",
                source_name="건강기능식품 기능성원료 인정현황",
                document_id=f"functional_ingredient_{ingredient.normalized_name}",
            )
        ]

        return ChatRespondResponse(
            content=content,
            citations=citations,
            guardrail_result=GuardrailResult(is_allowed=True, risk_level="low"),
        )

    return ChatRespondResponse(
        content=(
            "해당 질문은 현재 저장된 리포트의 추천 성분 정보 안에서 명확히 확인하기 어렵습니다. "
            "리포트에 포함된 성분, 섭취 및 주의사항, 일반적인 건강기능식품 정보 범위에서 다시 질문해 주세요."
        ),
        citations=[],
        guardrail_result=GuardrailResult(is_allowed=True, risk_level="low"),
    )


def is_high_risk_question(message: str) -> bool:
    return any(keyword in message for keyword in HIGH_RISK_CHAT_KEYWORDS)


def find_related_ingredient(payload: ChatRespondRequest):
    message = payload.message.content.lower()

    for ingredient in payload.report_context.recommended_ingredients:
        if ingredient.name_ko in payload.message.content:
            return ingredient

        if ingredient.name_en.lower() in message:
            return ingredient

        if ingredient.normalized_name.lower() in message:
            return ingredient

    if payload.report_context.recommended_ingredients:
        return payload.report_context.recommended_ingredients[0]

    return None
