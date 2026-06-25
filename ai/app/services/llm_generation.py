import json

from openai import OpenAI

from app.core.config import settings
from app.schemas.chat import ChatRespondRequest, ChatRespondResponse
from app.schemas.common import Citation, GuardrailResult
from app.schemas.guardrails import OutputGuardrailRequest, OutputGuardrailResponse
from app.schemas.reports import ReportGenerateRequest, ReportGenerateResponse
from app.services.guardrails import DEFAULT_SAFE_MESSAGE, check_output_guardrail, filter_valid_citations

SYSTEM_PROMPT = (
    "You are the internal AI generation layer for Neutripic. "
    "Return only valid JSON that matches the requested schema. "
    "Write all user-facing text in Korean. "
    "Do not provide diagnosis, prescription, treatment instructions, medication changes, "
    "or product purchase persuasion. "
    "Use only the supplied context and citations. "
    "Use cautious language and include this disclaimer when relevant: "
    "'질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.'"
)


def generate_report_with_llm(
    payload: ReportGenerateRequest,
    fallback_response: ReportGenerateResponse,
) -> ReportGenerateResponse:
    candidate = fallback_response

    if is_llm_enabled():
        content = invoke_chat_model(build_report_prompt(payload, fallback_response))
        parsed_response = parse_report_response(content)
        if parsed_response:
            candidate = parsed_response

    return apply_report_output_guardrail(payload, candidate, fallback_response)


def generate_chat_with_llm(
    payload: ChatRespondRequest,
    fallback_response: ChatRespondResponse,
) -> ChatRespondResponse:
    candidate = fallback_response

    if is_llm_enabled():
        content = invoke_chat_model(build_chat_prompt(payload, fallback_response))
        parsed_response = parse_chat_response(content)
        if parsed_response:
            candidate = parsed_response

    return apply_chat_output_guardrail(payload, candidate)


def apply_report_output_guardrail(
    payload: ReportGenerateRequest,
    candidate: ReportGenerateResponse,
    fallback_response: ReportGenerateResponse,
) -> ReportGenerateResponse:
    candidate.citations = filter_report_citations(candidate, payload)
    guardrail = check_output_guardrail(
        OutputGuardrailRequest(
            request_id=payload.request_id,
            task_type="report_generation",
            content=serialize_report_content(candidate),
            citations=candidate.citations,
        )
    )
    if guardrail.is_allowed:
        return with_report_guardrail(candidate, guardrail)

    if is_llm_enabled():
        rewrite = rewrite_report_response(
            payload, candidate, fallback_response, guardrail
        )
        if rewrite:
            rewrite.citations = filter_report_citations(rewrite, payload)
            rewrite_guardrail = check_output_guardrail(
                OutputGuardrailRequest(
                    request_id=payload.request_id,
                    task_type="report_generation",
                    content=serialize_report_content(rewrite),
                    citations=rewrite.citations,
                )
            )
            if rewrite_guardrail.is_allowed:
                return with_report_guardrail(rewrite, rewrite_guardrail)

    return build_blocked_report_response(payload, fallback_response, guardrail)


def apply_chat_output_guardrail(
    payload: ChatRespondRequest,
    candidate: ChatRespondResponse,
) -> ChatRespondResponse:
    candidate.citations = filter_chat_citations(candidate, payload)
    guardrail = check_output_guardrail(
        OutputGuardrailRequest(
            request_id=payload.request_id,
            task_type="chat_response",
            content=candidate.content,
            citations=candidate.citations,
        )
    )
    if guardrail.is_allowed:
        return with_chat_guardrail(candidate, guardrail)

    if is_llm_enabled():
        rewrite = rewrite_chat_response(payload, candidate, guardrail)
        if rewrite:
            rewrite.citations = filter_chat_citations(rewrite, payload)
            rewrite_guardrail = check_output_guardrail(
                OutputGuardrailRequest(
                    request_id=payload.request_id,
                    task_type="chat_response",
                    content=rewrite.content,
                    citations=rewrite.citations,
                )
            )
            if rewrite_guardrail.is_allowed:
                return with_chat_guardrail(rewrite, rewrite_guardrail)

    return build_blocked_chat_response(guardrail)


def rewrite_report_response(
    payload: ReportGenerateRequest,
    candidate: ReportGenerateResponse,
    fallback_response: ReportGenerateResponse,
    guardrail: OutputGuardrailResponse,
) -> ReportGenerateResponse | None:
    content = invoke_chat_model(
        build_rewrite_prompt(
            task="rewrite_ingredient_report",
            output_schema=build_report_output_schema(),
            current_response=candidate.model_dump(),
            required_fixes=guardrail.required_fixes,
            safe_message=guardrail.safe_message,
            source_context={
                "normalized_input": payload.normalized_input.model_dump(),
                "rag_contexts": [
                    context.model_dump() for context in payload.rag_contexts
                ],
                "fallback_response": fallback_response.model_dump(),
            },
        )
    )
    return parse_report_response(content)


