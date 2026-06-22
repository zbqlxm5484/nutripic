# AI Server API Specification

이 문서는 Django 백엔드가 내부적으로 호출하는 AI/RAG 서버 API 명세이다.

AI 서버는 외부 프론트엔드에 직접 노출하지 않는다. 인증, 사용자 권한, 데이터 저장, 사용량 제한의 최종 판정은 Django 백엔드가 담당한다.

## 1. Common Rules

### Base URL

```text
/internal/ai/v1/
```

### Naming

- Path segment, query parameter, request field, response field는 `snake_case`를 사용한다.
- 날짜와 시간은 ISO 8601 문자열을 사용한다.

### Server-To-Server Authentication

```http
X-Internal-Api-Key: {internal_api_key}
X-Request-Id: {request_id}
```

### Standard Error Response

```json
{
  "error_code": "rag_search_failed",
  "message": "RAG 검색 중 오류가 발생했습니다.",
  "details": {
    "request_id": "req_20260622_0001"
  }
}
```

### Common Error Codes

| HTTP Status | error_code | Description |
| --- | --- | --- |
| 400 | `validation_error` | 요청 형식 또는 값 오류 |
| 401 | `internal_authentication_failed` | 서버 간 인증 실패 |
| 429 | `ai_rate_limit_exceeded` | AI 서비스 제한 초과 |
| 500 | `ai_internal_server_error` | AI 서버 오류 |
| 503 | `rag_service_unavailable` | RAG 또는 벡터 DB 일시 불가 |

## 2. POST `/internal/ai/v1/guardrails/input/`

사용자 입력에 대한 AI 가드레일 검사.

Request:

```json
{
  "request_id": "req_20260622_0001",
  "user_id": 1,
  "task_type": "report_generation",
  "input_text": "카페인을 먹으면 심장이 두근거립니다.",
  "structured_input": {
    "health_goals": ["fatigue", "sleep"],
    "medications": ["anticoagulant"],
    "special_conditions": ["allergy"]
  }
}
```

Response `200`:

```json
{
  "is_allowed": true,
  "risk_level": "low",
  "blocked_reason": null,
  "safe_message": null,
  "needs_clarification": false,
  "questions": []
}
```

Blocked Response `200`:

```json
{
  "is_allowed": false,
  "risk_level": "high",
  "blocked_reason": "medical_high_risk",
  "safe_message": "의학적 진단, 처방, 약물 변경은 제공할 수 없습니다. 전문가와 상담하세요.",
  "needs_clarification": false,
  "questions": []
}
```

## 3. POST `/internal/ai/v1/normalize/`

한국어 사용자 입력을 내부 표준명과 영어 검색 질의로 정규화한다.

Request:

```json
{
  "request_id": "req_20260622_0001",
  "age": 30,
  "gender": "female",
  "health_goals": [
    {
      "code": "fatigue",
      "name": "피로",
      "priority": 1
    }
  ],
  "medications": [
    {
      "code": "anticoagulant",
      "name": "항응고제"
    }
  ],
  "special_conditions": [
    {
      "code": "allergy",
      "name": "알레르기"
    }
  ],
  "additional_notes": "카페인을 먹으면 심장이 두근거립니다."
}
```

Response `200`:

```json
{
  "normalized_input": {
    "health_goals": [
      {
        "code": "fatigue",
        "name_ko": "피로",
        "name_en": "fatigue",
        "priority": 1,
        "confidence": 0.98
      }
    ],
    "medications": [
      {
        "code": "anticoagulant",
        "name_ko": "항응고제",
        "name_en": "anticoagulant",
        "confidence": 0.95
      }
    ],
    "special_conditions": [
      {
        "code": "allergy",
        "name_ko": "알레르기",
        "name_en": "allergy",
        "confidence": 0.96
      }
    ],
    "additional_terms": [
      {
        "text_ko": "심장 두근거림",
        "text_en": "palpitations",
        "confidence": 0.88
      }
    ]
  },
  "search_queries": [
    "fatigue sleep supplements",
    "palpitations caffeine precautions",
    "anticoagulant supplement precautions"
  ],
  "needs_clarification": false,
  "questions": []
}
```

## 4. POST `/internal/ai/v1/rag/search/`

iDISK와 건강기능식품 기능성원료 인정현황 데이터를 RAG 검색한다.

Request:

```json
{
  "request_id": "req_20260622_0001",
  "search_queries": [
    "fatigue sleep supplements",
    "anticoagulant supplement precautions"
  ],
  "filters": {
    "source_types": ["idisk", "functional_ingredient"],
    "top_k": 8
  }
}
```

Response `200`:

```json
{
  "results": [
    {
      "document_id": "functional_ingredient_magnesium",
      "source_type": "functional_ingredient",
      "source_name": "건강기능식품 기능성원료 인정현황",
      "title": "마그네슘",
      "content": "기능성, 일일섭취량, 섭취 시 주의사항 요약",
      "score": 0.91,
      "metadata": {
        "ingredient_name_ko": "마그네슘",
        "ingredient_name_en": "Magnesium",
        "daily_dosage": "데이터 기준 용량",
        "precautions": ["신장 질환자는 전문가 상담 필요"]
      }
    }
  ]
}
```

## 5. POST `/internal/ai/v1/reports/generate/`

RAG 검색 결과와 사용자 입력을 기반으로 추천 리포트를 생성한다.

Request:

