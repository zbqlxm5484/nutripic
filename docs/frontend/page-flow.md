# Page Flow

이 문서는 `docs/common/development.md`의 MVP 범위를 기준으로 프론트엔드 페이지, 라우트, 인증 조건, 페이지 이동 흐름을 상세화한다. 백엔드 API 계약이 확정되기 전까지는 라우트와 필드명을 작업 기준안으로 사용하며, API 경계의 request/response field는 Django 백엔드 규칙에 맞춰 snake_case를 따른다.

## 1. 설계 원칙

- 뉴트리픽은 상품 추천 서비스가 아니라 성분 중심 AI 리포트 서비스이다.
- 서비스 내부에서 iHerb 상품명, 이미지, 가격, 리뷰, 판매자 정보는 표시하지 않는다.
- iHerb 연동은 백엔드가 검증한 성분 링크만 외부 링크로 제공한다.
- 비회원은 홈과 커뮤니티 목록/상세 조회만 가능하다.
- AI 추천, 리포트 저장/조회, 리포트 채팅, 게시글/댓글 작성은 로그인 상태를 요구한다.
- 의료 고지 문구는 설문, 리포트, 채팅 화면에서 반복적으로 확인 가능해야 한다.

## 2. 페이지 목록

| Page | Route | Auth | 주요 목적 |
| --- | --- | --- | --- |
| 홈 | `/` | 선택 | 서비스 소개, 추천 시작, 커뮤니티 진입 |
| 회원가입 | `/signup` | 비로그인 | 계정 생성 |
| 로그인 | `/login` | 비로그인 | JWT 인증 |
| 추천 설문 시작 | `/survey` | 필요 | 건강 목표, 복용 약, 특이사항 입력 |
| 리포트 생성 대기 | `/reports/generating` | 필요 | RAG/AI 리포트 생성 진행 상태 표시 |
| 신규 리포트 결과 | `/reports/new` | 필요 | 방금 생성된 리포트와 채팅 진입 표시 |
| 추천 기록 목록 | `/reports` | 필요 | 저장된 리포트 목록 조회 |
| 리포트 상세 | `/reports/:report_id` | 필요 | 저장 리포트 상세와 리포트 기반 채팅 |
| 마이페이지 | `/mypage` | 필요 | 회원 정보, 추천 기록, 내 게시글/댓글 조회 |
| 회원 정보 수정 | `/mypage/profile` | 필요 | 나이, 성별, 비밀번호 등 수정 |
| 커뮤니티 목록 | `/community` | 선택 | 게시글 목록, 정렬, 검색 |
| 커뮤니티 상세 | `/community/:post_id` | 선택 | 게시글, 댓글, 답글 조회 |
| 게시글 작성 | `/community/new` | 필요 | 게시글 작성 |
| 게시글 수정 | `/community/:post_id/edit` | 필요 | 본인 게시글 수정 |
| 관리자 대시보드 | `/admin` | 관리자 | 회원, 게시글, 댓글 관리 |
| 관리자 회원 관리 | `/admin/users` | 관리자 | 회원 목록/상태 관리 |
| 관리자 게시글 관리 | `/admin/posts` | 관리자 | 게시글 조회/삭제 |
| 관리자 댓글 관리 | `/admin/comments` | 관리자 | 댓글/답글 조회/삭제 |

## 3. 전체 이동 흐름

```text
/
  -> /signup
  -> /login
  -> /survey
  -> /community

/signup
  -> /survey
  -> /login

/login
  -> redirect_to
  -> /

/survey
  -> /reports/generating
  -> /

/reports/generating
  -> /reports/new
  -> /survey

/reports/new
  -> /reports/:report_id
  -> /reports
  -> /survey

/reports
  -> /reports/:report_id
  -> /survey

/reports/:report_id
  -> /reports
  -> /survey

/mypage
  -> /mypage/profile
  -> /reports
  -> /reports/:report_id
  -> /community/:post_id

/community
  -> /community/:post_id
  -> /community/new
  -> /login

/community/:post_id
  -> /community/:post_id/edit
  -> /login
  -> /community

/admin
  -> /admin/users
  -> /admin/posts
  -> /admin/comments
```

## 4. 추천 리포트 핵심 플로우

```text
로그인 사용자
  -> 추천 설문 시작
  -> 건강 목표 최대 5개 선택
  -> 목표 우선순위 지정
  -> 복용 약 선택
  -> 특이사항 선택
  -> 추가 정보 자유 입력
  -> 입력 검증 및 의료 고지 확인
  -> 리포트 생성 요청
  -> 생성 대기 화면
  -> 신규 리포트 결과
  -> 리포트 기반 채팅
  -> 추천 기록 목록 또는 상세 재조회
```