def rewrite_chat_response(
    payload: ChatRespondRequest,
    candidate: ChatRespondResponse,
    guardrail: OutputGuardrailResponse,
) -> ChatRespondResponse | None:
    content = invoke_chat_model(
        build_rewrite_prompt(
            task="rewrite_chat_response",
            output_schema=build_chat_output_schema(),
            current_response=candidate.model_dump(),
            required_fixes=guardrail.required_fixes,
            safe_message=guardrail.safe_message,
            source_context={
                "report_context": payload.report_context.model_dump(),
                "message": payload.message.model_dump(),
                "recent_messages": [
                    message.model_dump() for message in payload.recent_messages
                ],
            },
        )
    )
    return parse_chat_response(content)


def parse_report_response(content: str | None) -> ReportGenerateResponse | None:
    if not content:
        return None

    try:
        data = extract_json_object(content)
        return ReportGenerateResponse.model_validate(data)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def parse_chat_response(content: str | None) -> ChatRespondResponse | None:
    if not content:
        return None

    try:
        data = extract_json_object(content)
        return ChatRespondResponse.model_validate(data)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def with_report_guardrail(
    response: ReportGenerateResponse,
    guardrail: OutputGuardrailResponse,
) -> ReportGenerateResponse:
    response.guardrail_result = GuardrailResult(
        is_allowed=guardrail.is_allowed,
        risk_level=guardrail.risk_level,
    )
    return response


def with_chat_guardrail(
    response: ChatRespondResponse,
    guardrail: OutputGuardrailResponse,
) -> ChatRespondResponse:
    response.guardrail_result = GuardrailResult(
        is_allowed=guardrail.is_allowed,
        risk_level=guardrail.risk_level,
    )
    return response


def build_blocked_report_response(
    payload: ReportGenerateRequest,
    fallback_response: ReportGenerateResponse,
    guardrail: OutputGuardrailResponse,
) -> ReportGenerateResponse:
    blocked = fallback_response.model_copy(deep=True)
    blocked.status = "blocked"
    blocked.title = "안전 기준으로 차단된 리포트"
    blocked.recommended_ingredients = []
    blocked.lifestyle_tips = []
    blocked.disclaimer = guardrail.safe_message or DEFAULT_SAFE_MESSAGE
    blocked.citations = []
    blocked.guardrail_result = GuardrailResult(
        is_allowed=False, risk_level=guardrail.risk_level
    )
    blocked.input_summary.age = payload.normalized_input.age
    blocked.input_summary.gender = payload.normalized_input.gender
    return blocked


def build_blocked_chat_response(
    guardrail: OutputGuardrailResponse,
) -> ChatRespondResponse:
    return ChatRespondResponse(
        content=guardrail.safe_message or DEFAULT_SAFE_MESSAGE,
        citations=[],
        guardrail_result=GuardrailResult(
            is_allowed=False, risk_level=guardrail.risk_level
        ),
    )


def filter_report_citations(
    response: ReportGenerateResponse,
    payload: ReportGenerateRequest,
):
    context_by_id = {context.document_id: context for context in payload.rag_contexts}
    allowed = filter_valid_citations(response.citations, set(context_by_id))
    return dedupe_report_citation_sources(allowed, context_by_id)


def filter_chat_citations(
    response: ChatRespondResponse,
    payload: ChatRespondRequest,
):
    allowed_ids = {
        citation.document_id
        for citation in payload.report_context.citations
        if citation.document_id
    }
    allowed_ids.update({
        f"functional_ingredient_{ingredient.normalized_name}"
        for ingredient in payload.report_context.recommended_ingredients
        if ingredient.normalized_name
    })
    return filter_valid_citations(response.citations, allowed_ids)


def dedupe_report_citation_sources(
    citations: list[Citation],
    context_by_id: dict,
) -> list[Citation]:
    deduped = []
    seen_sources = set()
    for citation in citations:
        context = context_by_id.get(citation.document_id)
        source_name = report_source_name(
            context.source_type if context else citation.source_type,
            context.source_name if context else citation.source_name,
        )
        if not source_name or source_name in seen_sources:
            continue
        seen_sources.add(source_name)
        deduped.append(
            Citation(
                source_type=context.source_type if context else citation.source_type,
                source_name=source_name,
                document_id=citation.document_id,
            )
        )
    return deduped


def report_source_name(source_type: str, source_name: str | None) -> str | None:
    if source_type == "idisk":
        return "iDISK"
    if source_type == "functional_ingredient":
        return "건강기능식품 기능성원료 인정현황"
    if source_name in {"iDISK", "건강기능식품 기능성원료 인정현황"}:
        return source_name
    return None


def serialize_report_content(response: ReportGenerateResponse) -> str:
    parts = [
        response.title,
        response.disclaimer,
        *response.lifestyle_tips,
    ]

    for ingredient in response.recommended_ingredients:
        parts.extend(
            [
                ingredient.name_ko,
                ingredient.name_en,
                ingredient.reason,
                *ingredient.expected_effects,
                ingredient.recommended_dosage,
                *ingredient.side_effects,
                *ingredient.precautions,
            ]
        )

    return "\n".join(part for part in parts if part)


