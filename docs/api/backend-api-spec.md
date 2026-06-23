# Backend API Specification

이 문서는 프론트엔드가 호출하는 Django REST API 명세이다.

AI/RAG 처리는 백엔드가 내부적으로 AI 서버를 호출해서 수행한다. 프론트엔드는 AI 서버를 직접 호출하지 않는다.

## 1. Common Rules

### Base URL

```text
/api/v1/
```

### Naming

- Path segment, query parameter, request field, response field는 `snake_case`를 사용한다.
- Django REST Framework 관례에 맞춰 trailing slash(`/`)를 사용한다.
- 날짜와 시간은 ISO 8601 문자열을 사용한다.

### Authentication

인증이 필요한 API는 JWT access token을 사용한다.

```http
Authorization: Bearer {access_token}
```

### Standard Error Response

```json
{
  "error_code": "validation_error",
  "message": "요청 값이 올바르지 않습니다.",
  "details": {
    "health_goals": ["최대 5개까지 선택할 수 있습니다."]
  }
}
```

### Common Error Codes

| HTTP Status | error_code | Description |
| --- | --- | --- |
| 400 | `validation_error` | 요청 형식 또는 값 오류 |
| 401 | `authentication_failed` | 인증 실패 |
| 403 | `permission_denied` | 권한 없음 |
| 404 | `not_found` | 리소스 없음 |
| 409 | `conflict` | 중복 또는 상태 충돌 |
| 429 | `rate_limit_exceeded` | 사용량 제한 초과 |
| 500 | `internal_server_error` | 서버 오류 |
| 502 | `ai_server_error` | AI 서버 호출 실패 |
| 503 | `service_unavailable` | 외부 데이터 또는 AI 서비스 일시 불가 |

## 2. Auth

### POST `/api/v1/auth/signup/`

회원가입.

Request:

```json
{
  "email": "user@example.com",
  "username": "neutripic_user",
  "password": "password1234!",
  "age": 30,
  "gender": "female"
}
```

Response `201`:

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "neutripic_user",
  "age": 30,
  "gender": "female",
  "created_at": "2026-06-22T12:00:00+09:00"
}
```

### POST `/api/v1/auth/login/`

로그인.

Request:

```json
{
  "login_id": "user@example.com",
  "password": "password1234!"
}
```

Response `200`:

```json
{
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "neutripic_user",
    "role": "user"
  }
}
```

### POST `/api/v1/auth/token/refresh/`

Access token 재발급.

Request:

```json
{
  "refresh_token": "jwt_refresh_token"
}
```

Response `200`:

```json
{
  "access_token": "new_jwt_access_token"
}
```

### POST `/api/v1/auth/logout/`

로그아웃. 백엔드는 전달받은 refresh token을 무효화하고, 클라이언트는 보관 중인 토큰을 삭제한다.

Request:

```json
{
  "refresh_token": "jwt_refresh_token"
}
```

Response `204`

## 3. Users And My Page

### GET `/api/v1/users/me/`

내 회원 정보 조회.

Response `200`:

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "neutripic_user",
  "age": 30,
  "gender": "female",
  "role": "user",
  "created_at": "2026-06-22T12:00:00+09:00"
}
```

### PATCH `/api/v1/users/me/`

내 회원 정보 수정.

Request:

```json
{
  "age": 31,
  "gender": "female"
}
```

Response `200`: 수정된 사용자 정보

### PATCH `/api/v1/users/me/password/`

비밀번호 변경.

Request:

```json
{
  "current_password": "password1234!",
  "new_password": "new_password1234!"
}
```

Response `204`

### DELETE `/api/v1/users/me/`

회원 탈퇴.

Response `204`

### GET `/api/v1/mypage/`

마이페이지 요약.