예외 흐름:

- 사용량 제한 초과: 리포트 생성 요청을 막고 제한 안내를 표시한다.
- 가드레일 차단: 안전 안내 또는 추가 확인 질문을 표시하고 리포트 생성 상태로 이동하지 않는다.
- RAG/AI 실패: 생성 대기 화면에서 실패 상태와 재시도/설문 수정 CTA를 제공한다.
- 성분 링크 없음: 성분명만 표시하고 iHerb 외부 링크는 노출하지 않는다.

## 5. 페이지별 상세

### 5.1 홈

Route: `/`

역할:

- 뉴트리픽의 성분 중심 리포트 가치를 전달한다.
- 추천 설문, 로그인/회원가입, 커뮤니티로 진입시킨다.
- 비회원도 접근 가능하지만 추천 시작 시 인증이 필요함을 안내한다.

주요 컴포넌트:

- `AppHeader`
- `HeroSection`
- `PrimaryCta`
- `ServiceValueSection`
- `SafetyNotice`
- `CommunityPreview`
- `AppFooter`

상태:

- 비로그인: 추천 시작 클릭 시 `/login?redirect_to=/survey`
- 로그인: 추천 시작 클릭 시 `/survey`

### 5.2 회원가입

Route: `/signup`

역할:

- 아이디 또는 이메일, 비밀번호, 나이, 성별을 입력받아 계정을 생성한다.

주요 컴포넌트:

- `AuthLayout`
- `SignupForm`
- `PasswordField`
- `AgeInput`
- `GenderSelect`
- `FormErrorMessage`

검증:

- 필수값 누락
- 이메일 또는 아이디 형식
- 비밀번호 확인 일치
- 나이 허용 범위

이동:

- 가입 성공 -> `/survey`
- 이미 계정이 있음 -> `/login`

### 5.3 로그인

Route: `/login`

역할:

- 아이디 또는 이메일과 비밀번호로 로그인한다.
- 인증 성공 시 JWT를 저장하고 이전 의도 페이지로 이동한다.

주요 컴포넌트:

- `AuthLayout`
- `LoginForm`
- `PasswordField`
- `FormErrorMessage`
- `RedirectNotice`

이동:

- 로그인 성공 -> `redirect_to` 또는 `/`
- 회원가입 -> `/signup`

### 5.4 추천 설문

Route: `/survey`

Auth: 필요

역할:

- 건강 목표, 우선순위, 복용 약, 특이사항, 추가 정보를 입력받는다.
- 리포트 생성 전 입력 검증과 안전 안내 확인을 수행한다.

주요 컴포넌트:

- `SurveyLayout`
- `SurveyProgress`
- `HealthGoalSelector`
- `GoalPriorityList`
- `MedicationSelector`
- `SpecialConditionSelector`
- `AdditionalInfoTextarea`
- `UsageLimitBanner`
- `SafetyNotice`
- `SurveyActionBar`

입력:

- 건강 목표: 최대 5개
- 목표 우선순위: 선택한 목표 기준 1순위부터 5순위
- 복용 약: 대표 약물 분류 다중 선택
- 특이사항: 임신/수유, 간 질환, 신장 질환, 심혈관 질환, 알레르기, 수술 예정 등 다중 선택
- 추가 정보: 선택지에 없는 복용 약, 질환, 알레르기, 생활 습관

상태:

- 입력 중
- 필수값 누락
- 최대 선택 개수 초과
- 사용량 제한 초과
- 가드레일 차단
- 추가 확인 질문 필요
- 제출 중

이동:

- 생성 요청 성공 -> `/reports/generating`
- 취소 -> `/`

### 5.5 리포트 생성 대기

Route: `/reports/generating`

Auth: 필요

역할:

- 백엔드의 입력 정규화, RAG 검색, LangChain 리포트 생성 진행 상태를 보여준다.
- 사용자가 대기 중임을 인지할 수 있게 단계형 로딩을 제공한다.

주요 컴포넌트:

- `ReportGenerationStatus`
- `GenerationStepList`
- `SafetyNotice`
- `RetryPanel`

표시 단계:

- 입력 검증
- 한국어 입력 정규화
- iDISK/RAG 검색
- 기능성원료 데이터 확인
- 리포트 작성
- 추천 기록 저장

상태:

