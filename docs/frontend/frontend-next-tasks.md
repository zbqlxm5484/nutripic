# Frontend Next Tasks

이 문서는 현재 `frontend/` 구현 상태를 기준으로 다음 agent가 이어서 작업할 우선순위 체크리스트이다.

현재 프론트엔드는 페이지 구조, 도메인별 라우트, 공용 레이아웃/폼/상태 컴포넌트의 1차 골격이 잡혀 있다. 다음 단계는 정적 화면을 실제 기능과 백엔드 API 계약에 연결하는 것이다.

## 1. 공통 API 레이어 구축

Priority: High

Status: Done

### Goal

백엔드 `/api/v1/` API를 호출하는 공통 client를 만들고, 인증 토큰과 표준 에러 응답 처리를 한 곳에서 관리한다.

### Checklist

- [x] `frontend/src/shared/api/` 또는 `frontend/src/app/api/` 위치를 정한다.
- [x] 공통 `apiClient`를 만든다.
- [x] base URL을 `/api/v1/`로 관리한다.
- [x] JSON request/response 처리를 공통화한다.
- [x] JWT access token이 있으면 `Authorization: Bearer {access_token}` 헤더를 자동 첨부한다.
- [x] `204 No Content` 응답을 안전하게 처리한다.
- [x] 표준 에러 응답의 `error_code`, `message`, `details`를 페이지에서 쓰기 쉬운 형태로 정규화한다.
- [x] 네트워크 오류와 서버 오류를 구분해 반환한다.

### Success Criteria

- 로그인 API를 공통 client로 호출할 수 있다.
- 같은 에러 처리 함수를 인증, 설문, 리포트, 커뮤니티 페이지에서 재사용할 수 있다.
- 페이지 컴포넌트 안에 `fetch` 옵션과 토큰 헤더 조립 로직이 반복되지 않는다.

### Related APIs

- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/signup/`
- `POST /api/v1/auth/token/refresh/`
- 전체 API 공통 에러 응답

### Related Files

- `frontend/src/main.js`
- `frontend/src/app/router.js`
- `frontend/src/shared/components/status/FormErrorMessage.vue`
- `docs/api/backend-api-spec.md`

## 2. 인증 상태와 라우터 가드 구현

Priority: High

Status: Done

### Goal

로그인 상태를 전역에서 확인할 수 있게 만들고, 인증/관리자 권한이 필요한 라우트를 보호한다.

### Checklist

- [x] auth 상태 모듈 또는 composable 위치를 정한다.
- [x] access token, refresh token, user 정보를 저장하고 읽는 함수를 만든다.
- [x] 로그인 성공 시 토큰과 사용자 정보를 저장한다.
- [x] 로그아웃 시 저장된 인증 정보를 제거한다.
- [x] `/login?redirect_to=...` 복귀 흐름을 구현한다.
- [x] 인증 필요 라우트에 `meta.requiresAuth`를 추가한다.
- [x] 관리자 라우트에 `meta.requiresAdmin`을 추가한다.
- [x] `router.beforeEach`에서 인증/관리자 접근을 검사한다.
- [x] 로그인 사용자가 `/login`, `/signup`에 접근했을 때의 이동 정책을 정한다.

### Success Criteria

- 비로그인 사용자가 `/survey`에 접근하면 `/login?redirect_to=/survey`로 이동한다.
- 로그인 후 원래 접근하려던 경로로 돌아간다.
- 일반 사용자가 `/admin`에 접근하면 권한 없음 흐름으로 이동하거나 안내를 본다.
- 인증 상태 확인 로직이 페이지별로 중복되지 않는다.

### Related APIs

- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/logout/`
- `POST /api/v1/auth/token/refresh/`
- `GET /api/v1/users/me/`

### Related Files

- `frontend/src/app/router.js`
- `frontend/src/domains/auth/routes.js`
- `frontend/src/domains/survey/routes.js`
- `frontend/src/domains/reports/routes.js`
- `frontend/src/domains/mypage/routes.js`
- `frontend/src/domains/community/routes.js`
- `frontend/src/domains/admin/routes.js`
- `frontend/src/domains/auth/pages/LoginPage.vue`
- `frontend/src/domains/auth/pages/SignupPage.vue`

