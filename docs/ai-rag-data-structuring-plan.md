# AI/RAG 데이터 구조화 작업 계획

이 문서는 FastAPI AI 서버와 Django 백엔드 연동이 진행되는 동안, 별도 브랜치에서 병렬로 진행할 데이터 구조화 및 정리 작업 범위를 정의한다.

현재 목표는 LangChain 생성 로직을 바로 고도화하는 것이 아니라, RAG 검색과 성분 후보 선정에 사용할 수 있는 근거 데이터를 정리하는 것이다. 단, RAG 문서 schema는 아직 확정하지 않는다. 기능성원료 PDF와 연구 근거 Sheet의 실제 컬럼, 추출 가능성, FastAPI 응답 계약을 함께 보면서 확정한다.

## 1. 작업 범위

이번 데이터 브랜치의 범위는 다음으로 제한한다.

- 건강기능식품 기능성원료 인정현황 PDF 기반 데이터 추출 및 구조화
- 메타분석 및 연구 근거 수준 기반 성분-효과 데이터 구조화
- iDISK 증상/성분 데이터 인덱싱 전략 정리
- RAG 문서 schema 후보 정리
- source_type, document_id, metadata 규칙 후보 정리
- 동적 정규화 사전을 위한 저장 구조와 검증 정책 정리

이번 브랜치에서 제외하는 작업은 다음과 같다.

- LangChain prompt 구현
- 실제 LLM 호출 구현
- vector DB 연결
- embedding 생성 배치 구현
- Django 모델 또는 API 구현
- iHerb URL 매핑 구현
- 가드레일 판정 로직 구현

## 2. 데이터 소스

AI/RAG 레이어가 사용할 주요 데이터 소스는 다음 세 종류로 둔다.

| source_type | 설명 | 주 용도 |
| --- | --- | --- |
| `functional_ingredient` | 건강기능식품 기능성원료 인정현황 | 성분별 기능성, 일일섭취량, 섭취 시 주의사항 근거 |
| `evidence_review` | 메타분석, 체계적 문헌고찰, 임상 연구 근거 수준 데이터 | 증상 또는 건강 목표에 대해 어떤 성분이 얼마나 타당한지 점수화 |
| `idisk` | iDISK 증상/성분 데이터 | 영어 기반 증상, 성분, 키워드 검색 근거 |

사용자가 추가하려는 Google Sheet는 `evidence_review` 데이터 소스로 취급한다.

기능성원료 인정현황은 사용자가 제공한 PDF를 1차 원본으로 사용한다.

원본 파일:

```text
C:/Users/SSAFY/Downloads/건강기능식품 기능성 원료 인정 현황.pdf
```

확인된 파일 특성:

- 파일 크기: 약 1.4MB
- 페이지 수: 122쪽
- 사용자가 확인한 환경에서는 PDF 텍스트가 추출됨
- 일부 추출기에서는 한글 글꼴 매핑이 깨질 수 있으므로 추출 도구를 고정해야 함
- 표 기반 자료로 보이므로 텍스트 추출 후 행/컬럼 재구성 규칙 검증이 필요함

원본 링크:

```text
https://docs.google.com/spreadsheets/d/1VqJQ_C_R0OziW7m2wtdYz2-8n4_4xxyFRypzmo8iLN8/edit?pli=1&gid=2#gid=2
```

해당 시트는 메타분석 결과 등을 기반으로 특정 성분이 특정 효과 또는 건강 목표에 대해 어느 정도의 연구 근거를 가지는지 보여주는 자료로 본다. 따라서 리포트 문장 생성 근거뿐 아니라, RAG 검색 이후 성분 후보를 정렬하고 필터링하는 데 사용한다.

iDISK 2.0은 다음 GitHub repository를 원본 후보로 사용한다.

```text
https://github.com/houyurain/iDISK2.0
```

확인된 iDISK 2.0 데이터 구조:

- repository license: Apache-2.0
- repository의 `Data/Entity`와 `Data/Relation` 아래 README에서 실제 CSV 다운로드 링크를 제공함
- Entity 파일 후보: `DSI.csv`, `DSP.csv`, `D.csv`, `Dis.csv`, `SS.csv`
- Relation 파일 후보: `dsp_dsi.csv`, `dsi_dis.csv`, `dsi_d.csv`, `dsi_ss.csv`
- 주요 엔티티: Dietary Supplement Ingredient, Dietary Supplement Product, Drug, Disease, Sign/Symptom
- 주요 관계: DSI-Disease 효과, DSI-Sign/Symptom 이상반응, DSI-Drug 상호작용, DSP-DSI 포함 관계

Neutripic MVP에서는 상품 중심 추천을 하지 않으므로 `DSP.csv`와 `dsp_dsi.csv`는 우선순위를 낮춘다. 우선 처리 대상은 `DSI.csv`, `SS.csv`, `D.csv`, `Dis.csv`, `dsi_ss.csv`, `dsi_d.csv`, `dsi_dis.csv`이다.

## 3. 추천 흐름에서 데이터의 역할

리포트 생성 전 성분 후보 선정은 다음 순서로 생각한다.

```text
사용자 입력
-> input guardrail
-> normalize
-> RAG 검색
   -> evidence_review에서 건강 목표별 성분 후보 검색
   -> functional_ingredient에서 용량/기능성/주의사항 보강
   -> idisk에서 증상/성분 관련 컨텍스트 보강
-> 성분 후보 점수화
-> reports/generate
-> output guardrail
```

`evidence_review`는 "어떤 증상 또는 건강 목표에 어떤 성분이 타당한가"를 판단하는 1차 후보 선정 근거로 사용한다.

`functional_ingredient`는 추천된 성분을 사용자에게 설명할 때 필요한 공식 기능성, 일일섭취량, 주의사항을 보강한다.

`idisk`는 사용자 자유 입력, 증상 표현, 영어 기반 검색 질의와의 연결성을 높이는 보조 근거로 사용한다.

## 4. RAG 문서 Schema 후보

RAG 문서 schema는 아직 확정하지 않는다. 아래 형태는 FastAPI `/internal/ai/v1/rag/search/` 응답과 맞추기 위한 후보안이다.

모든 데이터 소스는 최종적으로 아래와 비슷한 공통 문서 형태로 변환하는 것을 검토한다.

```json
{
  "document_id": "evidence_review_sleep_magnesium",
  "source_type": "evidence_review",
  "source_name": "메타분석 기반 성분-효과 근거 데이터",
  "title": "수면의 질 - 마그네슘",
  "content": "마그네슘은 수면의 질 개선과 관련된 연구 근거가 일부 보고되어 있다...",
  "metadata": {
    "ingredient_name_ko": "마그네슘",
    "ingredient_name_en": "Magnesium",
    "normalized_name": "magnesium",
    "health_goal_code": "sleep_quality",
    "effect_name_ko": "수면의 질",
    "effect_name_en": "sleep quality",
    "evidence_grade": "moderate",
    "evidence_score": 0.72,
    "study_type": "meta_analysis",
    "citation_count": 3,
    "source_url": "",
    "version": "2026-06-24"
  }
}
```

공통 필드는 `/internal/ai/v1/rag/search/` 응답의 `results` 구조와 맞추되, 실제 확정은 데이터 샘플을 만든 뒤 진행한다.

필드 규칙:

- `document_id`: source_type과 핵심 엔티티를 조합한 안정적인 고유값
- `source_type`: `functional_ingredient`, `evidence_review`, `idisk` 중 하나
- `source_name`: 사람이 읽을 수 있는 원본 데이터명
- `title`: 검색 결과 목록과 citations에서 보여줄 수 있는 짧은 제목
- `content`: embedding과 keyword search에 사용할 요약 본문
- `metadata`: 필터링, 정렬, 리포트 생성에 필요한 구조화 필드

## 5. `evidence_review` Schema

메타분석/연구 근거 수준 데이터는 성분과 효과의 관계를 한 문서 단위로 만든다.

문서 단위:

```text
성분 1개 + 건강 목표 또는 효과 1개 = RAG 문서 1개
```

예시:

```text
마그네슘 + 수면의 질
오메가3 + 혈중 중성지질
루테인 + 눈 건강
프로바이오틱스 + 장 건강
```

권장 metadata:

| field | 설명 |
| --- | --- |
| `ingredient_name_ko` | 한국어 성분명 |
| `ingredient_name_en` | 영어 성분명 |
| `normalized_name` | 내부 표준 성분명 |
| `health_goal_code` | 내부 건강 목표 코드 |
| `effect_name_ko` | 한국어 효과명 |
| `effect_name_en` | 영어 효과명 |
| `evidence_grade` | 근거 수준 등급 |
| `evidence_score` | 정렬용 수치 점수 |
| `study_type` | meta_analysis, systematic_review, rct 등 |
| `population` | 연구 대상이 특정될 경우 |
| `outcome_summary` | 효과 결과 요약 |
| `safety_note` | 연구 또는 자료상 안전 관련 메모 |
| `citation_count` | 근거 문헌 수 |
| `source_url` | 원본 또는 참고 링크 |
| `raw_row_id` | 원본 시트 행 추적용 ID |
| `version` | 데이터 버전 |

`evidence_grade` 초안:

| grade | 의미 |
| --- | --- |
| `high` | 일관된 메타분석/체계적 문헌고찰 근거가 있음 |
| `moderate` | 제한적이지만 의미 있는 임상 근거가 있음 |
| `low` | 연구 수가 적거나 결과가 불일치함 |
| `insufficient` | 추천 근거로 쓰기 어려움 |
| `negative` | 효과 없음 또는 부정적 결과가 우세함 |

`evidence_score` 초안:

```text
high: 0.85-1.00
moderate: 0.65-0.84
low: 0.40-0.64
insufficient: 0.10-0.39
negative: 0.00-0.09
```

점수는 추천 후보 정렬용이지, 사용자에게 효과를 보장하는 표현으로 사용하지 않는다.

## 6. `functional_ingredient` Schema

기능성원료 인정현황 데이터는 성분 또는 원료 단위로 문서화한다.

이 작업은 `건강기능식품 기능성 원료 인정 현황.pdf`를 기반으로 우선 처리한다.

문서 단위:

```text
기능성원료 1개 = RAG 문서 1개
```

권장 metadata:

| field | 설명 |
| --- | --- |
| `ingredient_name_ko` | 한국어 원료명 |
| `ingredient_name_en` | 영어 원료명 |
| `normalized_name` | 내부 표준 성분명 |
| `functional_claims` | 인정 기능성 배열 |
| `daily_dosage` | 일일섭취량 원문 또는 구조화 값 |
| `precautions` | 섭취 시 주의사항 배열 |
| `recognized_type` | 고시형, 개별인정형 등 |
| `source_url` | 원본 출처 |
| `version` | 데이터 버전 |

이 데이터는 리포트의 권장 용량, 기능성, 주의사항 문구에 우선 사용한다.

PDF 처리 단계:

1. PDF의 표 구조와 섹션 구성을 육안으로 확인한다.
2. 정상 한글 텍스트를 추출할 수 있는 도구와 명령을 고정한다.
3. 원본에 기능성원료명, 기능성 내용, 일일섭취량, 섭취 시 주의사항, 인정 유형이 어떤 컬럼 또는 문단으로 존재하는지 확인한다.
4. 추출 텍스트를 페이지, 섹션, 원료 단위로 나누는 규칙을 만든다.
5. 추출이 안정적인 필드와 수동 검수가 필요한 필드를 구분한다.
6. 기능성원료 5-10개만 먼저 샘플 JSON으로 만든다.
7. 샘플 JSON을 기준으로 RAG 문서 schema와 metadata 필드를 함께 확정한다.

PDF 추출 관련 주의:

- 추출 도구에 따라 한글이 깨질 수 있으므로, 정상 추출되는 도구의 버전과 명령을 문서화한다.
- OCR은 기본 경로가 아니라, 정상 텍스트 추출이 불가능한 페이지가 발견될 때만 보조 수단으로 사용한다.
- 용량, 수치, 단위, 주의사항은 오류 영향이 크므로 자동 추출 후 검수 상태를 둔다.
- 저장소에는 원본 PDF를 바로 포함하지 않고, 라이선스와 공개 범위를 확인한 뒤 sample JSON만 포함하는 방향을 우선 검토한다.