- 생성 중
- 생성 실패
- 사용량 제한 실패
- 안전 가드레일 실패
- 네트워크 오류

이동:

- 생성 성공 -> `/reports/new` 또는 `/reports/:report_id`
- 실패 후 재시도 -> `/reports/generating`
- 설문 수정 -> `/survey`

### 5.6 신규 리포트 결과

Route: `/reports/new`

Auth: 필요

역할:

- 방금 생성한 추천 리포트를 표시한다.
- 추천 성분, 이유, 용량, 주의사항, iHerb 성분 링크, 리포트 채팅 진입을 제공한다.

주요 컴포넌트:

- `ReportHeader`
- `UserInputSummary`
- `RecommendedIngredientList`
- `IngredientDetailCard`
- `IngredientExternalLink`
- `DosageNotice`
- `SideEffectNotice`
- `LifestyleTipList`
- `MedicalDisclaimer`
- `ReportChatPanel`
- `ReportActionBar`

주의:

- iHerb 링크는 백엔드가 내려준 검증 URL만 사용한다.
- 링크가 없는 성분은 일반 텍스트로 표시한다.
- 상품명, 상품 이미지, 가격, 리뷰는 표시하지 않는다.

이동:

- 추천 기록 상세 -> `/reports/:report_id`
- 추천 기록 목록 -> `/reports`
- 다시 설문하기 -> `/survey`

### 5.7 추천 기록 목록

Route: `/reports`

Auth: 필요

역할:

- 저장된 추천 리포트 목록을 조회한다.
- 제목 수정, 삭제, 상세 진입을 제공한다.

주요 컴포넌트:

- `ReportHistoryHeader`
- `ReportFilterBar`
- `ReportHistoryList`
- `ReportHistoryCard`
- `ReportTitleEditDialog`
- `DeleteConfirmDialog`
- `EmptyState`

상태:

- 목록 로딩
- 저장된 리포트 없음
- 목록 조회 실패
- 제목 수정 중
- 삭제 확인

이동:

- 상세 보기 -> `/reports/:report_id`
- 새 추천 받기 -> `/survey`

### 5.8 리포트 상세

Route: `/reports/:report_id`

Auth: 필요

역할:

- 저장된 리포트 전체 내용과 후속 채팅 기록을 조회한다.
- 리포트 기반 추가 질문을 입력할 수 있다.

주요 컴포넌트:

- `ReportHeader`
- `UserInputSummary`
- `RecommendedIngredientList`
- `IngredientDetailCard`
- `EvidenceSourceList`
- `MedicalDisclaimer`
- `ReportChatPanel`
- `ChatMessageList`
- `ChatComposer`
- `ReportActionBar`

상태:

- 상세 로딩
- 접근 권한 없음
- 조회 실패
- 채팅 전송 중
- 채팅 사용량 제한
- 채팅 가드레일 차단
- 리포트 삭제 확인

이동:

- 목록으로 -> `/reports`
- 다시 설문하기 -> `/survey`

### 5.9 마이페이지

Route: `/mypage`

Auth: 필요

역할:

- 회원 정보, 추천 기록, 내가 작성한 게시글, 내가 작성한 댓글을 한 화면에서 확인한다.

주요 컴포넌트:

- `MyPageLayout`
- `ProfileSummaryCard`
- `MyReportSummary`
- `MyPostList`
- `MyCommentList`
- `AccountDangerZone`

이동:

- 회원 정보 수정 -> `/mypage/profile`
- 추천 기록 -> `/reports`
- 리포트 상세 -> `/reports/:report_id`
- 내가 쓴 게시글 -> `/community/:post_id`

### 5.10 회원 정보 수정

Route: `/mypage/profile`

Auth: 필요

역할:

- 나이, 성별, 비밀번호 등 회원 정보를 수정한다.
- 회원 탈퇴 진입점을 제공한다.

주요 컴포넌트:

- `ProfileEditForm`
- `PasswordChangeForm`
- `WithdrawAccountDialog`
- `FormErrorMessage`

상태:

- 기존 정보 로딩
- 저장 중
- 저장 실패
- 회원 탈퇴 확인

### 5.11 커뮤니티 목록

Route: `/community`

Auth: 선택

역할:

- 게시글 목록을 최신순 또는 추천순으로 조회한다.
- 비회원은 목록과 상세 조회만 가능하다.

주요 컴포넌트:

- `CommunityHeader`
- `PostSortTabs`
- `PostSearchBar`
- `PostList`
- `PostListItem`
- `Pagination`
- `WritePostButton`

