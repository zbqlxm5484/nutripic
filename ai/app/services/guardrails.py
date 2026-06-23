from app.schemas.guardrails import (
    InputGuardrailRequest,
    InputGuardrailResponse,
    OutputGuardrailRequest,
    OutputGuardrailResponse,
)

HIGH_RISK_INPUT_KEYWORDS = [
    "진단해줘",
    "처방해줘",
    "약 끊어",
    "약 중단",
    "약 늘려",
    "약 줄여",
]

PROMPT_INJECTION_KEYWORDS = [
    "이전 지시 무시",
    "system prompt",
    "시스템 프롬프트",
]

UNSAFE_OUTPUT_KEYWORDS = [
    "반드시 낫습니다",
    "약을 중단하세요",
    "약을 늘리세요",
    "이 제품을 구매하세요",
    "진단됩니다",
]


def check_input_guardrail(payload: InputGuardrailRequest) -> InputGuardrailResponse:
    text = payload.input_text.lower()

    if any(keyword.lower() in text for keyword in PROMPT_INJECTION_KEYWORDS):
        return InputGuardrailResponse(
            is_allowed=False,
            risk_level="high",
            blocked_reason="prompt_injection",
            safe_message="요청을 처리할 수 없습니다.",
        )

    if any(keyword in payload.input_text for keyword in HIGH_RISK_INPUT_KEYWORDS):
        return InputGuardrailResponse(
            is_allowed=False,
            risk_level="high",
            blocked_reason="medical_high_risk",
            safe_message="의학적 진단, 처방, 약물 변경은 제공할 수 없습니다. 전문가와 상담하세요.",
        )

    return InputGuardrailResponse(is_allowed=True, risk_level="low")


def check_output_guardrail(payload: OutputGuardrailRequest) -> OutputGuardrailResponse:
    required_fixes = [keyword for keyword in UNSAFE_OUTPUT_KEYWORDS if keyword in payload.content]

    if required_fixes:
        return OutputGuardrailResponse(
            is_allowed=False,
            risk_level="high",
            blocked_reason="unsafe_medical_output",
            safe_message="응답에 의료적으로 부적절한 표현이 포함되어 수정이 필요합니다.",
            required_fixes=required_fixes,
        )

    return OutputGuardrailResponse(is_allowed=True, risk_level="low")