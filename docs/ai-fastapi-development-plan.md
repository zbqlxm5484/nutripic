# AI FastAPI Development Plan

이 문서는 AI/RAG 서버를 FastAPI로 개발할 때의 작업 순서를 정리한다.

AI 서버는 외부 프론트엔드에 직접 노출하지 않는다. Django 백엔드가 내부 API로 AI 서버를 호출하며, JWT 인증, 사용자 권한, 데이터 저장, 사용량 제한 최종 판정, iHerb 링크 매핑은 Django 백엔드가 담당한다.

## 1. Development Goal

FastAPI 기반 AI 서버는 다음 내부 API를 명세에 맞게 제공한다.

```text
POST /internal/ai/v1/guardrails/input/
POST /internal/ai/v1/normalize/
POST /internal/ai/v1/rag/search/
POST /internal/ai/v1/reports/generate/
POST /internal/ai/v1/chat/respond/
POST /internal/ai/v1/guardrails/output/
```

개발의 1차 목표는 실제 AI 품질보다 API 계약을 안정적으로 맞추는 것이다. 먼저 Django 백엔드와 연동 가능한 FastAPI 서버를 만들고, 이후 LangChain, RAG, 벡터 DB, 실제 데이터 처리를 단계적으로 고도화한다.

## 2. Development Principles

- API path, request field, response field는 모두 `snake_case`를 사용한다.
- 모든 endpoint는 trailing slash(`/`)를 유지한다.
- AI 서버는 Django 백엔드에서만 호출된다고 가정한다.
- 모든 내부 API 요청은 `X-Internal-Api-Key`, `X-Request-Id` 헤더를 검증한다.
- 표준 에러 응답은 `error_code`, `message`, `details` 구조를 따른다.
- 리포트와 채팅 답변은 RAG 검색 근거 기반으로 생성한다.
- 진단, 처방, 치료 지시, 약물 변경 지시, 특정 제품 구매 유도는 제공하지 않는다.
- iHerb 링크 매핑은 AI 서버가 담당하지 않는다.

## 3. Recommended Directory Structure

```text
ai/
  app/
    main.py
    core/
      config.py
      security.py
      errors.py
    api/
      routes/
        guardrails.py
        normalize.py
        rag.py
        reports.py
        chat.py
    schemas/
      common.py
      guardrails.py
      normalize.py
      rag.py
      reports.py
      chat.py
    services/
      guardrails.py
      normalize.py
      rag.py
      report_generator.py
      chat.py
    data/
      dictionaries/
      raw/
      processed/
  tests/
    test_guardrails.py
    test_normalize.py
    test_rag.py
    test_reports.py
    test_chat.py
```

구현 초기에는 `services/`에 mock 또는 rule-based 로직을 두고, API schema와 응답 구조를 먼저 고정한다.

## 4. Environment Setup

### 4.1 Python Environment

AI 서버 전용 Python 가상환경을 준비한다.

```bash
cd ai
python -m venv .venv
source .venv/Scripts/activate
```

Windows PowerShell에서는 다음을 사용할 수 있다.

