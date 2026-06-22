# Git Conventions

This project uses a `main` and `develop` branch flow. Feature work should happen on child branches from `develop`, then return to `develop` through pull requests.

## Branch Strategy

Long-lived branches:

- `main`: stable branch for production-ready or release-ready code.
- `develop`: integration branch for active development.

Working branches:

- Create all feature, fix, and task branches from `develop`.
- Open pull requests back into `develop`.
- Merge pull requests into `develop` using squash merge.
- Keep each pull request focused on one coherent change.

Recommended flow:

```text
develop
  -> prefix/feature-name-in-english
  -> PR into develop
  -> squash merge
```

## Branch Naming

Branch format:

```text
prefix/feature-name-in-english
```

Rules:

- Use lowercase English for the branch description.
- Use hyphens between English words.
- Keep the branch name short but specific.
- Use the same prefix that will be used in commits and the PR title.

Examples:

```text
feat/user-profile
fix/login-validation
docs/api-conventions
refactor/image-upload-service
test/nutrition-parser
```

## Commit Message Convention

Commit format:

```text
prefix: 개발할 기능 또는 변경 내용
```

Rules:

- Use the same prefix as the branch.
- Write the description in Korean.
- Use an imperative or concise noun phrase style.
- Keep the first line short and specific.
- Avoid vague messages such as `fix`, `update`, `작업`, or `수정`.
- If more context is needed, add it in the commit body.

Examples:

```text
feat: 사용자 프로필 화면 추가
fix: 로그인 입력값 검증 오류 수정
docs: API 네이밍 규칙 문서화
refactor: 이미지 업로드 서비스 구조 정리
test: 영양 정보 파서 테스트 추가
```

## Pull Request Convention

PR title format:

```text
prefix: 개발할 기능 또는 변경 내용
```

PR title rules:

- Follow the same convention as commit messages.
- Use the same prefix as the branch and commits.
- Describe the user-visible or codebase-visible change clearly.

Recommended PR body:

```md
## Summary

- 변경 사항 요약
- 구현 범위

## Verification

- 실행한 테스트 또는 확인 방법
- 확인하지 못한 항목이 있다면 그 이유

## Notes

- 리뷰어가 알아야 할 결정, 제한, 후속 작업
```

## Prefixes

Use common conventional commit-style prefixes.

| Prefix | Use for |
| --- | --- |
| `feat` | New user-facing or product feature |
| `fix` | Bug fix |
| `docs` | Documentation-only change |
| `refactor` | Code restructuring without behavior change |
| `test` | Tests or test infrastructure |
| `chore` | Maintenance, setup, or non-product tasks |
| `style` | Formatting or style-only changes |
| `perf` | Performance improvement |
| `ci` | CI configuration or workflow changes |
| `build` | Build system or dependency changes |

Choose the prefix by the main purpose of the work. If a change touches multiple areas, prefer the prefix that best describes the user-facing or reviewer-facing intent.

## Squash Merge Rules

When merging a PR into `develop`:

- Use squash merge.
- Ensure the final squash commit title follows the PR title convention.
- Keep the squash commit body useful if the PR contains important implementation notes.
- Do not merge unrelated work into the same PR.

## Examples

Feature:

```text
Branch: feat/user-profile
Commit: feat: 사용자 프로필 화면 추가
PR: feat: 사용자 프로필 화면 추가
```

Bug fix:

```text
Branch: fix/login-validation
Commit: fix: 로그인 입력값 검증 오류 수정
PR: fix: 로그인 입력값 검증 오류 수정
```

Documentation:

```text
Branch: docs/git-conventions
Commit: docs: Git 작업 규칙 문서화
PR: docs: Git 작업 규칙 문서화
```
