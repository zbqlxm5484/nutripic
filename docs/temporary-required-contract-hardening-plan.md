# 필수 계약 보강 계획

## 진행 상황
- [x] 백엔드 일일 리포트 생성 quota 설정값 추가 (`REPORT_DAILY_CREATE_LIMIT`, 기본 3회)
- [x] 백엔드 일일 채팅 quota 설정값 추가 (`REPORT_CHAT_DAILY_CREATE_LIMIT`, 기본 30회)
- [x] `Report` 생성 전 사용자별 한국 시간 기준 일일 생성 횟수 검사
- [x] 리포트 quota 초과 시 `429 rate_limit_exceeded` 응답
- [x] `ReportMessage` 사용자 메시지 생성 전 사용자별 한국 시간 기준 일일 채팅 횟수 검사
- [x] 채팅 quota 초과 시 `429 rate_limit_exceeded` 응답
- [x] 리포트 4번째 생성 요청 `429` 테스트 추가
- [x] 채팅 31번째 요청 `429` 테스트 추가
- [x] `IngredientLinkMapping` 모델 추가
- [x] iHerb URL allowlist 검증 및 서버 저장값 기반 응답 주입
- [x] AI 서버 schema/citation/RAG 품질/guardrail 보강
- [x] 추천 정렬 및 위험 신호 반영 로직 보강

## 요약
- 문서상 필수인 서버 측 사용량 제한, iHerb 성분 링크 매핑, citation 검증, 낮은 RAG 품질 처리, 안전 가드레일 보강을 우선 구현한다.
- AI 추천 품질 고도화는 “근거 없는 추천 방지”와 “위험/불확실성 표시” 수준까지 포함하고, 대규모 랭킹 모델화는 후속으로 남긴다.
- 기본 quota는 설정값 기반 `일 3회 리포트 생성 / 일 30회 채팅`으로 둔다.

## 주요 변경
- Django 백엔드
  - [x] `Report` 생성 전 사용자별 일일 리포트 생성 횟수를 검사하고 초과 시 `429 rate_limit_exceeded`를 반환한다.
  - [x] `ReportMessage` 생성 전 사용자별 일일 채팅 횟수를 검사하고 초과 시 `429`를 반환한다.
  - `IngredientLinkMapping` 모델을 추가해 `normalized_name`, `ingredient_name_ko`, `iherb_url`, `iherb_category_name`, `is_active`를 관리한다.
  - iHerb URL은 서버 저장값만 사용하고, `kr.iherb.com` 등 allowlist 도메인 검증을 통과한 값만 리포트 응답에 주입한다.
  - AI 서버 응답의 `recommended_ingredients`에 `iherb_url`, `iherb_category_name`을 병합해 저장/응답한다.

- AI 서버
  - `RecommendedIngredient` schema와 LLM output schema에 `iherb_url: null`, `iherb_category_name: null` 필드를 추가하되 AI는 링크를 생성하지 않는다.
  - report/chat 생성 후 citation `document_id`가 제공된 RAG/report context 안에 있는지 검증하고, 허용되지 않은 citation은 제거하거나 안전 응답으로 전환한다.
  - RAG 검색 결과가 비어 있거나 최고 점수가 기준 미만이면 `needs_clarification`과 질문을 반환해 리포트 생성을 강행하지 않는다.
  - normalize 결과의 낮은 confidence 항목은 `needs_clarification`으로 표시하고, 사용자에게 확인 질문을 제공한다.
  - guardrail 키워드를 개인정보 과다 입력, 서비스 범위 이탈, 과도한 확신 표현, 근거 없는 citation 위험까지 확장한다.

- 추천/주의사항 로직
  - fallback 추천은 functional ingredient context를 그대로 나열하지 않고, 건강 목표 우선순위와 RAG score를 기준으로 정렬한다.
  - 복용 약/특이사항과 RAG metadata의 `precautions`, `side_effects`, `drugs`, `conditions` 계열 정보를 비교해 위험 신호가 있으면 추천 사유와 주의사항에 명시한다.
  - 위험 신호가 강하거나 근거가 부족하면 성분 추천 대신 추가 확인 질문을 반환한다.

## 테스트 계획
- 백엔드
  - [x] 리포트 4번째 생성 요청이 `429`를 반환하는지 테스트한다.
  - [x] 채팅 31번째 요청이 `429`를 반환하는지 테스트한다.
  - iHerb 매핑이 있는 성분은 URL/category가 응답에 포함되고, 없는 성분은 필드가 `null` 또는 미표시 가능한 값으로 유지되는지 테스트한다.
  - allowlist 밖 URL은 저장/응답 주입되지 않는지 테스트한다.

- AI
  - 낮은 normalize confidence가 `needs_clarification`을 반환하는지 테스트한다.
  - 낮은 RAG score 또는 빈 검색 결과가 추가 확인 질문으로 이어지는지 테스트한다.
  - RAG context에 없는 citation `document_id`가 제거/차단되는지 테스트한다.
  - 약물/질환 위험 metadata가 precautions에 반영되는지 테스트한다.
  - 개인정보 과다 입력, 범위 이탈, 과도한 확신 표현이 guardrail에 걸리는지 테스트한다.

## 가정
- quota 기준은 한국 시간 기준 일 단위로 계산한다.
- 기본 제한값은 환경변수 또는 Django settings로 변경 가능하게 둔다.
- iHerb 초기 데이터는 현재 저장소에 완성 매핑 파일이 없으므로, 우선 Django fixture 또는 migration seed로 MVP 성분 샘플을 넣고 이후 운영 데이터로 확장한다.
- 프론트는 이미 `ingredient.iherb_url` 표시와 `429` 에러 분기를 준비하고 있으므로, 이번 작업은 API 응답 계약을 맞추는 데 집중한다.
