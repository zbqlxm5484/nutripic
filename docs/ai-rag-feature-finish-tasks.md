# AI/RAG 기능 완성 마감 작업 메모

목적: 현재 구현된 AI/RAG 흐름을 제품 기능으로 마감하기 위한 남은 작업만 정리한다. 데이터는 고정으로 보고, Chroma/LangChain 도입은 보류한다.

## 현재 상태

- iDISK, 기능성원료, supplement evidence 데이터는 RAG 문서와 벡터 인덱스로 생성되어 있다.
- 기본 RAG backend는 `local_json`이다.
- Backend 리포트 생성 흐름은 `guardrail -> normalize -> rag/search -> reports/generate -> output_guardrail`로 연결되어 있다.
- Normalizer는 `search_queries`와 `rag_query_bundle`를 만든다.
- 현재 RAG 검색은 `search_queries` 중심이고, `rag_query_bundle["idisk"]` 구조화 정보는 검색 점수에 아직 반영되지 않는다.

## 마감 방향

- LangChain은 도입하지 않는다.
- 데이터가 고정이므로 Chroma도 필수로 도입하지 않는다.
- `local_json` 검색 유지.
- 핵심 마감 작업은 normalizer가 만든 구조화 정보를 RAG 검색 boost/filter에 연결하는 것이다.

## 작업 1. RAG 요청 스키마 확장

대상:

- `ai/app/schemas/rag.py`

작업:

- `RagSearchRequest`에 `rag_query_bundle` 필드를 추가한다.
- 우선 `dict[str, Any]`로 받아도 된다.
- 시간이 있으면 `IdiskQueryBundle`, `RagQueryBundle` Pydantic 모델로 구조화한다.

완료 기준:

- 기존 `search_queries`만 들어오는 요청도 깨지지 않는다.
- `rag_query_bundle`가 없어도 기본값 `{}`로 처리된다.

## 작업 2. Backend에서 RAG bundle 전달

대상:

- `backend/reports/services.py`

작업:

- `client.rag_search` payload에 `normalize_response.get("rag_query_bundle", {})`를 포함한다.

완료 기준:

- 기존 리포트 생성 API 응답 형식은 유지된다.
- AI normalize 응답의 `rag_query_bundle`가 RAG search 요청까지 전달된다.

## 작업 3. local_json RAG 검색에 metadata boost 추가

대상:

- `ai/app/services/rag.py`
- `ai/app/services/rag_vector_store.py`

작업:

- `search_rag()`가 `payload.rag_query_bundle`를 `search_selected_backend()`로 넘긴다.
- `search_vector_index()`가 `query_bundle`를 받는다.
- iDISK 문서 metadata 기준 boost를 추가한다.

권장 boost:

- `metadata["dsi_id"] in ingredient_ids`: `+0.12`
- `metadata["disease_id"] in condition_ids`: `+0.12`
- `metadata["target_id"] in drug_ids`: `+0.12`
- relation target match: `+0.05`

주의:

- 처음부터 hard filter만 적용하지 않는다. 결과 0개 위험이 있다.
- source type filter는 기존 로직 유지.
- boost 후 score는 기존처럼 최대 `0.99`로 clamp한다.

완료 기준:

- `rag_query_bundle`가 있으면 관련 iDISK 문서가 상위로 올라온다.
- `rag_query_bundle`가 없어도 기존 텍스트 검색 동작이 유지된다.

## 작업 4. RAG 테스트 추가

대상:

- `ai/tests/test_rag_search.py`

테스트 케이스:

- bundle 없이 기존 검색이 동작한다.
- `condition_ids`가 있으면 iDISK disease 문서가 boost된다.
- `drug_ids`가 있으면 iDISK interaction 문서가 boost된다.
- `ingredient_ids`가 있으면 해당 DSI 문서가 boost된다.
- source type filter와 top_k가 기존처럼 유지된다.

완료 기준:

- RAG 관련 테스트 통과.
- 기존 API contract 테스트 깨지지 않음.

## 작업 5. 배포용 AI 서버 점검

대상:

- `ai/app/main.py`
- Render AI service 설정

작업:

- 가능하면 `/health` endpoint 추가.
- Render는 `Root Directory: ai`로 배포한다.
- Start command는 `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- `AI_INTERNAL_API_KEY`를 Render와 backend에 같은 값으로 설정한다.
- `RAG_VECTOR_BACKEND=local_json` 사용.

완료 기준:

- 배포된 AI 서버에서 `/internal/ai/v1/rag/search/` 호출 성공.
- backend env의 `AI_SERVER_BASE_URL`이 배포된 AI URL을 가리킨다.

## 작업 6. E2E 확인

흐름:

1. Frontend에서 설문 제출.
2. Backend report 생성 API 호출.
3. Backend가 AI normalize 호출.
4. Backend가 AI rag/search 호출.
5. Backend가 AI reports/generate 호출.
6. Frontend에서 리포트 결과 표시.

확인 항목:

- 리포트 생성 성공.
- RAG citations가 포함된다.
- iDISK 또는 기능성원료 문서가 `rag_contexts`에 들어간다.
- AI 서버 장애 시 backend가 503 또는 안전한 에러를 반환한다.
- 빈 검색 결과에서도 fallback report가 깨지지 않는다.

## 우선순위

1. `rag_query_bundle` 전달.
2. local_json metadata boost.
3. RAG 테스트.
4. AI Render 배포.
5. Backend/Frontend E2E 검증.

## 보류

- LangChain 도입.
- Chroma 전환.
- 외부 vector DB.
- 데이터 자동 갱신 pipeline.
- 복잡한 reranker.

