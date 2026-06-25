# AGENTS.md

Project-wide agent instructions. Read this first, then refer to `docs/` for details.

## Core Behavior

- Answer and collaborate in Korean by default.
- Think before coding: state assumptions, surface tradeoffs, and ask when the request is unclear.
- Keep changes simple and surgical. Do not add speculative features, abstractions, refactors, or formatting churn.
- Match existing project style even when another style seems preferable.
- Touch only files directly related to the request. Mention unrelated issues instead of fixing them silently.
- Define success criteria before multi-step work and verify the result with the smallest meaningful check.

## Project Structure

- `frontend/`: frontend application code.
- `backend/`: Django backend application code.
- `ai/`: AI/model/pipeline-related code.
- `docs/`: human-readable project rules and conventions.

## Git Flow

- Long-lived branches are `main` and `develop`.
- Create feature work from `develop` using a child branch.
- Open PRs back into `develop`.
- Merge PRs into `develop` with squash merge.
- Keep `main` stable and release-oriented.

## Branch, Commit, And PR Convention

- Branch format: `prefix/feature-name-in-english`
- Commit format: `prefix: 개발할 기능 또는 변경 내용`
- PR title format: same as commit convention, `prefix: 개발할 기능 또는 변경 내용`
- Use the same prefix for the branch, commits, and PR title.
- Prefer common prefixes such as `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `style`, `perf`, `ci`, and `build`.

Examples:

```text
feat/user-profile
feat: 사용자 프로필 화면 추가
```

## API And Naming

- API endpoint naming follows the backend.
- Because the backend is Django, use snake_case for API path segments, query parameters, request fields, and response fields unless an existing contract says otherwise.
- Frontend and AI code should follow backend API contracts rather than inventing alternate casing.

## Detailed Docs

- Common agent behavior: `docs/common/agent-guidelines.md`
- Service definition and MVP scope: `docs/common/development.md`
- Git branch, commit, and PR conventions: `docs/conventions/git-conventions.md`
- API and naming conventions: `docs/conventions/api-conventions.md`
- API specifications: `docs/api/`
- Frontend flows and page design: `docs/frontend/`