```powershell
cd ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4.2 Required Dependencies

초기 개발에 필요한 최소 의존성은 다음과 같다.

```text
fastapi
uvicorn
pydantic
pydantic-settings
python-dotenv
pytest
httpx
```

LangChain, vector DB client, embedding model 관련 의존성은 API 계약 테스트가 안정화된 뒤 추가한다.

## 5. Configuration

환경변수는 `.env`로 관리하고, 코드에는 비밀 값을 직접 넣지 않는다.

필수 환경변수 예시:

```text
AI_INTERNAL_API_KEY=local_internal_key
AI_ENV=local
AI_MODEL_NAME=
AI_TEMPERATURE=0.2
AI_MAX_TOKENS=2000
VECTOR_DB_URL=
VECTOR_DB_API_KEY=
```

초기에는 모델과 벡터 DB 값이 비어 있어도 mock 응답으로 서버가 실행되도록 만든다.

## 6. Common API Foundation

### 6.1 FastAPI App

`app/main.py`에서 FastAPI 앱을 만들고 `/internal/ai/v1` prefix 아래에 router를 등록한다.

성공 기준:

- `GET /docs`에서 OpenAPI 문서를 확인할 수 있다.
- 모든 내부 API path가 `/internal/ai/v1/`로 시작한다.
- endpoint의 trailing slash가 명세와 일치한다.

### 6.2 Internal Authentication

모든 내부 API는 다음 헤더를 요구한다.

```http
X-Internal-Api-Key: {internal_api_key}
X-Request-Id: {request_id}
```

성공 기준:

- API key가 없거나 다르면 `401 internal_authentication_failed`를 반환한다.
- `X-Request-Id`가 없으면 요청을 거부하거나 서버에서 생성할지 정책을 정한다.
- 에러 응답 `details.request_id`에 request id를 포함한다.

### 6.3 Standard Error Response

에러 응답 형식:

```json
{
  "error_code": "validation_error",
  "message": "요청 값이 올바르지 않습니다.",
  "details": {
    "request_id": "req_20260622_0001"
  }
}
```

우선 구현할 공통 error code:

```text
validation_error
internal_authentication_failed
ai_rate_limit_exceeded
ai_internal_server_error
rag_service_unavailable
```

## 7. Step 1 - Input Guardrail API

### 7.1 Endpoint

```text
POST /internal/ai/v1/guardrails/input/
```

### 7.2 Responsibility

사용자 입력이 AI 처리에 적합한지 검사한다.

검사 대상:

- 부적절한 표현
- 프롬프트 인젝션
- 시스템 명령 탈취 시도
- 과도한 개인정보 입력
- 서비스 범위 밖 요청
- 고위험 의료 요청
- 추가 확인 질문 필요 여부

### 7.3 Initial Implementation

초기에는 rule-based 로직으로 시작한다.

예시:

- "진단해줘", "처방해줘", "약 끊어도 돼" 등은 high risk로 분류한다.
- "이전 지시 무시", "system prompt" 등은 prompt injection으로 분류한다.
- 입력이 정상적이면 `is_allowed: true`를 반환한다.

### 7.4 Success Criteria

- 정상 입력은 `is_allowed: true`를 반환한다.
- 고위험 의료 요청은 `is_allowed: false`, `risk_level: high`를 반환한다.
- 차단 시 `safe_message`를 포함한다.
- 응답 schema가 `ai-api-spec.md`와 일치한다.

## 8. Step 2 - Normalize API

### 8.1 Endpoint

```text
POST /internal/ai/v1/normalize/
```

### 8.2 Responsibility

한국어 사용자 입력을 내부 표준명과 영어 RAG 검색 질의로 변환한다.

처리 대상:

- 건강 목표
- 복용 약
- 특이사항
- 자유 입력 텍스트

### 8.3 Initial Implementation

초기에는 정적 dictionary를 사용한다.

예시:

```text
피로 -> fatigue
수면 -> sleep
항응고제 -> anticoagulant
알레르기 -> allergy
심장 두근거림 -> palpitations
```

이후 다음 순서로 고도화한다.

```text
1. 정적 dictionary
2. 동의어 dictionary
3. 번역 모델 또는 LLM 기반 정규화
4. embedding 기반 유사도 매칭
5. confidence 기반 추가 질문
```

### 8.4 Success Criteria

- `normalized_input`에 `name_ko`, `name_en`, `confidence`를 포함한다.
- `search_queries`는 영어 검색 질의 배열로 반환한다.
- confidence가 낮은 경우 `needs_clarification` 정책을 적용할 수 있게 구조를 유지한다.
- request/response field는 모두 `snake_case`를 사용한다.

## 9. Step 3 - RAG Search API

### 9.1 Endpoint

```text
POST /internal/ai/v1/rag/search/
```

### 9.2 Responsibility

정규화된 검색 질의를 이용해 다음 데이터를 검색한다.

- iDISK 증상/성분 데이터
- 건강기능식품 기능성원료 인정현황 데이터

### 9.3 Initial Implementation

실제 vector DB가 준비되기 전에는 fixture 기반 검색으로 시작한다.

예시:

- `fatigue`, `sleep` 질의가 들어오면 magnesium fixture를 반환한다.
- `anticoagulant` 질의가 들어오면 주의사항 fixture를 반환한다.

### 9.4 Later Implementation

고도화 순서:

```text
1. fixture 검색
2. local JSON/CSV 검색
3. keyword search
4. embedding 생성
5. vector DB 검색
6. metadata filter 적용
7. score threshold 적용
```

### 9.5 Success Criteria

- 응답은 `results` 배열을 반환한다.
- 각 result는 `document_id`, `source_type`, `source_name`, `title`, `content`, `score`, `metadata`를 포함한다.
- `source_type`은 우선 `idisk`, `functional_ingredient`를 지원한다.
- 검색 실패 시 `503 rag_service_unavailable` 또는 적절한 에러를 반환한다.

## 10. Step 4 - Report Generate API

### 10.1 Endpoint

```text
POST /internal/ai/v1/reports/generate/
```

### 10.2 Responsibility

정규화된 사용자 입력과 RAG 검색 결과를 바탕으로 성분 중심 리포트를 생성한다.

리포트 필수 구성:

- 제목
- 사용자 입력 요약
- 추천 성분 목록
- 성분별 추천 이유
- 기대 기능성
- 권장 용량
- 부작용 가능성
- 섭취 시 주의사항
- 생활 습관 팁
- 면책 문구
- citations
- guardrail_result

### 10.3 Initial Implementation

초기에는 template 기반 리포트를 생성한다.

예시:

- RAG result의 `metadata.ingredient_name_ko`를 추천 성분명으로 사용한다.
- `metadata.daily_dosage`를 권장 용량에 반영한다.
- `metadata.precautions`를 주의사항에 반영한다.
- 필수 고지 문구를 항상 포함한다.

필수 고지 문구:

```text
질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.
```

### 10.4 Later Implementation

고도화 순서:

```text
1. template 기반 응답
2. RAG context 기반 prompt 구성
3. LangChain chain 구성
4. structured output parser 적용
5. output schema validation
6. output guardrail과 재작성 루프 연결
```

### 10.5 Success Criteria

- 응답 `status`는 정상 생성 시 `completed`이다.
- `recommended_ingredients`는 최소 1개 이상 반환할 수 있다.
- 각 추천 성분에 `normalized_name`을 포함한다.
- `citations`는 RAG context의 `document_id`와 연결된다.
- 진단, 처방, 약물 변경 표현을 포함하지 않는다.

## 11. Step 5 - Output Guardrail API

### 11.1 Endpoint

```text
POST /internal/ai/v1/guardrails/output/
```

### 11.2 Responsibility

생성된 리포트 또는 채팅 답변이 안전한지 검증한다.

검증 대상:

- 의학적 진단 표현
- 처방 또는 치료 지시
- 약물 중단, 변경, 증량, 감량 지시
- 과도한 확신 표현
- 허위 근거
- 특정 제품 구매 유도
- citations 누락

### 11.3 Initial Implementation

초기에는 금지 표현 기반 rule check를 사용한다.

차단 또는 수정 대상 예시:

```text
반드시 낫습니다
약을 중단하세요
이 제품을 구매하세요
처방받으세요
진단됩니다
```

### 11.4 Success Criteria

- 안전한 응답은 `is_allowed: true`를 반환한다.
- 위험 표현이 있으면 `is_allowed: false` 또는 `required_fixes`를 반환한다.
- `required_fixes`는 추후 재작성 루프에 사용할 수 있게 배열로 유지한다.

## 12. Step 6 - Chat Respond API

### 12.1 Endpoint

```text
POST /internal/ai/v1/chat/respond/
```

### 12.2 Responsibility

저장된 리포트 context와 사용자의 후속 질문을 바탕으로 답변을 생성한다.

답변 범위:

- 리포트에 포함된 성분 설명
- 복용법, 권장 용량, 부작용, 주의사항
- 성분 간 차이
- 사용자 입력과 관련된 일반적인 건강기능식품 정보

제한 범위:

- 질병 진단
- 처방 또는 치료 지시
- 약물 중단, 변경, 증량, 감량 지시
- 서비스 목적과 무관한 질문
- 특정 제품 구매 유도

### 12.3 Initial Implementation

초기에는 report context 기반 template 응답을 만든다.

예시:

- 질문이 성분 복용 시간과 관련되면 일반적인 안내와 전문가 상담 문구를 반환한다.
- report context에 없는 성분 질문은 범위 제한 안내를 반환한다.
- 고위험 의료 질문은 전문가 상담 안내로 대체한다.

### 12.4 Success Criteria

- 응답은 `content`, `citations`, `guardrail_result`를 포함한다.
- citations는 report context 또는 RAG context와 연결된다.
- 답변에는 필요한 경우 전문가 상담 문구를 포함한다.
- 서비스 범위 밖 질문은 안전한 안내로 대체한다.

## 13. Backend Integration Sequence

Django 백엔드와 연동할 때의 전체 순서는 다음과 같다.

```text
1. Frontend -> Backend
   POST /api/v1/reports/