## 7. `idisk` Schema

iDISK는 영어 기반 증상/성분 데이터를 검색 가능한 단위로 나눈다.

문서 단위는 iDISK 2.0 CSV 원본 확인 후 결정하되, 우선 다음 후보를 둔다.

- 증상 1개 + 관련 성분 목록
- 성분 1개 + 관련 증상 목록
- 증상-성분 관계 1개
- 성분 1개 + 약물 상호작용 관계
- 성분 1개 + 질병 관련 효과 관계

권장 metadata:

| field | 설명 |
| --- | --- |
| `idisk_entity_id` | iDISK 엔티티 ID |
| `idisk_relation_id` | 관계 파일의 행 또는 관계 추적용 ID |
| `symptom_name_en` | 영어 증상명 |
| `symptom_name_ko` | 한국어 번역명 |
| `disease_name_en` | 영어 질병명 |
| `drug_name_en` | 영어 약물명 |
| `ingredient_name_en` | 영어 성분명 |
| `ingredient_name_ko` | 한국어 성분명 |
| `normalized_name` | 내부 표준 성분명 |
| `keywords_en` | 영어 검색 키워드 |
| `keywords_ko` | 한국어 검색 키워드 |
| `relation_type` | `is_effective_for`, `has_adverse_reaction`, `interacts_with` 등 |
| `source_dataset` | `DSI.csv`, `dsi_ss.csv` 등 원본 파일명 |
| `source_description` | iDISK 원본 관계 설명 |
| `interaction_rating` | 약물 상호작용 등급이 있는 경우 |
| `source_url` | 원본 출처 |
| `version` | 데이터 버전 |

iDISK 2.0 처리 우선순위:

1. `DSI.csv`에서 성분 기본 정보와 안전성, 작용기전, source material 확인
2. `SS.csv`에서 증상/징후 vocabulary 확인
3. `dsi_ss.csv`에서 성분-증상 관계와 이상반응 관계 확인
4. `dsi_d.csv`에서 성분-약물 상호작용 정보를 safety context로 분리
5. `dsi_dis.csv`에서 성분-질병 효과 관계 확인
6. `DSP.csv`, `dsp_dsi.csv`는 상품 추천과 직접 연결되므로 MVP에서는 제외하거나 낮은 우선순위로 보류

iDISK 2.0은 영어 기반이므로 한국어 사용자 입력과 연결하려면 별도의 번역/정규화 레이어가 필요하다. `SS.csv`, `D.csv`, `Dis.csv`, `DSI.csv`의 `Name`을 내부 `normalized_name` 및 한국어 alias 후보와 연결하는 작업은 RAG schema 확정 이후 진행한다.

## 8. 동적 정규화 사전 정책

정규화 사전은 처음부터 완성하지 않고, AI가 후보를 만들고 시스템이 상태를 관리하는 방식으로 둔다.

상태값:

| status | 의미 |
| --- | --- |
| `approved` | 검토 완료 또는 신뢰 가능한 seed |
| `auto_added` | AI가 자동 생성했으나 검토 전 |
| `pending` | 충돌 또는 낮은 confidence로 검토 필요 |
| `rejected` | 사용하지 않기로 한 매핑 |

저장 후보 schema:

```json
{
  "original_text": "잠을 깊게 못 자요",
  "normalized_code": "sleep_quality",
  "entity_type": "health_goal",
  "name_ko": "수면의 질",
  "name_en": "sleep quality",
  "aliases_ko": ["숙면", "깊은 잠", "잠을 깊게 못 잠"],
  "confidence": 0.86,
  "status": "auto_added",
  "created_by": "ai",
  "reason": "수면의 깊이와 질을 나타내는 사용자 표현으로 판단됨"
}
```

주의 정책:

- 약물명, 질병명, 고위험 증상은 자동 `approved` 처리하지 않는다.
- 기존 alias가 다른 코드에 연결되어 있으면 `pending`으로 둔다.
- confidence가 낮으면 리포트 생성을 강행하지 않고 추가 확인 질문 후보를 만든다.
- AI가 만든 정규화 결과는 검색 후보이지 의학적 판단이 아니다.

## 9. 성분 후보 점수화 초안

RAG 검색 결과에서 성분 후보를 고를 때는 다음 신호를 조합한다.

| signal | 설명 |
| --- | --- |
| `evidence_score` | 메타분석/연구 근거 수준 점수 |
| `rag_score` | 검색 유사도 점수 |
| `goal_priority_weight` | 사용자가 선택한 건강 목표 우선순위 |
| `safety_penalty` | 복용 약, 질환, 임신/수유, 알레르기 등 주의 요인 |
| `functional_data_bonus` | 기능성원료 인정현황에서 용량/주의사항이 확인되는지 |

초기 의사코드:

```text
candidate_score =
  evidence_score * 0.45
  + rag_score * 0.25
  + goal_priority_weight * 0.20
  + functional_data_bonus * 0.10
  - safety_penalty
```

이 점수는 내부 정렬용이다. 사용자에게는 "효과가 강하다"가 아니라 "검색된 근거와 사용자의 목표를 함께 고려했을 때 후보로 검토할 수 있다"처럼 안전하게 표현한다.

## 10. 우선 작업 순서

1. 기능성원료 PDF의 표 구조 확인
2. 정상 한글 텍스트 추출 도구와 명령 고정
3. 추출 텍스트를 페이지/섹션/원료 단위로 분리하는 규칙 작성
4. PDF에서 기능성원료 5-10개 샘플을 반자동으로 구조화
5. 샘플을 기준으로 `functional_ingredient` 필드 후보 정리
6. Google Sheet 원본 컬럼 확인
7. `evidence_review` 컬럼을 성분-효과 관계 데이터로 매핑
8. `evidence_grade`와 `evidence_score` 변환 규칙 후보 작성
9. 성분명 `normalized_name` 규칙 후보 작성
10. 건강 목표 코드 목록 초안 작성
11. iDISK 2.0 CSV 다운로드 가능 여부와 라이선스 재확인
12. iDISK entity/relation 파일 컬럼 확인
13. iDISK 문서 단위 후보 정리
14. FastAPI `rag/search` fixture를 샘플 JSON 기반으로 바꿀 수 있는지 확인
15. vector DB 적재를 위한 embedding 대상 필드 후보 정리

## 11. 산출물

데이터 구조화 브랜치에서 기대하는 산출물은 다음과 같다.

```text
docs/ai-rag-data-structuring-plan.md
ai/app/data/processed/evidence_reviews.sample.json
ai/app/data/processed/functional_ingredients.sample.json
ai/app/data/processed/idisk_documents.sample.json
ai/app/data/dictionaries/normalization_seed.sample.json
```

실제 원본 데이터가 크거나 라이선스/공개 범위가 불확실한 경우, 저장소에는 sample 파일만 두고 원본 데이터 확보 및 변환 절차를 문서화한다.

## 12. 확인 필요 사항

- Google Sheet의 실제 컬럼명과 각 컬럼의 의미
- 해당 Sheet 데이터를 저장소에 포함해도 되는지 여부
- 원본 데이터의 라이선스 또는 공개 범위
- 기능성원료 인정현황 PDF를 저장소에 포함해도 되는지 여부
- 기능성원료 인정현황의 원본 엑셀/CSV 확보 가능 여부
- PDF 텍스트 추출 도구와 명령
- 텍스트 추출 실패 페이지가 있을 때의 OCR fallback 방식
- iDISK 2.0 Google Drive CSV 다운로드 가능 여부
- iDISK 2.0 CSV 파일을 저장소에 포함해도 되는지 여부
- iDISK 2.0 citation 표기 방식
- 최종 vector DB 선택
- Django DB에 일부 데이터를 저장할지, AI 서버 내부 데이터로만 둘지
