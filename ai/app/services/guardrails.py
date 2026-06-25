from app.schemas.guardrails import (
    InputGuardrailRequest,
    InputGuardrailResponse,
    OutputGuardrailRequest,
    OutputGuardrailResponse,
)

import re

# ── 입력 가드레일 ──────────────────────────────────────────────

HIGH_RISK_INPUT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"진단\s*(해줘|해주세요|해\s*줘|해\s*주세요|가능|결과)",
        r"처방\s*(해줘|해주세요|해\s*줘|해\s*주세요|받고|가능)",
        r"(약|복용약|처방약|항응고제|혈압약|당뇨약|항우울제)\s*(을|를)?\s*(끊|중단|중지|줄|늘|증량|감량|바꾸|대체)",
        r"(복용량|용량)\s*(을|를)?\s*(늘|줄|증량|감량|조절)",
        r"병원\s*(안|가지\s*않|갈\s*필요\s*없)",
        r"수술\s*(받아야|해야|필요)",
        r"(가슴\s*통증|호흡\s*곤란|숨\s*쉬기\s*힘|의식\s*잃|극심한\s*통증)",
        r"(자살|극단적\s*선택|죽고\s*싶|해치고\s*싶)",
    ]
]

PROMPT_INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"(이전|위|앞선)\s*(지시|명령|규칙)\s*(무시|삭제|잊)",
        r"(system|developer|assistant)\s*(prompt|message|instruction)",
        r"(시스템|개발자)\s*(프롬프트|메시지|지시)",
        r"ignore\s+(all\s+)?previous",
        r"reveal\s+(the\s+)?(prompt|system)",
        r"jailbreak|DAN\s*mode",
        r"act\s+as\s+(a\s+)?(\w+\s+)?(doctor|developer|system)",
        r"너는\s*(이제|지금부터)\s*(의사|개발자|시스템)",
    ]
]

# 서비스 범위 이탈 키워드 (건강기능식품 추천 서비스 외 요청)
OUT_OF_SCOPE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"성형",
        r"(다이어트|체중\s*감량)\s*(약|처방|주사)",
        r"처방약\s*추천",
        r"정신과\s*처방",
        r"항우울제\s*추천",
        r"(마약|불법|스테로이드|도핑)",
        r"(제품|브랜드|쇼핑몰|최저가|구매처)\s*(추천|알려|찾아)",
    ]
]

# 개인정보 과다 입력 패턴 (정규표현식으로 체크)
PERSONAL_INFO_PATTERNS = [
    re.compile(r"\d{6}[-–]\d{7}"),  # 주민등록번호
    re.compile(r"01[016789][-–\s]?\d{3,4}[-–\s]?\d{4}"),  # 휴대폰 번호
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),  # 이메일
    re.compile(r"\d{4}[-\s]\d{4}[-\s]\d{4}[-\s]\d{4}"),  # 카드 번호
    re.compile(r"(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주).{0,30}(로|길|동)\s*\d+"),
]

# ── 출력 가드레일 ──────────────────────────────────────────────

UNSAFE_OUTPUT_RULES = [
    {
        "patterns": [
            re.compile(pattern)
            for pattern in [
                r"반드시\s*낫",
                r"확실히\s*치료",
                r"완치\s*됩니다?",
                r"진단\s*합니다",
                r"질병\s*을?\s*치료",
            ]
        ],
        "fix": "질병의 진단, 치료, 완치처럼 단정적인 의료 표현을 제거하세요.",
    },
    {
        "patterns": [
            re.compile(pattern)
            for pattern in [
                r"약(을|를)?\s*(중단|끊|바꾸)",
                r"복용량(을|를)?\s*(늘|줄|증량|감량)",
                r"처방(을|를)?\s*변경",
            ]
        ],
        "fix": "약물 중단, 변경, 용량 조절 지시를 제거하고 전문가 상담 안내로 바꾸세요.",
    },
    {
        "patterns": [
            re.compile(pattern)
            for pattern in [
                r"이\s*제품(을|를)?\s*구매",
                r"바로\s*구매",
                r"최저가로\s*사",
                r"브랜드\s*추천",
            ]
        ],
        "fix": "특정 제품 구매를 유도하는 문구를 제거하세요.",
    },
    {
        "patterns": [
            re.compile(pattern)
            for pattern in [
                r"100%\s*효과",
                r"무조건\s*좋아",
                r"반드시\s*효과",
                r"절대\s*안전",
                r"부작용\s*없",
            ]
        ],
        "fix": "과도한 확신 표현을 제거하고 개인차가 있다는 표현으로 바꾸세요.",
    },
    {
        "patterns": [
            re.compile(pattern)
            for pattern in [
                r"완전히\s*안전",
                r"전혀\s*위험하지\s*않",
                r"누구나\s*안전",
            ]
        ],
        "fix": "안전에 관한 단정적 표현을 제거하고 전문가 상담 안내를 포함하세요.",
    },
]

