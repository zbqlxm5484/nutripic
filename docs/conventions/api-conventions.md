# API와 이름 규칙

API 엔드포인트와 payload 이름은 백엔드를 기준으로 맞춘다. 백엔드가 Django이므로, 기존 계약이나 외부 연동에서 다른 형식을 요구하지 않는 한 API 이름은 snake_case를 사용한다.

## 기준

- Django 백엔드를 API 엔드포인트의 기준으로 삼는다.
- 프론트엔드와 AI 연동 코드는 별도 casing을 만들지 않고 백엔드 이름을 따른다.
- 백엔드와 프론트엔드의 이름이 다르면 먼저 백엔드 계약을 정리한 뒤 사용하는 쪽을 수정한다.

## 엔드포인트 이름

API path segment에는 snake_case를 사용한다.

권장:

```text
/api/user_profiles/
/api/meal_records/
/api/nutrition_logs/
```

피할 예:

```text
/api/userProfiles/
/api/meal-records/
/api/nutritionLogs/
```

Django 프로젝트가 trailing slash를 사용하도록 설정되어 있다면 일관되게 사용한다. 같은 API 영역 안에서 스타일을 섞지 않는다.

## 요청과 응답 필드

다음 항목에는 snake_case를 사용한다.

- JSON 요청 본문 필드
- JSON 응답 필드
- Query parameter
- 문서에 적는 path parameter 이름
- 에러 응답 필드

권장:

```json
{
  "user_id": 1,
  "meal_record_id": 10,
  "created_at": "2026-06-22T12:00:00+09:00"
}
```

피할 예:

```json
{
  "userId": 1,
  "mealRecordId": 10,
  "createdAt": "2026-06-22T12:00:00+09:00"
}
```

## 프론트엔드 연동

프론트엔드 내부 코드는 자체 규칙을 사용할 수 있지만, API 경계에서는 백엔드 필드 이름을 그대로 유지한다.

- 이미 합의된 공통 mapper가 없다면 API 이름을 조용히 변환하지 않는다.
- 요청과 응답 타입은 백엔드 serializer와 맞춘다.
- API 데이터를 문서화하거나 mock으로 만들 때도 백엔드의 snake_case 계약을 사용한다.

## 백엔드 구현

백엔드 코드는 Django와 Django REST Framework 규칙을 일관되게 따른다.

- serializer 필드 이름은 API 응답 이름과 맞추는 것을 우선한다.
- URL route 이름과 path segment는 예측 가능하게 유지한다.
- 내부 API에는 camelCase 필드를 도입하지 않는다.
- 외부 서비스가 다른 규칙을 요구하면 연동 경계에서만 변환한다.

## AI 연동

프로젝트 API를 호출하는 AI pipeline도 같은 백엔드 계약을 사용한다.

- API payload가 포함된 프롬프트 예시는 snake_case를 사용한다.
- API 필드와 연결되는 데이터셋 필드는 백엔드 필드 이름을 사용한다.
- API 요청으로 이어지는 생성 결과는 백엔드 serializer나 문서화된 schema를 기준으로 검증한다.

## 예외

명확한 이유가 있을 때만 예외를 허용한다.

- 외부 API나 SDK가 다른 casing을 요구하는 경우.
- 기존 endpoint가 이미 다른 규칙을 사용하고 있고, 변경하면 client가 깨지는 경우.
- 문서화된 migration 계획에 따라 일시적으로 두 스타일을 모두 지원하는 경우.

예외가 있다면 API 계약 근처에 문서화하고, 변환 로직은 해당 경계 안에만 둔다.