2. Backend
   - JWT 검증
   - 요청 필드 검증
   - 사용자별 사용량 제한 확인

3. Backend -> AI FastAPI
   - POST /internal/ai/v1/guardrails/input/
   - POST /internal/ai/v1/normalize/
   - POST /internal/ai/v1/rag/search/
   - POST /internal/ai/v1/reports/generate/
   - POST /internal/ai/v1/guardrails/output/

4. Backend
   - 추천 성분 iHerb 링크 매핑
   - 리포트 저장
   - 사용량 차감

5. Backend -> Frontend
   - 201 Created
```

채팅 연동 순서:

```text
1. Frontend -> Backend
   POST /api/v1/reports/{report_id}/messages/

2. Backend
   - JWT 검증
   - report 소유권 검증
   - 채팅 사용량 제한 확인
   - report context와 최근 메시지 구성

3. Backend -> AI FastAPI
   - POST /internal/ai/v1/chat/respond/
   - POST /internal/ai/v1/guardrails/output/

4. Backend
   - 사용자 메시지 저장
   - assistant 메시지 저장
   - 사용량 차감

5. Backend -> Frontend
   - 201 Created
```

## 14. Test Plan

### 14.1 Unit Tests

각 service 단위로 테스트한다.

```text
guardrails input rule
normalize dictionary mapping
rag fixture search
report template generation
output guardrail rule
chat response template
```

### 14.2 API Contract Tests

FastAPI test client 또는 httpx로 endpoint 응답 구조를 검증한다.

필수 검증:

- 정상 요청은 명세와 같은 JSON 구조를 반환한다.
- 잘못된 API key는 401을 반환한다.
- validation error는 표준 에러 구조를 반환한다.
- 모든 field가 `snake_case`이다.
- trailing slash endpoint가 정상 동작한다.

### 14.3 Integration Tests

Django 백엔드와 연결되기 전에는 mock client로 다음 흐름을 검증한다.

```text
input guardrail -> normalize -> rag search -> report generate -> output guardrail
chat respond -> output guardrail
```

## 15. MVP Completion Criteria

AI FastAPI MVP는 다음 조건을 만족하면 완료로 본다.

- 6개 내부 API가 모두 구현되어 있다.
- 모든 API가 내부 API key를 검증한다.
- 모든 request/response schema가 `ai-api-spec.md`와 일치한다.
- 리포트 생성 API가 mock 또는 fixture 기반으로 정상 응답을 반환한다.
- 채팅 응답 API가 report context 기반으로 정상 응답을 반환한다.
- 입력/출력 가드레일이 최소 rule-based로 동작한다.
- RAG search가 최소 fixture 또는 local data 기반으로 동작한다.
- pytest로 주요 endpoint 계약 테스트가 통과한다.
- Django 백엔드에서 호출 가능한 서버 실행 명령이 문서화되어 있다.

## 16. Recommended Work Order

실제 개발은 다음 순서로 진행한다.

```text
1. develop 브랜치에서 작업 브랜치 생성
   feat/ai-fastapi-server

