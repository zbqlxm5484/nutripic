# API And Naming Conventions

API endpoint and payload naming should follow the backend. Since the backend is Django, API names should use snake_case unless an existing contract or external integration requires otherwise.

## Source Of Truth

- The Django backend is the source of truth for API endpoints.
- Frontend and AI integrations should follow backend naming instead of inventing alternate casing.
- If backend and frontend naming disagree, resolve the backend contract first, then update consumers.

## Endpoint Naming

Use snake_case for API path segments.

Recommended:

```text
/api/user_profiles/
/api/meal_records/
/api/nutrition_logs/
```

Avoid:

```text
/api/userProfiles/
/api/meal-records/
/api/nutritionLogs/
```

Use trailing slashes consistently if the Django project is configured that way. Do not mix styles within the same API surface.

## Request And Response Fields

Use snake_case for:

- JSON request body fields
- JSON response fields
- Query parameters
- Path parameter names in documentation
- Error response fields

Recommended:

```json
{
  "user_id": 1,
  "meal_record_id": 10,
  "created_at": "2026-06-22T12:00:00+09:00"
}
```

Avoid:

```json
{
  "userId": 1,
  "mealRecordId": 10,
  "createdAt": "2026-06-22T12:00:00+09:00"
}
```

## Frontend Integration

Frontend code may use local conventions internally, but API boundaries must preserve backend field names.

- Do not silently convert API names unless there is an established shared mapper.
- Keep request and response typings aligned with backend serializers.
- When documenting or mocking API data, use the backend snake_case contract.

## Backend Integration

Backend code should keep Django and Django REST Framework conventions consistent.

- Prefer serializer field names that match API response names.
- Keep URL route names and path segments predictable.
- Do not introduce camelCase fields for internal APIs.
- If an external service requires a different convention, isolate the conversion at the integration boundary.

## AI Integration

AI pipelines that call project APIs should use the same backend contract.

- Prompt examples that include API payloads should use snake_case.
- Dataset fields intended to map to API fields should use the backend field names.
- Generated outputs that become API requests should be validated against backend serializers or documented schemas.

## Exceptions

Exceptions are allowed only when there is a clear reason:

- An external API or SDK requires another casing style.
- A legacy endpoint already uses another convention and changing it would break clients.
- A documented migration plan temporarily supports both styles.

When an exception exists, document it near the API contract and keep conversion logic localized.
