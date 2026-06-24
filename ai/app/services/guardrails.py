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

UNSAFE_OUTPUT_RULES = [
    {
        "keywords": ["반드시 낫습니다", "확실히 치료", "완치됩니다", "진단합니다"],
        "fix": "질병의 진단, 치료, 완치처럼 단정적인 의료 표현을 제거하세요.",
    },
    {
        "keywords": ["약을 중단하세요", "약을 끊으세요", "복용량을 늘리세요", "복용량을 줄이세요"],
        "fix": "약물 중단, 변경, 용량 조절 지시를 제거하고 전문가 상담 안내로 바꾸세요.",
    },
    {
        "keywords": ["이 제품을 구매하세요", "바로 구매하세요", "최저가로 사세요"],
        "fix": "특정 제품 구매를 유도하는 문구를 제거하세요.",
    },
]

DISCLAIMER_FIX = "건강 위험이나 섭취 주의사항이 있는 답변에는 전문가 상담 안내를 포함하세요."
DISCLAIMER_KEYWORDS = ["전문가와 상담", "의사와 상담", "약사와 상담"]
HEALTH_RISK_KEYWORDS = ["질환", "복용", "약", "부작용", "주의", "처방", "치료"]
DEFAULT_SAFE_MESSAGE = "응답에 의료적으로 부적절한 표현이 포함되어 제공할 수 없습니다. 질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요."


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
    required_fixes = []

    for rule in UNSAFE_OUTPUT_RULES:
        if any(keyword in payload.content for keyword in rule["keywords"]):
            required_fixes.append(rule["fix"])

    if needs_disclaimer(payload.content):
        required_fixes.append(DISCLAIMER_FIX)

    if required_fixes:
        return OutputGuardrailResponse(
            is_allowed=False,
            risk_level="high",
            blocked_reason="unsafe_medical_output",
            safe_message=DEFAULT_SAFE_MESSAGE,
            required_fixes=required_fixes,
        )

    return OutputGuardrailResponse(is_allowed=True, risk_level="low")


def needs_disclaimer(content: str) -> bool:
    has_health_risk = any(keyword in content for keyword in HEALTH_RISK_KEYWORDS)
    has_disclaimer = any(keyword in content for keyword in DISCLAIMER_KEYWORDS)
    return has_health_risk and not has_disclaimer