Response `200`:

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "neutripic_user",
    "age": 30,
    "gender": "female"
  },
  "report_count": 3,
  "post_count": 5,
  "comment_count": 12
}
```

## 4. Survey Metadata

### GET `/api/v1/health_goals/`

건강 목표 선택지 조회.

Response `200`:

```json
[
  {
    "code": "fatigue",
    "name": "피로"
  },
  {
    "code": "sleep",
    "name": "수면"
  }
]
```

### GET `/api/v1/medication_options/`

대표 복용 약 선택지 조회.

Response `200`:

```json
[
  {
    "code": "anticoagulant",
    "name": "항응고제"
  }
]
```

### GET `/api/v1/special_condition_options/`

특이사항 선택지 조회.

Response `200`:

```json
[
  {
    "code": "pregnancy_or_lactation",
    "name": "임신 또는 수유"
  }
]
```

## 5. AI Reports

### POST `/api/v1/reports/`

AI 추천 리포트 생성을 요청한다.

백엔드는 요청을 검증하고 사용량 제한을 확인한 뒤 AI 서버를 내부 호출한다. AI 서버가 추가 확인 질문이 필요하다고 판단하면 리포트 대신 확인 질문을 반환할 수 있다.

Request:

```json
{
  "age": 30,
  "gender": "female",
  "health_goals": [
    {
      "code": "fatigue",
      "priority": 1
    },
    {
      "code": "sleep",
      "priority": 2
    }
  ],
  "medications": [
    {
      "code": "anticoagulant",
      "name": "항응고제"
    }
  ],
  "special_conditions": [
    {
      "code": "allergy",
      "name": "알레르기"
    }
  ],
  "additional_notes": "카페인을 먹으면 심장이 두근거립니다."
}
```

Response `201`:

```json
{
  "id": 10,
  "status": "completed",
  "title": "피로와 수면 개선을 위한 성분 리포트",
  "input_summary": {
    "age": 30,
    "gender": "female",
    "health_goals": ["피로", "수면"],
    "medications": ["항응고제"],
    "special_conditions": ["알레르기"],
    "additional_notes": "카페인을 먹으면 심장이 두근거립니다."
  },
  "recommended_ingredients": [
    {
      "name_ko": "마그네슘",
      "name_en": "Magnesium",
      "normalized_name": "magnesium",
      "reason": "수면과 근육 이완 관련 기능성 근거가 있어 후보로 선정되었습니다.",
      "expected_effects": ["수면 질 관리", "근육 기능 유지"],
      "recommended_dosage": "기능성 원료 인정현황 기준 범위 내에서 섭취하세요.",
      "side_effects": ["설사", "복부 불편감"],
      "precautions": ["신장 질환이 있는 경우 전문가와 상담하세요."],
      "iherb_url": "https://kr.iherb.com/c/minerals"
    }
  ],
  "lifestyle_tips": [
    "카페인 섭취 시간과 양을 조절해 보세요."
  ],
  "disclaimer": "질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.",
  "citations": [
    {
      "source_type": "functional_ingredient",
      "source_name": "건강기능식품 기능성원료 인정현황",
      "document_id": "functional_ingredient_magnesium"
    }
  ],
  "created_at": "2026-06-22T12:00:00+09:00"
}
```

Response `200` when clarification is required:

```json
{
  "status": "needs_clarification",
  "questions": [
    {
      "code": "medication_detail_required",
      "message": "복용 중인 항응고제 이름을 입력해 주세요."
    }
  ]
}
```

### GET `/api/v1/reports/`

내 추천 기록 목록 조회.

Query parameters:

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | integer | no | 페이지 번호 |
| `page_size` | integer | no | 페이지 크기 |

Response `200`:

```json
{
  "count": 3,
  "results": [
    {
      "id": 10,
      "title": "피로와 수면 개선을 위한 성분 리포트",
      "status": "completed",
      "created_at": "2026-06-22T12:00:00+09:00"
    }
  ]
}
```

### GET `/api/v1/reports/{report_id}/`

추천 기록 상세 조회.

Response `200`: `POST /api/v1/reports/`의 리포트 응답과 동일한 상세 구조

### PATCH `/api/v1/reports/{report_id}/`

추천 기록 제목 수정.

Request:

```json
{
  "title": "수면 관리 리포트"
}
```

Response `200`:

```json
{
  "id": 10,
  "title": "수면 관리 리포트"
}
```

### DELETE `/api/v1/reports/{report_id}/`

추천 기록 삭제.

Response `204`

## 6. Report Chat

### GET `/api/v1/reports/{report_id}/messages/`

리포트 기반 채팅 내역 조회.

Response `200`:

```json
[
  {
    "id": 100,
    "role": "user",
    "content": "마그네슘은 언제 먹는 게 좋나요?",
    "created_at": "2026-06-22T12:10:00+09:00"
  },
  {
    "id": 101,
    "role": "assistant",
    "content": "일반적으로 저녁 식후 섭취를 고려할 수 있지만...",
    "citations": [],
    "created_at": "2026-06-22T12:10:05+09:00"
  }
]
```

### POST `/api/v1/reports/{report_id}/messages/`

리포트 기반 후속 질문.

Request:

```json
{
  "content": "마그네슘은 언제 먹는 게 좋나요?"
}
```

Response `201`:

```json
{
  "id": 101,
  "role": "assistant",
  "content": "일반적으로 저녁 식후 섭취를 고려할 수 있습니다. 다만 질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.",
  "guardrail_result": {
    "is_allowed": true,
    "risk_level": "low"
  },
  "citations": [
    {
      "source_type": "functional_ingredient",
      "source_name": "건강기능식품 기능성원료 인정현황",
      "document_id": "functional_ingredient_magnesium"
    }
  ],
  "created_at": "2026-06-22T12:10:05+09:00"
}
```

## 7. Community Posts

### GET `/api/v1/posts/`

게시글 목록 조회. 비회원도 조회 가능하다.

`ordering=latest`는 인피니트 스크롤을 위해 cursor pagination을 사용한다.
`ordering=likes`는 좋아요 수가 변동 가능한 값이므로 기존 page number pagination을 유지한다.

Query parameters:

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `ordering` | string | no | `latest`, `likes`. 기본값은 `latest` |
| `cursor` | string | no | `ordering=latest`에서 사용하는 다음/이전 페이지 커서 |
| `page` | integer | no | `ordering=likes`에서 사용하는 페이지 번호 |
| `page_size` | integer | no | 페이지 크기 |

Response `200` for `ordering=latest`:

```json
{
  "next": "https://example.com/api/v1/posts/?cursor=cD0yMDI2LTA2LTIzKzEyJTNBMDA%3D&page_size=10",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "수면 관리 루틴 공유합니다",
      "author": {
        "id": 1,
        "username": "neutripic_user"
      },
      "like_count": 3,
      "comment_count": 2,
      "created_at": "2026-06-22T12:00:00+09:00"
    }
  ]
}
```

Response `200` for `ordering=likes`:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "수면 관리 루틴 공유합니다",
      "author": {
        "id": 1,
        "username": "neutripic_user"
      },
      "like_count": 3,
      "comment_count": 2,
      "created_at": "2026-06-22T12:00:00+09:00"
    }
  ]
}
```

