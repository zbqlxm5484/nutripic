# 프로젝트 문서

이 폴더는 사람이 읽는 프로젝트 규칙, 컨벤션, 명세, 제품 기획 문서를 모아두는 위치다.

## 공통

- `common/agent-guidelines.md`: 코딩 에이전트와 개발자가 함께 따르는 기본 행동 규칙.
- `common/development.md`: Neutripic 서비스 정의, 핵심 기능, 아키텍처, MVP 범위.

## 컨벤션

- `conventions/git-conventions.md`: 브랜치, 커밋, PR, merge workflow 규칙.
- `conventions/api-conventions.md`: Django 백엔드를 기준으로 한 API endpoint와 이름 규칙.

## API

- `api/backend-api-spec.md`: 프론트엔드가 호출하는 Django REST API 명세.
- `api/ai-api-spec.md`: 백엔드가 호출하는 내부 AI/RAG 서버 API 명세.
- `ai-rag-data-structuring-plan.md`: AI/RAG에 사용할 기능성원료, 연구 근거, iDISK 데이터 구조화 계획.

## 프론트엔드

- `frontend/README.md`: 프론트엔드 문서 목록.
- `frontend/user-flow.md`: 전체 사용자 흐름.
- `frontend/page-flow.md`: 페이지 목록, route, 인증 조건, 이동 흐름.
- `frontend/page-components.md`: 페이지 단위 component와 state 구성.

## 사용 방법

짧은 규칙은 먼저 `AGENTS.md`에서 확인한다. 더 많은 맥락이 필요하거나 프론트엔드, 백엔드, AI 담당자가 온보딩할 때 이 문서를 참고한다.
