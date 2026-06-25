# Git 작업 규칙

이 프로젝트는 `main`과 `develop`을 기준으로 브랜치를 운영한다. 기능 작업은 `develop`에서 파생한 하위 브랜치에서 진행하고, pull request를 통해 다시 `develop`으로 반영한다.

## 브랜치 전략

장기 유지 브랜치:

- `main`: 배포 가능하거나 릴리스 준비가 끝난 코드를 유지하는 안정 브랜치.
- `develop`: 진행 중인 개발 내용을 통합하는 브랜치.

작업 브랜치:

- 기능, 버그 수정, 문서 등 모든 작업 브랜치는 `develop`에서 만든다.
- pull request 대상 브랜치는 `develop`으로 한다.
- pull request는 squash merge로 `develop`에 반영한다.
- 하나의 pull request에는 하나의 일관된 변경만 담는다.

권장 흐름:

```text
develop
  -> prefix/feature-name-in-english
  -> develop으로 PR 생성
  -> squash merge
```

## 브랜치 이름

브랜치 형식:

```text
prefix/feature-name-in-english
```

규칙:

- 브랜치 설명은 소문자 영어로 작성한다.
- 영어 단어 사이는 하이픈으로 구분한다.
- 짧지만 작업 내용을 알아볼 수 있게 작성한다.
- 커밋과 PR 제목에 사용할 prefix와 같은 prefix를 사용한다.

예시:

```text
feat/user-profile
fix/login-validation
docs/api-conventions
refactor/image-upload-service
test/nutrition-parser
```

## 커밋 메시지 규칙

커밋 형식:

```text
prefix: 개발할 기능 또는 변경 내용
```

규칙:

- 브랜치와 같은 prefix를 사용한다.
- 설명은 한국어로 작성한다.
- 명령형 또는 간결한 명사구 형태로 작성한다.
- 첫 줄은 짧고 구체적으로 작성한다.
- `fix`, `update`, `작업`, `수정`처럼 모호한 메시지는 피한다.
- 추가 설명이 필요하면 커밋 본문에 작성한다.

예시:

```text
feat: 사용자 프로필 화면 추가
fix: 로그인 입력값 검증 오류 수정
docs: API 네이밍 규칙 문서화
refactor: 이미지 업로드 서비스 구조 정리
test: 영양 정보 파서 테스트 추가
```

## Pull Request 규칙

PR 제목 형식:

```text
prefix: 개발할 기능 또는 변경 내용
```

PR 제목 규칙:

- 커밋 메시지와 같은 규칙을 따른다.
- 브랜치와 커밋에 사용한 prefix를 동일하게 사용한다.
- 사용자 또는 코드베이스 관점에서 드러나는 변경을 명확히 설명한다.

권장 PR 본문:

```md
## 요약

- 변경 사항 요약
- 구현 범위

## 확인

- 실행한 테스트 또는 확인 방법
- 확인하지 못한 항목이 있다면 그 이유

## 참고

- 리뷰어가 알아야 할 결정, 제한, 후속 작업
```

## Prefix 목록

일반적인 conventional commit 스타일의 prefix를 사용한다.

| Prefix | 사용 기준 |
| --- | --- |
| `feat` | 사용자 또는 제품 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서만 변경 |
| `refactor` | 동작 변경 없는 코드 구조 개선 |
| `test` | 테스트 또는 테스트 기반 코드 변경 |
| `chore` | 유지보수, 설정, 제품 기능과 무관한 작업 |
| `style` | 포맷팅 또는 스타일만 변경 |
| `perf` | 성능 개선 |
| `ci` | CI 설정 또는 워크플로 변경 |
| `build` | 빌드 시스템 또는 의존성 변경 |

작업의 주된 목적에 맞춰 prefix를 선택한다. 여러 영역을 함께 수정했다면 사용자나 리뷰어가 이해하기 쉬운 대표 의도에 맞춘다.

## Squash Merge 규칙

PR을 `develop`에 병합할 때:

- squash merge를 사용한다.
- 최종 squash 커밋 제목은 PR 제목 규칙을 따른다.
- PR에 중요한 구현 메모가 있다면 squash 커밋 본문에 유용하게 남긴다.
- 관련 없는 작업을 같은 PR에 섞어 병합하지 않는다.

## 예시

기능 추가:

```text
Branch: feat/user-profile
Commit: feat: 사용자 프로필 화면 추가
PR: feat: 사용자 프로필 화면 추가
```

버그 수정:

```text
Branch: fix/login-validation
Commit: fix: 로그인 입력값 검증 오류 수정
PR: fix: 로그인 입력값 검증 오류 수정
```

문서 변경:

```text
Branch: docs/git-conventions
Commit: docs: Git 작업 규칙 문서화
PR: docs: Git 작업 규칙 문서화
```