DISCLAIMER_FIX = "건강 위험이나 섭취 주의사항이 있는 답변에는 전문가 상담 안내를 포함하세요."
DISCLAIMER_KEYWORDS = ["전문가와 상담", "의사와 상담", "약사와 상담"]
HEALTH_RISK_KEYWORDS = ["질환", "복용", "약", "부작용", "주의", "처방", "치료"]
EVIDENCE_CLAIM_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        r"(연구|근거|논문|데이터|자료).{0,20}(입증|확인|보여|근거)",
        r"(효과|기능성).{0,20}(입증|확인)",
    ]
]
DEFAULT_SAFE_MESSAGE = "응답에 의료적으로 부적절한 표현이 포함되어 제공할 수 없습니다. 질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요."


def check_input_guardrail(payload: InputGuardrailRequest) -> InputGuardrailResponse:
    text = normalize_text(payload.input_text)
    original_text = payload.input_text

    # 프롬프트 인젝션 탐지
    if matches_any(PROMPT_INJECTION_PATTERNS, text):
        return InputGuardrailResponse(
            is_allowed=False,
            risk_level="high",
            blocked_reason="prompt_injection",
            safe_message="요청을 처리할 수 없습니다.",
        )

    # 개인정보 과다 입력 탐지
    if matches_any(PERSONAL_INFO_PATTERNS, original_text):
        return InputGuardrailResponse(
            is_allowed=False,
            risk_level="high",
            blocked_reason="excessive_personal_info",
            safe_message="개인 식별 정보(주민등록번호, 전화번호, 이메일, 주소 등)는 입력하지 마세요. 해당 정보 없이 건강 목표와 증상만 입력해 주세요.",
        )

    # 고위험 의료 요청 탐지 (약물 중단/변경 등)
    if matches_any(HIGH_RISK_INPUT_PATTERNS, text):
        return InputGuardrailResponse(
            is_allowed=False,
            risk_level="high",
            blocked_reason="medical_high_risk",
            safe_message="의학적 진단, 처방, 약물 변경은 제공할 수 없습니다. 전문가와 상담하세요.",
        )

    # 서비스 범위 이탈 탐지
    if matches_any(OUT_OF_SCOPE_PATTERNS, text):
        return InputGuardrailResponse(
            is_allowed=False,
            risk_level="medium",
            blocked_reason="out_of_scope",
            safe_message="이 서비스는 건강기능식품 성분 추천만 제공합니다. 의약품 처방이나 의료 상담은 전문가에게 문의하세요.",
        )

    return InputGuardrailResponse(is_allowed=True, risk_level="low")


def check_output_guardrail(payload: OutputGuardrailRequest) -> OutputGuardrailResponse:
    required_fixes = []

    for rule in UNSAFE_OUTPUT_RULES:
        if matches_any(rule["patterns"], payload.content):
            required_fixes.append(rule["fix"])

    if needs_disclaimer(payload.content):
        required_fixes.append(DISCLAIMER_FIX)

    if makes_evidence_claim_without_citation(payload.content, payload.citations):
        required_fixes.append("근거 또는 연구를 언급하는 문장은 citations가 있는 데이터에 기반해야 합니다.")

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


def makes_evidence_claim_without_citation(content: str, citations: list) -> bool:
    return not citations and matches_any(EVIDENCE_CLAIM_PATTERNS, content)


def matches_any(patterns: list[re.Pattern], text: str) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def filter_valid_citations(citations: list, allowed_document_ids: set) -> list:
    """
    RAG context에 실제로 존재하는 document_id를 가진 citation만 허용한다.
    근거 없는 citation은 제거한다.
    """
    if not allowed_document_ids:
        return []
    return [c for c in citations if c.document_id in allowed_document_ids]