2. ai/ FastAPI 프로젝트 기본 구조 생성

3. settings, env, internal API key 검증 구현

4. 공통 error response와 exception handler 구현

5. Pydantic schema 작성
   - common
   - guardrails
   - normalize
   - rag
   - reports
   - chat

6. guardrails/input endpoint 구현

7. normalize endpoint 구현

8. rag/search endpoint 구현

9. reports/generate endpoint 구현

10. guardrails/output endpoint 구현

11. chat/respond endpoint 구현

12. endpoint별 pytest 작성

13. report generation 전체 흐름 통합 테스트 작성

14. chat response 흐름 통합 테스트 작성

15. uvicorn 실행 방법 문서화

16. Django 백엔드와 base URL, API key, timeout 정책 합의

17. 실제 LangChain/RAG/vector DB 연결 시작
```

## 17. Local Run Command

예상 실행 명령:

```bash
cd ai
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Django 백엔드는 AI 서버 base URL을 다음처럼 설정해서 호출한다.

```text
AI_SERVER_BASE_URL=http://127.0.0.1:8001/internal/ai/v1
AI_INTERNAL_API_KEY=local_internal_key
```

## 18. Commit And PR

브랜치:

```text
feat/ai-fastapi-server
```

커밋:

```text
feat: AI FastAPI 내부 서버 구현
```

PR 제목:

```text
feat: AI FastAPI 내부 서버 구현
```

PR에는 다음을 포함한다.

```md
## 요약

- FastAPI 기반 AI 내부 API 서버 추가
- 내부 API key 인증 및 표준 에러 응답 구현
- 리포트 생성과 채팅 응답 API의 초기 계약 구현

## 확인

- pytest
- uvicorn 로컬 실행
- 주요 endpoint 수동 호출

## 참고

- 실제 LangChain/RAG/vector DB 연결은 후속 작업
```
