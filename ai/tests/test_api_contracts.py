import os

os.environ.setdefault("AI_INTERNAL_API_KEY", "test_internal_key")

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
HEADERS = {
    "X-Internal-Api-Key": "test_internal_key",
    "X-Request-Id": "req_test_0001",
}


def test_input_guardrail_allows_normal_request():
    response = client.post(
        "/internal/ai/v1/guardrails/input/",
        headers=HEADERS,
        json={
            "request_id": "req_test_0001",
            "user_id": 1,
            "task_type": "report_generation",
            "input_text": "피로하고 잠을 잘 못 잡니다.",
            "structured_input": {
                "health_goals": ["fatigue", "sleep"],
                "medications": [],
                "special_conditions": [],
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["is_allowed"] is True
    assert body["risk_level"] == "low"
    assert body["blocked_reason"] is None
    assert body["needs_clarification"] is False
    assert body["questions"] == []


def test_input_guardrail_blocks_high_risk_request():
    response = client.post(
        "/internal/ai/v1/guardrails/input/",
        headers=HEADERS,
        json={
            "request_id": "req_test_0001",
            "user_id": 1,
            "task_type": "report_generation",
            "input_text": "약 끊어도 되는지 진단해줘",
            "structured_input": {},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["is_allowed"] is False
    assert body["risk_level"] == "high"
    assert body["blocked_reason"] == "medical_high_risk"
    assert body["safe_message"]


def test_normalize_returns_normalized_input_and_search_queries():
    response = client.post(
        "/internal/ai/v1/normalize/",
        headers=HEADERS,
        json={
            "request_id": "req_test_0001",
            "age": 30,
            "gender": "female",
            "health_goals": [
                {"code": "fatigue", "name": "피로", "priority": 1},
                {"code": "sleep", "name": "수면", "priority": 2},
            ],
            "medications": [{"code": "anticoagulant", "name": "항응고제"}],
            "special_conditions": [{"code": "allergy", "name": "알레르기"}],
            "additional_notes": "카페인을 먹으면 심장이 두근거립니다.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["needs_clarification"] is False
    assert body["normalized_input"]["health_goals"][0]["name_en"] == "fatigue"
    assert body["normalized_input"]["medications"][0]["name_en"] == "anticoagulant"
    assert body["normalized_input"]["special_conditions"][0]["name_en"] == "allergy"
    assert "fatigue sleep supplements" in body["search_queries"]
    assert "anticoagulant supplement precautions" in body["search_queries"]


def test_rag_search_returns_results():
    response = client.post(
        "/internal/ai/v1/rag/search/",
        headers=HEADERS,
        json={
            "request_id": "req_test_0001",
            "search_queries": [
                "fatigue sleep supplements",
                "anticoagulant supplement precautions",
            ],
            "filters": {
                "source_types": ["idisk", "functional_ingredient"],
                "top_k": 8,
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) >= 1
    result = body["results"][0]
    assert result["document_id"]
    assert result["source_type"] in ["idisk", "functional_ingredient"]
    assert "metadata" in result


def test_report_generate_returns_completed_report():
    response = client.post(
        "/internal/ai/v1/reports/generate/",
        headers=HEADERS,
        json={
            "request_id": "req_test_0001",
            "user_id": 1,
            "normalized_input": {
                "age": 30,
                "gender": "female",
                "health_goals": [
                    {
                        "code": "fatigue",
                        "name_ko": "피로",
                        "name_en": "fatigue",
                        "priority": 1,
                        "confidence": 0.98,
                    }
                ],
                "medications": [
                    {
                        "code": "anticoagulant",
                        "name_ko": "항응고제",
                        "name_en": "anticoagulant",
                        "confidence": 0.95,
                    }
                ],
                "special_conditions": [],
                "additional_notes": "카페인을 먹으면 심장이 두근거립니다.",
                "additional_terms": [],
            },
            "rag_contexts": [
                {
                    "document_id": "functional_ingredient_magnesium",
                    "source_type": "functional_ingredient",
                    "source_name": "건강기능식품 기능성원료 인정현황",
                    "title": "마그네슘",
                    "content": "기능성, 일일섭취량, 섭취 시 주의사항 요약",
                    "metadata": {
                        "ingredient_name_ko": "마그네슘",
                        "ingredient_name_en": "Magnesium",
                        "normalized_name": "magnesium",
                        "daily_dosage": "기능성원료 인정현황의 일일섭취량 범위를 따르세요.",
                        "expected_effects": ["정상적인 근육 기능 유지"],
                        "side_effects": ["설사", "복부 불편감"],
                        "precautions": ["신장 질환이 있는 경우 전문가와 상담하세요."],
                    },
                }
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["title"]
    assert body["input_summary"]["health_goals"] == ["피로"]
    assert body["recommended_ingredients"][0]["normalized_name"] == "magnesium"
    assert body["disclaimer"] == "질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요."
    assert body["citations"][0]["document_id"] == "functional_ingredient_magnesium"
    assert body["guardrail_result"]["is_allowed"] is True


def test_output_guardrail_allows_safe_content():
    response = client.post(
        "/internal/ai/v1/guardrails/output/",
        headers=HEADERS,
        json={
            "request_id": "req_test_0001",
            "task_type": "report_generation",
            "content": "질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.",
            "citations": [
                {
                    "source_type": "functional_ingredient",
                    "source_name": "건강기능식품 기능성원료 인정현황",
                    "document_id": "functional_ingredient_magnesium",
                }
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["is_allowed"] is True
    assert body["risk_level"] == "low"
    assert body["required_fixes"] == []


def test_chat_respond_returns_answer_based_on_report_context():
    response = client.post(
        "/internal/ai/v1/chat/respond/",
        headers=HEADERS,
        json={
            "request_id": "req_test_0001",
            "user_id": 1,
            "report_id": 10,
            "report_context": {
                "title": "피로 개선을 위한 성분 리포트",
                "recommended_ingredients": [
                    {
                        "name_ko": "마그네슘",
                        "name_en": "Magnesium",
                        "normalized_name": "magnesium",
                        "precautions": ["신장 질환이 있는 경우 전문가와 상담하세요."],
                    }
                ],
                "disclaimer": "질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.",
            },
            "message": {"content": "마그네슘은 언제 먹는 게 좋나요?"},
            "recent_messages": [
                {"role": "user", "content": "마그네슘은 언제 먹는 게 좋나요?"}
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "마그네슘" in body["content"]
    assert body["citations"][0]["document_id"] == "functional_ingredient_magnesium"
    assert body["guardrail_result"]["is_allowed"] is True


def test_internal_api_key_is_required():
    response = client.post(
        "/internal/ai/v1/rag/search/",
        json={
            "request_id": "req_test_0001",
            "search_queries": ["fatigue sleep supplements"],
            "filters": {"top_k": 1},
        },
    )

    assert response.status_code == 401
    body = response.json()
    assert body == {
        "error_code": "internal_authentication_failed",
        "message": "서버 간 인증에 실패했습니다.",
        "details": {"request_id": None},
    }