def is_llm_enabled() -> bool:
    return (
        settings.ai_generation_provider == "openai"
        and bool(settings.openai_api_key)
        and bool(settings.openai_base_url)
        and bool(settings.ai_model_name)
    )


def invoke_chat_model(prompt: str) -> str | None:
    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )

    try:
        if settings.ai_model_name.startswith("gpt-5"):
            messages = [
                {
                    "role": "user",
                    "content": f"{SYSTEM_PROMPT}\n\n{prompt}",
                }
            ]
        else:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]

        request_kwargs = {
            "model": settings.ai_model_name,
            "messages": messages,
            "max_completion_tokens": settings.ai_max_tokens,
        }

        if settings.ai_model_name.startswith("gpt-5"):
            request_kwargs["reasoning_effort"] = "minimal"
        else:
            request_kwargs["temperature"] = settings.ai_temperature

        response = client.chat.completions.create(**request_kwargs)
    except Exception:
        return None

    if not response.choices:
        return None

    return response.choices[0].message.content


def build_report_prompt(
    payload: ReportGenerateRequest,
    fallback_response: ReportGenerateResponse,
) -> str:
    return json.dumps(
        {
            "task": "generate_ingredient_report",
            "output_schema": build_report_output_schema(),
            "normalized_input": payload.normalized_input.model_dump(),
            "rag_contexts": [context.model_dump() for context in payload.rag_contexts],
            "fallback_response": fallback_response.model_dump(),
            "rules": [
                "Use Korean for user-facing text.",
                "Recommend ingredients only, not products.",
                "Do not invent citations.",
                "Use document_id values from rag_contexts only.",
                "Do not invent iHerb URLs or categories; leave iherb fields null.",
                "Keep medical safety language cautious.",
            ],
        },
        ensure_ascii=False,
    )


def build_chat_prompt(
    payload: ChatRespondRequest,
    fallback_response: ChatRespondResponse,
) -> str:
    return json.dumps(
        {
            "task": "answer_report_follow_up_question",
            "output_schema": build_chat_output_schema(),
            "report_context": payload.report_context.model_dump(),
            "message": payload.message.model_dump(),
            "recent_messages": [
                message.model_dump() for message in payload.recent_messages
            ],
            "fallback_response": fallback_response.model_dump(),
            "rules": [
                "Use Korean for user-facing text.",
                "Answer only within the report context.",
                "Do not provide diagnosis, prescription, treatment instructions, or medication changes.",
                "Do not persuade the user to buy a product.",
                "Use a safe expert-consultation disclaimer when health risk is possible.",
            ],
        },
        ensure_ascii=False,
    )


def build_rewrite_prompt(
    task: str,
    output_schema: dict,
    current_response: dict,
    required_fixes: list[str],
    safe_message: str | None,
    source_context: dict,
) -> str:
    return json.dumps(
        {
            "task": task,
            "output_schema": output_schema,
            "current_response": current_response,
            "required_fixes": required_fixes,
            "safe_message": safe_message,
            "source_context": source_context,
            "rules": [
                "Return only valid JSON matching output_schema.",
                "Apply every required_fix.",
                "Keep allowed citations only.",
                "Do not add diagnosis, prescription, medication changes, treatment claims, or purchase persuasion.",
                "If safe rewriting is impossible, use safe_message as the main user-facing text.",
            ],
        },
        ensure_ascii=False,
    )


def build_report_output_schema() -> dict:
    return {
        "status": "completed",
        "title": "string",
        "input_summary": {
            "age": "integer",
            "gender": "string",
            "health_goals": ["string"],
            "medications": ["string"],
            "special_conditions": ["string"],
            "additional_notes": "string or null",
        },
        "recommended_ingredients": [
            {
                "name_ko": "string",
                "name_en": "string",
                "normalized_name": "string",
                "reason": "string",
                "recommendation_score": "integer from 0 to 100; suitability score, not efficacy probability",
                "score_label": "높음, 보통, 주의 필요, or 낮음",
                "score_reasons": ["string"],
                "caution_level": "low, medium, or high",
                "expected_effects": ["string"],
                "recommended_dosage": "string",
                "side_effects": ["string"],
                "precautions": ["string"],
                "iherb_url": "string or null",
                "iherb_category_name": "string or null",
            }
        ],
        "lifestyle_tips": ["string"],
        "disclaimer": "string",
        "citations": [
            {
                "source_type": "string",
                "source_name": "string or null",
                "document_id": "string",
            }
        ],
        "guardrail_result": {
            "is_allowed": True,
            "risk_level": "low",
        },
    }


def build_chat_output_schema() -> dict:
    return {
        "content": "string",
        "citations": [
            {
                "source_type": "string",
                "source_name": "string or null",
                "document_id": "string",
            }
        ],
        "guardrail_result": {
            "is_allowed": True,
            "risk_level": "low",
        },
    }


def extract_json_object(content: str):
    text = content.strip()

    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.startswith("json"):
            text = text[4:].strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object found.")

    return json.loads(text[start : end + 1])