### POST `/api/v1/posts/`

게시글 작성.

Request:

```json
{
  "title": "수면 관리 루틴 공유합니다",
  "content": "최근에 수면 시간을 고정해 보고 있습니다."
}
```

Response `201`: 생성된 게시글

### GET `/api/v1/posts/{post_id}/`

게시글 상세 조회.

### PATCH `/api/v1/posts/{post_id}/`

게시글 수정.

Request:

```json
{
  "title": "수면 관리 루틴 수정",
  "content": "수정된 내용입니다."
}
```

### DELETE `/api/v1/posts/{post_id}/`

게시글 삭제.

Response `204`

### POST `/api/v1/posts/{post_id}/like/`

게시글 추천.

Response `200`:

```json
{
  "post_id": 1,
  "is_liked": true,
  "like_count": 4
}
```

### DELETE `/api/v1/posts/{post_id}/like/`

게시글 추천 취소.

Response `200`:

```json
{
  "post_id": 1,
  "is_liked": false,
  "like_count": 3
}
```

## 8. Comments And Replies

### GET `/api/v1/posts/{post_id}/comments/`

댓글과 답글 목록 조회.

### POST `/api/v1/posts/{post_id}/comments/`

댓글 또는 답글 작성.

Request:

```json
{
  "content": "좋은 공유 감사합니다.",
  "parent_id": null
}
```

