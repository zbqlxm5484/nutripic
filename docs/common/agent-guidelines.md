# Agent Guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge these with project-specific instructions as needed.

Tradeoff: these guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

Do not assume. Do not hide confusion. Surface tradeoffs.

Before implementing:

- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them instead of picking silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop, name what is confusing, and ask.

Good agents make uncertainty visible before it becomes broken code.

## 2. Simplicity First

Write the minimum code that solves the problem. Add nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No flexibility or configurability that was not requested.
- No error handling for impossible scenarios.
- If 200 lines could reasonably be 50, simplify before finalizing.

Ask: would a senior engineer say this is overcomplicated? If yes, reduce the design.

## 3. Surgical Changes

Touch only what you must. Clean up only your own mess.

When editing existing code:

- Do not improve adjacent code, comments, or formatting unless required.
- Do not refactor things that are not broken.
- Match existing style, even if you would normally write it differently.
- If you notice unrelated dead code, mention it instead of deleting it.

When your changes create orphans:

- Remove imports, variables, functions, and files made unused by your own changes.
- Do not remove pre-existing dead code unless asked.

Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

Define success criteria. Loop until verified.

Transform tasks into verifiable goals:

- "Add validation" becomes "write tests for invalid inputs, then make them pass."
- "Fix the bug" becomes "write or run a check that reproduces it, then make it pass."
- "Refactor X" becomes "ensure relevant checks pass before and after."

For multi-step tasks, state a brief plan:

```text
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

Strong success criteria allow independent progress. Weak criteria such as "make it work" require clarification.

## 5. Frontend Guidance

Frontend contributors should apply the common rules with extra attention to user experience.

- Follow the existing design system and component structure first.
- Do not introduce new state management, routing, styling, or component abstractions without a clear need.
- Consider loading, empty, error, disabled, and mobile states when the requested change affects UI behavior.
- Keep API usage aligned with backend contracts, including field names and endpoint casing.
- Prefer accessible, semantic markup and clear interaction states.

## 6. Backend Guidance

Backend contributors should apply the common rules with extra attention to contracts and data integrity.

- Treat API request and response shapes as contracts.
- When changing endpoints, consider authentication, authorization, validation, serialization, and error format.
- Keep database migrations narrow and reversible where possible.
- Avoid changing model relationships, transaction behavior, or permissions unless the task requires it.
- Keep Django naming and structure consistent with nearby code.

## 7. AI Guidance

AI contributors should apply the common rules with extra attention to reproducibility and evaluation.

- Make model inputs, outputs, prompts, and assumptions explicit.
- Validate AI pipeline changes with representative examples.
- Separate deterministic tests from quality checks for non-deterministic model behavior.
- Do not change prompts, thresholds, model names, or data preprocessing casually.
- Keep frontend and backend API contracts as the source of truth for integration.

## Success Signal

These guidelines are working if diffs are smaller, fewer rewrites are needed due to overcomplication, and clarifying questions happen before implementation mistakes.