## 3. 인증 페이지 API 연결

Priority: High

Status: Done

### Goal

로그인과 회원가입 폼을 실제 백엔드 API에 연결하고, 제출 중/성공/실패 상태를 화면에 반영한다.

### Checklist

- [x] 로그인 폼 입력 상태를 Vue state로 연결한다.
- [x] 회원가입 폼 입력 상태를 Vue state로 연결한다.
- [x] 클라이언트 필수값 검증을 추가한다.
- [x] 로그인 submit에서 `POST /auth/login/`을 호출한다.
- [x] 회원가입 submit에서 `POST /auth/signup/`을 호출한다.
- [x] 제출 중 버튼 disabled 상태를 적용한다.
- [x] API 에러 메시지를 `FormErrorMessage`로 표시한다.
- [x] 로그인 성공 후 `redirect_to` 또는 `/`로 이동한다.
- [x] 회원가입 성공 후 정책에 따라 `/survey` 또는 `/login`으로 이동한다.

### Success Criteria

- 올바른 계정으로 로그인하면 인증 정보가 저장되고 다음 페이지로 이동한다.
- 잘못된 입력이나 인증 실패가 사용자에게 명확히 표시된다.
- 폼 제출 중 중복 제출이 막힌다.

### Related APIs

- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/signup/`

### Related Files

- `frontend/src/domains/auth/pages/LoginPage.vue`
- `frontend/src/domains/auth/pages/SignupPage.vue`
- `frontend/src/shared/components/form/BaseForm.vue`
- `frontend/src/shared/components/form/FormField.vue`
- `frontend/src/shared/components/status/FormErrorMessage.vue`

## 4. 설문 선택지 조회와 입력 상태 구현

Priority: High

Status: Pending

### Goal

현재 정적 배열로 표시되는 설문 선택지를 백엔드 메타데이터 API에서 가져오고, 리포트 생성 request 형식에 맞는 설문 상태를 구성한다.

### Checklist

- [ ] 건강 목표 선택지를 API에서 조회한다.
- [ ] 복용 약 선택지를 API에서 조회한다.
- [ ] 특이사항 선택지를 API에서 조회한다.
- [ ] 선택지 로딩, 실패, 빈 상태를 처리한다.
- [ ] 건강 목표 1개 이상, 최대 5개 검증을 구현한다.
- [ ] 선택한 건강 목표의 우선순위 상태를 구현한다.
- [ ] 복용 약과 특이사항 선택 상태를 구현한다.
- [ ] 추가 입력 값을 `additional_notes` request field로 연결한다.
- [ ] 설문 request payload를 백엔드 명세의 snake_case 형식에 맞춘다.

### Success Criteria

- 설문 선택지가 백엔드 API 응답으로 렌더링된다.
- 건강 목표를 6개 이상 선택할 수 없다.
- 선택한 목표의 우선순위가 중복 없이 request payload에 포함된다.
- 설문 페이지가 새로고침되어도 최소한 오류 없이 초기 상태를 복구한다.

### Related APIs

- `GET /api/v1/health_goals/`
- `GET /api/v1/medication_options/`
- `GET /api/v1/special_condition_options/`
- `POST /api/v1/reports/`

### Related Files

- `frontend/src/domains/survey/pages/SurveyPage.vue`
- `frontend/src/shared/components/layout/SurveyLayout.vue`
- `frontend/src/shared/components/status/SafetyNotice.vue`
- `docs/api/backend-api-spec.md`

## 5. 리포트 생성 플로우 연결

Priority: High

Status: Pending

### Goal

설문 제출 시 백엔드에 리포트 생성을 요청하고, 성공/추가 확인/실패 흐름을 사용자에게 명확히 보여준다.

### Checklist

- [ ] 설문 submit에서 `POST /api/v1/reports/`를 호출한다.
- [ ] `201 Created` 리포트 응답을 저장하거나 다음 페이지로 전달하는 방식을 정한다.
- [ ] 생성 성공 시 `/reports/new` 또는 `/reports/:report_id`로 이동한다.
- [ ] `needs_clarification` 응답을 설문 화면에 표시한다.
- [ ] 사용량 제한, 검증 실패, AI 서버 실패 메시지를 구분해 표시한다.
- [ ] `/reports/generating` 화면의 역할을 확정한다.
- [ ] 실제 비동기 job API가 없으면 단계형 대기 화면 대신 제출 중 상태 중심으로 단순화할지 결정한다.

### Success Criteria

- 설문을 제출하면 백엔드 리포트 생성 API가 호출된다.
- 추가 확인 질문이 필요한 경우 리포트 화면으로 이동하지 않고 질문을 표시한다.
- 생성 실패 시 재시도 또는 설문 수정 액션이 제공된다.
- 성공 후 사용자가 생성된 리포트 내용을 확인할 수 있다.

### Related APIs

- `POST /api/v1/reports/`

### Related Files

- `frontend/src/domains/survey/pages/SurveyPage.vue`
- `frontend/src/domains/reports/pages/ReportGeneratingPage.vue`
- `frontend/src/domains/reports/pages/ReportNewPage.vue`
- `frontend/src/domains/reports/routes.js`

## 6. 리포트 목록, 상세, 수정, 삭제 연결

Priority: Medium

Status: Pending

### Goal

저장된 추천 기록을 조회하고, 상세 확인, 제목 수정, 삭제 액션을 실제 API와 연결한다.

### Checklist

- [ ] 추천 기록 목록을 조회한다.
- [ ] 목록 로딩, 빈 목록, 조회 실패 상태를 표시한다.
- [ ] 리포트 상세를 `report_id` 기준으로 조회한다.
- [ ] 리포트 상세의 입력 요약, 추천 성분, 생활 팁, 출처, 면책 문구를 렌더링한다.
- [ ] `iherb_url`이 있는 성분만 외부 링크를 표시한다.
- [ ] 제목 수정 API를 연결한다.
- [ ] 삭제 API를 연결하고 성공 후 목록으로 이동한다.
- [ ] 삭제 전 확인 UI를 추가한다.

### Success Criteria

- `/reports`에서 저장된 리포트 목록이 보인다.
- `/reports/:report_id`에서 백엔드 응답 구조대로 상세가 렌더링된다.
- iHerb 상품명, 이미지, 가격, 리뷰는 표시하지 않는다.
- 제목 수정과 삭제 후 화면 상태가 API 결과와 일치한다.

### Related APIs

- `GET /api/v1/reports/`
- `GET /api/v1/reports/{report_id}/`
- `PATCH /api/v1/reports/{report_id}/`
- `DELETE /api/v1/reports/{report_id}/`

### Related Files

- `frontend/src/domains/reports/pages/ReportsPage.vue`
- `frontend/src/domains/reports/pages/ReportDetailPage.vue`
- `frontend/src/domains/reports/pages/ReportNewPage.vue`
- `frontend/src/shared/components/layout/ReportLayout.vue`
- `frontend/src/shared/components/status/MedicalDisclaimer.vue`

## 7. 리포트 기반 채팅 연결

Priority: Medium

Status: Pending

### Goal

리포트 상세에서 기존 채팅 내역을 조회하고, 사용자의 후속 질문을 백엔드에 전송한다.

### Checklist

- [ ] `ReportChatPanel`을 입력 값과 submit 이벤트를 받을 수 있게 확장한다.
- [ ] 메시지 목록 조회 API를 연결한다.
- [ ] 질문 전송 API를 연결한다.
- [ ] 전송 중 상태와 중복 제출 방지를 구현한다.
- [ ] assistant 응답의 citations와 guardrail 결과 표시 정책을 정한다.
- [ ] 채팅 사용량 제한 또는 가드레일 차단 오류를 표시한다.

### Success Criteria

- 리포트 상세 진입 시 기존 메시지가 보인다.
- 질문을 보내면 사용자 메시지와 assistant 응답이 화면에 반영된다.
- 채팅 범위를 벗어난 요청이나 제한 오류가 명확히 안내된다.

### Related APIs

- `GET /api/v1/reports/{report_id}/messages/`
- `POST /api/v1/reports/{report_id}/messages/`

### Related Files

- `frontend/src/shared/components/chat/ReportChatPanel.vue`
- `frontend/src/domains/reports/pages/ReportDetailPage.vue`
- `frontend/src/domains/reports/pages/ReportNewPage.vue`

## 8. 커뮤니티 목록과 상세 조회 연결

Priority: Medium

Status: Pending

### Goal

비회원도 접근 가능한 커뮤니티 목록/상세 조회를 먼저 API와 연결한다.

### Checklist

- [ ] 게시글 목록 조회 API를 연결한다.
- [ ] 최신순/추천순 정렬 query를 연결한다.
- [ ] 페이지네이션 정책을 정한다.
- [ ] 목록 로딩, 빈 목록, 실패 상태를 표시한다.
- [ ] 게시글 상세 조회 API를 연결한다.
- [ ] 댓글/답글 목록 조회 API를 연결한다.

### Success Criteria

- 비로그인 사용자가 `/community`와 `/community/:post_id`를 조회할 수 있다.
- 정렬 변경 시 API query와 화면 목록이 함께 변경된다.
- 목록/상세 실패 시 재시도 가능한 오류 상태가 보인다.

### Related APIs

- `GET /api/v1/posts/`
- `GET /api/v1/posts/{post_id}/`
- `GET /api/v1/posts/{post_id}/comments/`

### Related Files

- `frontend/src/domains/community/pages/CommunityPage.vue`
- `frontend/src/domains/community/pages/CommunityDetailPage.vue`
- `frontend/src/domains/community/routes.js`
- `frontend/src/shared/components/status/EmptyState.vue`
- `frontend/src/shared/components/status/ErrorState.vue`
- `frontend/src/shared/components/status/LoadingState.vue`

## 9. 커뮤니티 작성, 수정, 삭제, 추천, 댓글 연결

Priority: Medium

Status: Pending

### Goal

로그인 사용자의 커뮤니티 액션을 실제 API와 연결하고 권한 없는 액션은 로그인 또는 오류 안내로 보낸다.

### Checklist

- [ ] 게시글 작성 API를 연결한다.
- [ ] 게시글 수정 API를 연결한다.
- [ ] 게시글 삭제 API를 연결한다.
- [ ] 게시글 추천/추천 취소 API를 연결한다.
- [ ] 댓글/답글 작성 API를 연결한다.
- [ ] 댓글/답글 수정 API를 연결한다.
- [ ] 댓글/답글 삭제 API를 연결한다.
- [ ] 비로그인 액션 시 `/login?redirect_to=...` 이동을 적용한다.
- [ ] 본인 글/댓글이 아닌 경우 수정/삭제 액션 노출 정책을 정한다.

### Success Criteria

- 로그인 사용자가 게시글과 댓글을 작성할 수 있다.
- 작성/수정 성공 후 상세 화면에 최신 데이터가 보인다.
- 비로그인 사용자가 작성 액션을 시도하면 로그인 후 복귀한다.
- 권한 없음 응답이 사용자에게 명확히 표시된다.

### Related APIs

- `POST /api/v1/posts/`
- `PATCH /api/v1/posts/{post_id}/`
- `DELETE /api/v1/posts/{post_id}/`
- `POST /api/v1/posts/{post_id}/like/`
- `DELETE /api/v1/posts/{post_id}/like/`
- `POST /api/v1/posts/{post_id}/comments/`
- `PATCH /api/v1/comments/{comment_id}/`
- `DELETE /api/v1/comments/{comment_id}/`

### Related Files

- `frontend/src/domains/community/pages/CommunityFormPage.vue`
- `frontend/src/domains/community/pages/CommunityNewPage.vue`
- `frontend/src/domains/community/pages/CommunityEditPage.vue`
- `frontend/src/domains/community/pages/CommunityDetailPage.vue`
- `frontend/src/domains/community/pages/CommunityPage.vue`

## 10. 마이페이지와 회원 정보 수정 연결

Priority: Low

Status: Pending

### Goal

내 정보, 활동 요약, 회원 정보 수정, 비밀번호 변경, 회원 탈퇴 흐름을 API와 연결한다.

### Checklist

- [ ] 마이페이지 요약 API를 연결한다.
- [ ] 내 회원 정보 조회 API를 연결한다.
- [ ] 회원 정보 수정 API를 연결한다.
- [ ] 비밀번호 변경 API를 연결한다.
- [ ] 회원 탈퇴 API를 연결한다.
- [ ] 탈퇴 전 확인 UI와 성공 후 로그아웃 처리를 구현한다.

### Success Criteria

- `/mypage`에서 내 정보와 활동 요약이 보인다.
- `/mypage/profile`에서 회원 정보를 수정할 수 있다.
- 비밀번호 변경과 회원 탈퇴 결과가 명확히 안내된다.

### Related APIs

- `GET /api/v1/mypage/`
- `GET /api/v1/users/me/`
- `PATCH /api/v1/users/me/`
- `PATCH /api/v1/users/me/password/`
- `DELETE /api/v1/users/me/`

### Related Files

- `frontend/src/domains/mypage/pages/MyPage.vue`
- `frontend/src/domains/mypage/pages/ProfilePage.vue`
- `frontend/src/domains/mypage/routes.js`

## 11. 관리자 화면 API 연결

Priority: Low

Status: Pending

### Goal

관리자 권한 사용자가 회원, 게시글, 댓글을 조회하고 필요한 관리 액션을 수행할 수 있게 한다.

### Checklist

- [ ] 관리자 라우트 접근 권한을 검사한다.
- [ ] 회원 목록 조회 API를 연결한다.
- [ ] 회원 상태 수정 API를 연결한다.
- [ ] 관리자 게시글 목록 조회 API를 연결한다.
- [ ] 관리자 게시글 삭제 API를 연결한다.
- [ ] 관리자 댓글 목록 조회 API를 연결한다.
- [ ] 관리자 댓글 삭제 API를 연결한다.
- [ ] 권한 없음, 로딩, 실패, 삭제 확인 상태를 표시한다.

### Success Criteria

- 관리자만 `/admin` 하위 페이지에 접근할 수 있다.
- 관리자 페이지의 테이블 데이터가 API 응답으로 채워진다.
- 삭제 또는 상태 변경 후 목록이 최신 상태로 갱신된다.

### Related APIs

- `GET /api/v1/admin/users/`
- `GET /api/v1/admin/users/{user_id}/`
- `PATCH /api/v1/admin/users/{user_id}/`
- `GET /api/v1/admin/posts/`
- `DELETE /api/v1/admin/posts/{post_id}/`
- `GET /api/v1/admin/comments/`
- `DELETE /api/v1/admin/comments/{comment_id}/`
- `GET /api/v1/admin/reports/statistics/`

### Related Files

- `frontend/src/domains/admin/pages/AdminPage.vue`
- `frontend/src/domains/admin/pages/AdminUsersPage.vue`
- `frontend/src/domains/admin/pages/AdminPostsPage.vue`
- `frontend/src/domains/admin/pages/AdminCommentsPage.vue`
- `frontend/src/domains/admin/routes.js`
- `frontend/src/shared/components/data/AdminTablePanel.vue`

## Suggested Implementation Order

1. 공통 API 레이어
2. 인증 상태와 라우터 가드
3. 로그인/회원가입 API 연결
4. 설문 선택지 조회와 입력 상태
5. 리포트 생성 플로우
6. 리포트 목록/상세/채팅
7. 커뮤니티 조회
8. 커뮤니티 작성/댓글/추천
9. 마이페이지
10. 관리자

## Verification Checklist

- [ ] `npm run build`가 성공한다.
- [ ] 비로그인 보호 라우트 접근 시 로그인 페이지로 이동한다.
- [ ] 로그인 성공 후 `redirect_to` 경로로 복귀한다.
- [ ] 백엔드 API request/response field는 snake_case를 유지한다.
- [ ] API 에러 응답은 모든 페이지에서 일관된 메시지로 표시된다.
- [ ] 리포트 화면에서 iHerb 상품 정보는 표시하지 않고 검증된 성분 링크만 표시한다.