Response `201`: 생성된 댓글

### PATCH `/api/v1/comments/{comment_id}/`

댓글 또는 답글 수정.

Request:

```json
{
  "content": "수정된 댓글입니다."
}
```

Response `200`: 수정된 댓글

### DELETE `/api/v1/comments/{comment_id}/`

댓글 또는 답글 삭제.

Response `204`

## 9. Admin

관리자 API는 `role=admin` 사용자만 접근할 수 있다.

### GET `/api/v1/admin/users/`

회원 목록 조회.

### GET `/api/v1/admin/users/{user_id}/`

회원 상세 조회.

### PATCH `/api/v1/admin/users/{user_id}/`

회원 상태 수정.

Request:

```json
{
  "is_active": false
}
```

### GET `/api/v1/admin/posts/`

전체 게시글 관리 목록 조회.

### DELETE `/api/v1/admin/posts/{post_id}/`

관리자 게시글 삭제.

### GET `/api/v1/admin/comments/`

전체 댓글 및 답글 관리 목록 조회.

### DELETE `/api/v1/admin/comments/{comment_id}/`

관리자 댓글 또는 답글 삭제.

### GET `/api/v1/admin/reports/statistics/`

추천 기록 통계 조회.

Response `200`:

```json
{
  "report_count": 120,
  "popular_health_goals": [
    {
      "code": "fatigue",
      "name": "피로",
      "count": 45
    }
  ],
  "popular_ingredients": [
    {
      "normalized_name": "magnesium",
      "name_ko": "마그네슘",
      "count": 30
    }
  ]
}
```

## 10. Backend Responsibilities

| Concern | Backend Responsibility |
| --- | --- |
| JWT 인증 | access token 검증 |
| 사용자 권한 | 본인 리소스와 관리자 권한 검증 |
| 사용자별 데이터 저장 | 회원, 리포트, 채팅, 게시글, 댓글 저장 |
| 사용량 제한 | 리포트 생성과 채팅 사용량 최종 판정 |
| 설문 입력 검증 | 필수 값, 최대 건강 목표 5개, 우선순위 검증 |
| AI 호출 | AI 서버 내부 API 호출 및 실패 처리 |
| iHerb 링크 매핑 | 서버 저장 매핑 테이블의 허용 URL만 노출 |
| 커뮤니티 | 게시글, 댓글, 답글, 추천 처리 |
| 관리자 기능 | 회원, 게시글, 댓글, 통계 관리 |

## 11. Report Generation Sequence

```text
1. Frontend -> Backend
   POST /api/v1/reports/

2. Backend
   - JWT 검증
   - 요청 필드 검증
   - 사용자별 사용량 제한 확인

3. Backend -> AI Server
   - input guardrail
   - normalize
   - rag search
   - report generate
   - output guardrail

4. Backend
   - 추천 성분 iHerb 링크 매핑
   - 리포트 저장
   - 사용량 차감

5. Backend -> Frontend
   201 Created
```

## 12. Open Decisions

- JWT refresh token 저장 및 폐기 방식
- 회원 탈퇴 시 추천 기록과 커뮤니티 글의 보존 또는 익명화 정책
- 리포트 생성 사용량 제한 수치
- 채팅 사용량 제한 수치
- 건강 목표, 복용 약, 특이사항 선택지의 최종 코드 목록
- iHerb 링크 매핑 테이블의 관리자 편집 여부
- 관리자 통계 API의 기간 필터와 집계 기준