```json
{
  "request_id": "req_20260622_0001",
  "user_id": 1,
  "normalized_input": {
    "age": 30,
    "gender": "female",
    "health_goals": [
      {
        "code": "fatigue",
        "name_ko": "피로",
        "name_en": "fatigue",
        "priority": 1
      }
    ],
    "medications": [
      {
        "code": "anticoagulant",
        "name_ko": "항응고제",
        "name_en": "anticoagulant"
      }
    ],
    "special_conditions": [
      {
        "code": "allergy",
        "name_ko": "알레르기",
        "name_en": "allergy"
      }
    ],
    "additional_notes": "카페인을 먹으면 심장이 두근거립니다."
  },
  "rag_contexts": [
    {
      "document_id": "functional_ingredient_magnesium",
      "source_type": "functional_ingredient",
      "title": "마그네슘",
      "content": "기능성, 일일섭취량, 섭취 시 주의사항 요약",
      "metadata": {
        "ingredient_name_ko": "마그네슘",
        "ingredient_name_en": "Magnesium"
      }
    }
  ]
}
```

Response `200`:

```json
{
  "status": "completed",
  "title": "피로 개선을 위한 성분 리포트",
  "input_summary": {
    "age": 30,
    "gender": "female",
    "health_goals": ["피로"],
    "medications": ["항응고제"],
    "special_conditions": ["알레르기"],
    "additional_notes": "카페인을 먹으면 심장이 두근거립니다."
  },
  "recommended_ingredients": [
    {
      "name_ko": "마그네슘",
      "name_en": "Magnesium",
      "normalized_name": "magnesium",
      "reason": "피로와 수면 관리에 관련된 근거가 검색되어 후보로 선정되었습니다.",
      "expected_effects": ["정상적인 근육 기능 유지"],
      "recommended_dosage": "기능성원료 인정현황의 일일섭취량 범위를 따르세요.",
      "side_effects": ["설사", "복부 불편감"],
      "precautions": ["신장 질환이 있는 경우 전문가와 상담하세요."]
    }
  ],
  "lifestyle_tips": [
    "수면 시간을 일정하게 유지하세요."
  ],
  "disclaimer": "질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.",
  "citations": [
    {
      "source_type": "functional_ingredient",
      "source_name": "건강기능식품 기능성원료 인정현황",
      "document_id": "functional_ingredient_magnesium"
    }
  ],
  "guardrail_result": {
    "is_allowed": true,
    "risk_level": "low"
  }
}
```

## 6. POST `/internal/ai/v1/chat/respond/`

저장된 리포트와 후속 질문을 기반으로 채팅 답변을 생성한다.

Request:

```json
{
  "request_id": "req_20260622_0002",
  "user_id": 1,
  "report_id": 10,
  "report_context": {
    "title": "피로 개선을 위한 성분 리포트",
    "recommended_ingredients": [
      {
        "name_ko": "마그네슘",
        "name_en": "Magnesium",
        "normalized_name": "magnesium",
        "precautions": ["신장 질환이 있는 경우 전문가와 상담하세요."]
      }
    ],
    "disclaimer": "질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요."
  },
  "message": {
    "content": "마그네슘은 언제 먹는 게 좋나요?"
  },
  "recent_messages": [
    {
      "role": "user",
      "content": "마그네슘은 언제 먹는 게 좋나요?"
    }
  ]
}
```

Response `200`:

```json
{
  "content": "일반적으로 마그네슘은 식후 섭취를 고려할 수 있습니다. 다만 개인의 질환, 복용 약, 제품 형태에 따라 달라질 수 있으므로 질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.",
  "citations": [
    {
      "source_type": "functional_ingredient",
      "source_name": "건강기능식품 기능성원료 인정현황",
      "document_id": "functional_ingredient_magnesium"
    }
  ],
  "guardrail_result": {
    "is_allowed": true,
    "risk_level": "low"
  }
}
```

## 7. POST `/internal/ai/v1/guardrails/output/`

AI가 생성한 리포트 또는 채팅 답변의 응답 가드레일을 검증한다.

Request:

```json
{
  "request_id": "req_20260622_0002",
  "task_type": "chat_response",
  "content": "일반적으로 마그네슘은 식후 섭취를 고려할 수 있습니다.",
  "citations": [
    {
      "source_type": "functional_ingredient",
      "document_id": "functional_ingredient_magnesium"
    }
  ]
}
```

Response `200`:

```json
{
  "is_allowed": true,
  "risk_level": "low",
  "blocked_reason": null,
  "safe_message": null,
  "required_fixes": []
}
```

## 8. AI Server Responsibilities

| Concern | AI Server Responsibility |
| --- | --- |
| 입력 가드레일 | 부적절 입력, 프롬프트 인젝션, 고위험 의료 요청 탐지 |
| 한국어-영어 정규화 | 건강 목표, 약물, 특이사항, 자유 입력을 검색용 표준명으로 변환 |
| RAG 검색 | iDISK와 기능성원료 인정현황 검색 |
| 리포트 생성 | RAG 근거 기반 성분 중심 리포트 작성 |
| 채팅 답변 생성 | 저장된 리포트와 근거 기반 후속 답변 작성 |
| 출력 가드레일 | 진단, 처방, 약물 변경 지시, 과도한 확신, 제품 구매 유도 검증 |

## 9. Non-Responsibilities

AI 서버는 다음을 담당하지 않는다.

- JWT 인증
- 사용자 권한 검증
- 회원, 리포트, 채팅, 커뮤니티 데이터 영구 저장
- 사용자별 사용량 제한 최종 판정
- iHerb 링크 매핑
- 커뮤니티 기능
- 관리자 기능

## 10. Open Decisions

- RAG 문서 메타데이터 스키마
- iDISK 인덱싱 단위와 `document_id` 규칙
- 기능성원료 인정현황 데이터의 용량/주의사항 구조화 방식
- 정규화 confidence 임계값
- 추가 확인 질문 생성 조건
- 모델명, temperature, max token 등 생성 파라미터
- 가드레일 차단 사유 코드 목록
