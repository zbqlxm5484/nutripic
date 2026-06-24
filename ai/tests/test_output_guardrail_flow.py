import os

os.environ.setdefault("AI_INTERNAL_API_KEY", "test_internal_key")
os.environ["AI_GENERATION_PROVIDER"] = "fallback"

from app.core.config import settings
from app.schemas.chat import (
    ChatMessage,
    ChatRespondRequest,
    ChatRespondResponse,
    ReportContext,
    ReportIngredientContext,
)
from app.schemas.common import GuardrailResult
from app.schemas.reports import (
    InputSummary,
    NormalizedGoal,
    ReportGenerateRequest,
    ReportGenerateResponse,
    ReportNormalizedInput,
)
from app.services import llm_generation
from app.services.guardrails import check_output_guardrail
from app.schemas.guardrails import OutputGuardrailRequest


def test_output_guardrail_returns_required_fixes_for_unsafe_content():
    result = check_output_guardrail(
        OutputGuardrailRequest(
            request_id="req_test_guardrail",
            task_type="chat_response",
            content="이 성분은 확실히 치료됩니다. 약을 중단하세요.",
            citations=[],
        )
    )

    assert result.is_allowed is False
    assert result.risk_level == "high"
    assert result.blocked_reason == "unsafe_medical_output"
    assert len(result.required_fixes) >= 2
    assert result.safe_message


def test_chat_generation_rewrites_when_output_guardrail_fails(monkeypatch):
    enable_fake_llm(monkeypatch)
    responses = [
        ChatRespondResponse(
            content="마그네슘을 먹으면 확실히 치료됩니다. 약을 중단하세요.",
            citations=[],
            guardrail_result=GuardrailResult(is_allowed=True, risk_level="low"),
        ),
        ChatRespondResponse(
            content="마그네슘은 개인 상태에 따라 섭취 방법이 달라질 수 있습니다. 질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.",
            citations=[],
            guardrail_result=GuardrailResult(is_allowed=True, risk_level="low"),
        ),
    ]
    calls = []

    def fake_invoke_chat_model(prompt: str):
        calls.append(prompt)
        return responses[len(calls) - 1].model_dump_json()

    monkeypatch.setattr(llm_generation, "invoke_chat_model", fake_invoke_chat_model)

    result = llm_generation.generate_chat_with_llm(
        build_chat_request(),
        ChatRespondResponse(
            content="기본 답변입니다. 질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.",
            citations=[],
            guardrail_result=GuardrailResult(is_allowed=True, risk_level="low"),
        ),
    )

    assert len(calls) == 2
    assert "required_fixes" in calls[1]
    assert result.guardrail_result.is_allowed is True
    assert "약을 중단하세요" not in result.content
    assert "전문가와 상담" in result.content


def test_report_generation_blocks_when_rewrite_still_fails(monkeypatch):
    enable_fake_llm(monkeypatch)
    unsafe_report = build_report_response("마그네슘으로 확실히 치료됩니다. 약을 중단하세요.")

    def fake_invoke_chat_model(prompt: str):
        return unsafe_report.model_dump_json()

    monkeypatch.setattr(llm_generation, "invoke_chat_model", fake_invoke_chat_model)

    result = llm_generation.generate_report_with_llm(
        build_report_request(),
        build_report_response("기본 리포트입니다. 질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요."),
    )

    assert result.status == "blocked"
    assert result.guardrail_result.is_allowed is False
    assert result.recommended_ingredients == []
    assert "의료적으로 부적절한 표현" in result.disclaimer


def enable_fake_llm(monkeypatch):
    monkeypatch.setattr(settings, "ai_generation_provider", "openai")
    monkeypatch.setattr(settings, "openai_api_key", "test_key")
    monkeypatch.setattr(settings, "openai_base_url", "https://example.com/v1")
    monkeypatch.setattr(settings, "ai_model_name", "gpt-5-nano")


def build_chat_request() -> ChatRespondRequest:
    return ChatRespondRequest(
        request_id="req_test_chat_guardrail",
        user_id=1,
        report_id=10,
        report_context=ReportContext(
            title="피로 개선 리포트",
            recommended_ingredients=[
                ReportIngredientContext(
                    name_ko="마그네슘",
                    name_en="Magnesium",
                    normalized_name="magnesium",
                    precautions=["신장 질환이 있는 경우 전문가와 상담하세요."],
                )
            ],
            disclaimer="질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.",
        ),
        message=ChatMessage(content="마그네슘은 언제 먹는 게 좋아?"),
        recent_messages=[],
    )


def build_report_request() -> ReportGenerateRequest:
    return ReportGenerateRequest(
        request_id="req_test_report_guardrail",
        user_id=1,
        normalized_input=ReportNormalizedInput(
            age=30,
            gender="female",
            health_goals=[
                NormalizedGoal(
                    code="fatigue",
                    name_ko="피로",
                    name_en="fatigue",
                    priority=1,
                    confidence=0.98,
                )
            ],
            medications=[],
            special_conditions=[],
            additional_notes=None,
            additional_terms=[],
        ),
        rag_contexts=[],
    )


def build_report_response(reason: str) -> ReportGenerateResponse:
    return ReportGenerateResponse(
        status="completed",
        title="피로 개선을 위한 성분 리포트",
        input_summary=InputSummary(
            age=30,
            gender="female",
            health_goals=["피로"],
            medications=[],
            special_conditions=[],
            additional_notes=None,
        ),
        recommended_ingredients=[],
        lifestyle_tips=[reason],
        disclaimer="질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.",
        citations=[],
        guardrail_result=GuardrailResult(is_allowed=True, risk_level="low"),
    )