상태:

- 목록 로딩
- 게시글 없음
- 목록 조회 실패

이동:

- 게시글 상세 -> `/community/:post_id`
- 글쓰기 -> 로그인 상태면 `/community/new`, 비로그인이면 `/login?redirect_to=/community/new`

### 5.12 커뮤니티 상세

Route: `/community/:post_id`

Auth: 선택

역할:

- 게시글, 댓글, 답글을 조회한다.
- 로그인 사용자는 추천, 댓글, 답글을 작성할 수 있다.

주요 컴포넌트:

- `PostDetail`
- `PostActionMenu`
- `PostLikeButton`
- `CommentList`
- `CommentItem`
- `ReplyList`
- `CommentComposer`
- `DeleteConfirmDialog`

상태:

- 상세 로딩
- 조회 실패
- 추천 처리 중
- 댓글 작성 중
- 답글 작성 중
- 권한 없음

이동:

- 목록으로 -> `/community`
- 수정 -> `/community/:post_id/edit`
- 비로그인 댓글 작성 -> `/login?redirect_to=/community/:post_id`

### 5.13 게시글 작성

Route: `/community/new`

Auth: 필요

역할:

- 건강 고민, 영양제 경험, 추천 후기 등 게시글을 작성한다.

주요 컴포넌트:

- `PostEditor`
- `PostCategorySelect`
- `PostTitleInput`
- `PostContentEditor`
- `EditorActionBar`

상태:

- 입력 중
- 필수값 누락
- 저장 중
- 저장 실패

이동:

- 작성 성공 -> `/community/:post_id`
- 취소 -> `/community`

### 5.14 게시글 수정

Route: `/community/:post_id/edit`

Auth: 필요

역할:

- 본인 게시글을 수정한다.

주요 컴포넌트:

- `PostEditor`
- `PostCategorySelect`
- `PostTitleInput`
- `PostContentEditor`
- `EditorActionBar`

상태:

- 기존 글 로딩
- 권한 없음
- 저장 중
- 저장 실패

이동:

- 수정 성공 -> `/community/:post_id`
- 취소 -> `/community/:post_id`

### 5.15 관리자 화면

Routes: `/admin`, `/admin/users`, `/admin/posts`, `/admin/comments`

Auth: 관리자

역할:

- 회원 상태, 게시글, 댓글/답글을 관리한다.
- 선택 기능인 추천 기록 통계는 MVP 후순위로 분리한다.

주요 컴포넌트:

- `AdminLayout`
- `AdminNav`
- `UserManagementTable`
- `PostModerationTable`
- `CommentModerationTable`
- `AdminDeleteDialog`

상태:

- 권한 없음
- 목록 로딩
- 삭제 확인
- 처리 실패

## 6. 인증 가드

인증이 필요한 라우트:

- `/survey`
- `/reports/generating`
- `/reports/new`
- `/reports`
- `/reports/:report_id`
- `/mypage`
- `/mypage/profile`
- `/community/new`
- `/community/:post_id/edit`

관리자 권한이 필요한 라우트:

- `/admin`
- `/admin/users`
- `/admin/posts`
- `/admin/comments`

인증이 필요한 액션:

- 리포트 생성
- 리포트 조회, 제목 수정, 삭제
- 리포트 기반 채팅
- 게시글 작성, 수정, 삭제
- 댓글/답글 작성, 수정, 삭제
- 게시글 추천/추천 취소
- 회원 정보 수정, 회원 탈퇴

비로그인 사용자가 인증이 필요한 라우트나 액션에 접근하면 `/login?redirect_to=...`로 이동하고, 로그인 성공 후 원래 의도한 위치로 복귀한다.

## 7. API 경계 메모

예상 API 영역:

- 인증: 회원가입, 로그인, 로그아웃, 토큰 검증
- 회원: 내 정보 조회/수정/탈퇴
- 추천 설문: 건강 목표, 복용 약, 특이사항 선택지 조회
- AI 추천: 리포트 생성, 생성 상태 조회, 가드레일 결과
- 추천 기록: 목록, 상세, 제목 수정, 삭제
- 리포트 채팅: 메시지 목록, 메시지 전송
- 외부 링크: 추천 성분별 iHerb 성분 링크
- 커뮤니티: 게시글 CRUD, 댓글/답글 CRUD, 추천/추천 취소
- 관리자: 회원, 게시글, 댓글 관리

프론트엔드 mock data도 API 계약과 동일하게 snake_case를 사용한다.
