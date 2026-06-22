# Page Components

이 문서는 프론트엔드 구현을 페이지 단위 작업으로 나누기 위한 컴포넌트 설계 초안이다. 실제 디렉터리 구조와 컴포넌트 이름은 프레임워크가 확정되면 조정할 수 있지만, 화면 책임과 상태는 이 문서를 기준으로 유지한다.

## 1. 공통 컴포넌트

### 1.1 Layout

| Component | 책임 | 사용 페이지 |
| --- | --- | --- |
| `AppLayout` | 기본 페이지 프레임, 헤더/푸터 포함 | 대부분의 공개/사용자 페이지 |
| `AuthLayout` | 로그인/회원가입 중앙 정렬 레이아웃 | 로그인, 회원가입 |
| `SurveyLayout` | 설문 진행률과 단계별 입력 영역 배치 | 추천 설문 |
| `ReportLayout` | 리포트 본문과 채팅 패널 배치 | 신규 리포트, 리포트 상세 |
| `MyPageLayout` | 마이페이지 사이드/탭 구조 | 마이페이지 |
| `AdminLayout` | 관리자 네비게이션과 테이블 영역 | 관리자 화면 |

### 1.2 Navigation

| Component | 책임 |
| --- | --- |
| `AppHeader` | 로고, 홈, 추천 시작, 커뮤니티, 마이페이지, 로그인/로그아웃 |
| `MobileNav` | 모바일 하단 또는 드로어 네비게이션 |
| `AuthGuard` | 인증 필요 라우트 접근 제어 |
| `AdminGuard` | 관리자 라우트 접근 제어 |
| `RedirectNotice` | 로그인 후 복귀 안내 |

### 1.3 Feedback

| Component | 책임 |
| --- | --- |
| `LoadingState` | 목록/상세 로딩 표시 |
| `EmptyState` | 데이터 없음 안내와 다음 행동 CTA |
| `ErrorState` | 조회/저장 실패 안내와 재시도 |
| `FormErrorMessage` | 입력 필드 또는 폼 단위 오류 |
| `ConfirmDialog` | 삭제, 탈퇴 등 되돌리기 어려운 행동 확인 |
| `ToastMessage` | 저장 완료, 삭제 완료 등 짧은 피드백 |
| `SafetyNotice` | 건강 정보 제공 목적과 전문가 상담 안내 |
| `MedicalDisclaimer` | 리포트/채팅 하단 의료 면책 문구 |

## 2. 홈

Page: `/`

### Components

| Component | 책임 |
| --- | --- |
| `HeroSection` | 서비스명, 성분 중심 리포트 가치, 추천 시작 CTA |
| `ServiceValueSection` | RAG 기반 근거, 안전 가드레일, 성분 링크 정책 설명 |
| `MainFlowPreview` | 설문부터 리포트/채팅까지 흐름 요약 |
| `SafetyNotice` | 진단/처방 대체 아님 안내 |
| `CommunityPreview` | 최신 게시글 일부 또는 커뮤니티 진입 CTA |

### 작업 메모

- 첫 화면에서 제품 추천/쇼핑몰처럼 보이지 않게 한다.
- CTA는 로그인 상태에 따라 `/survey` 또는 `/login?redirect_to=/survey`로 이동한다.
- iHerb는 상품 구매 유도 문구가 아니라 검증된 외부 성분 링크로만 설명한다.

## 3. 인증

Pages: `/signup`, `/login`

### Components

| Component | 책임 |
| --- | --- |
| `SignupForm` | 아이디/이메일, 비밀번호, 나이, 성별 입력 |
| `LoginForm` | 아이디/이메일, 비밀번호 입력 |
| `PasswordField` | 비밀번호 표시 전환, 확인 입력 |
| `AgeInput` | 숫자 범위 검증 |
| `GenderSelect` | 성별 선택 |
| `AuthSubmitButton` | 제출 중 disabled 처리 |

### 상태

- 입력 중
- 제출 중
- 유효성 오류
- 인증 실패
- 가입 성공

### API 경계

- request/response field는 snake_case를 사용한다.
- JWT 저장 위치와 갱신 전략은 보안 정책 확정 후 공통 auth 모듈에서 처리한다.

## 4. 추천 설문

Page: `/survey`

### Components

| Component | 책임 |
| --- | --- |
| `SurveyProgress` | 현재 단계와 완료 상태 표시 |
| `HealthGoalSelector` | 건강 목표 최대 5개 선택 |
| `GoalPriorityList` | 선택한 목표의 우선순위 지정 |
| `MedicationSelector` | 대표 복용 약 선택 |
| `SpecialConditionSelector` | 임신/수유, 질환, 알레르기 등 특이사항 선택 |
| `AdditionalInfoTextarea` | 선택지에 없는 정보 자유 입력 |
| `AdditionalQuestionPanel` | 위험 요인 또는 정보 부족 시 추가 확인 질문 |
| `UsageLimitBanner` | 리포트 생성 제한 안내 |
| `SurveyActionBar` | 이전, 다음, 생성 요청 버튼 |

### 입력 규칙

- 건강 목표는 1개 이상, 최대 5개까지 선택한다.
- 선택한 건강 목표는 우선순위를 지정할 수 있어야 한다.
- 자유 입력에는 과도한 개인정보를 입력하지 않도록 안내한다.
- 리포트 생성 버튼은 필수값과 사용량 제한을 통과해야 활성화한다.

### 상태

- 선택지 로딩
- 입력 중
- 필수값 누락
- 최대 선택 개수 초과
- 사용량 제한 초과
- 가드레일 차단
- 추가 확인 질문 표시
- 제출 중

### 검증 포인트

- 건강 목표 6개 이상 선택 불가
- 복용 약/특이사항이 없어도 명시적으로 "없음" 또는 미선택 상태를 구분
- 임신/수유, 간/신장 질환, 항응고제 등 고위험 항목 선택 시 안전 안내 강화

## 5. 리포트 생성

Page: `/reports/generating`

### Components

| Component | 책임 |
| --- | --- |
| `ReportGenerationStatus` | 전체 진행 상태 표시 |
| `GenerationStepList` | 입력 검증, 정규화, RAG 검색, 리포트 작성 단계 표시 |
| `GenerationErrorPanel` | 실패 사유와 재시도/설문 수정 CTA |
| `SafetyNotice` | 대기 중에도 의료 고지 표시 |

### 상태

- 생성 요청 접수
- 입력 정규화 중
- RAG 검색 중
- 리포트 생성 중
- 저장 중
- 생성 성공
- 생성 실패

### 작업 메모

- 실제 진행률을 알 수 없으면 퍼센트 대신 단계형 상태를 사용한다.
- 새로고침 시 최근 생성 작업을 복구할 수 있는지 백엔드 계약이 필요하다.

## 6. 추천 리포트

Pages: `/reports/new`, `/reports/:report_id`

### Components

| Component | 책임 |
| --- | --- |
| `ReportHeader` | 리포트 제목, 생성일, 액션 |
| `UserInputSummary` | 나이, 성별, 건강 목표, 복용 약, 특이사항 요약 |
| `RecommendedIngredientList` | 핵심 추천 성분 목록 |
| `IngredientDetailCard` | 성분별 추천 이유, 기능성, 용량, 주의사항 |
| `IngredientExternalLink` | 검증된 iHerb 성분 링크 표시 |
| `DosageNotice` | 일일섭취량/복용법 안내 |
| `SideEffectNotice` | 부작용 가능성 안내 |
| `EvidenceSourceList` | 가능한 경우 근거 데이터 출처 표시 |
| `LifestyleTipList` | 생활 습관 관리 팁 |
| `MedicalDisclaimer` | 필수 면책 안내 |
| `ReportActionBar` | 제목 수정, 삭제, 다시 설문, 목록 이동 |

### iHerb 링크 표시 규칙

- `iherb_url`이 있는 성분만 링크로 표시한다.
- 링크 텍스트는 성분명 중심으로 표시한다.
- 링크 클릭 시 새 창 또는 외부 이동임을 명확히 한다.
- 상품명, 이미지, 가격, 리뷰, 별점, 판매자 정보는 표시하지 않는다.
- 사용자 입력을 직접 URL로 만들지 않는다.

### 리포트 필수 섹션

- 사용자 입력 요약
- 핵심 추천 성분 목록
- 성분별 추천 이유
- 기대할 수 있는 기능성
- 복용법 및 권장 용량
- 부작용 가능성
- 섭취 시 주의사항
- 복용 약 또는 특이사항 관련 주의 문구
- 생활 습관 관리 팁
- 건강 정보 제공 목적의 면책 안내

## 7. 리포트 기반 채팅

Pages: `/reports/new`, `/reports/:report_id`

### Components

| Component | 책임 |
| --- | --- |
| `ReportChatPanel` | 채팅 영역 컨테이너 |
| `ChatMessageList` | 사용자/AI 메시지 목록 |
| `ChatMessageItem` | 메시지 본문, 생성 시간, 안전 안내 |
| `ChatComposer` | 질문 입력과 전송 |
| `ChatScopeNotice` | 질문 가능 범위 안내 |
| `ChatLimitBanner` | 채팅 사용량 제한 안내 |
| `BlockedAnswerPanel` | 고위험 요청 또는 범위 외 질문 차단 안내 |

### 허용 범위

- 리포트에 포함된 성분 설명
- 복용법, 권장 용량, 부작용, 주의사항
- 성분 간 차이
- 사용자 입력과 관련된 일반적인 건강기능식품 정보

### 제한 범위

- 질병 진단
- 처방 또는 치료 지시
- 복용 약물의 중단, 변경, 증량, 감량 지시
- 제품 구매 유도
- 특정 제품 효능 보장

## 8. 추천 기록과 마이페이지

Pages: `/reports`, `/mypage`, `/mypage/profile`

### Components

| Component | 책임 |
| --- | --- |
| `ReportHistoryList` | 추천 기록 목록 |
| `ReportHistoryCard` | 리포트 제목, 생성일, 주요 목표/성분 표시 |
| `ReportFilterBar` | 목표, 기간 등 필터 |
| `ReportTitleEditDialog` | 추천 기록 제목 수정 |
| `ProfileSummaryCard` | 회원 정보 요약 |
| `ProfileEditForm` | 나이, 성별 등 수정 |
| `PasswordChangeForm` | 비밀번호 변경 |
| `MyPostList` | 내가 작성한 게시글 |
| `MyCommentList` | 내가 작성한 댓글 |
| `WithdrawAccountDialog` | 회원 탈퇴 확인 |

### 상태

- 목록 로딩
- 빈 목록
- 조회 실패
- 제목 수정 중
- 삭제 확인
- 회원 정보 저장 중
- 회원 탈퇴 확인

## 9. 커뮤니티

Pages: `/community`, `/community/:post_id`, `/community/new`, `/community/:post_id/edit`

### Components

| Component | 책임 |
| --- | --- |
| `CommunityHeader` | 게시판 제목, 글쓰기 CTA |
| `PostSortTabs` | 최신순/추천순 정렬 |
| `PostSearchBar` | 검색어 입력 |
| `PostList` | 게시글 목록 |
| `PostListItem` | 제목, 작성자, 댓글 수, 추천 수, 작성일 |
| `PostDetail` | 게시글 본문 |
| `PostActionMenu` | 수정/삭제 |
| `PostLikeButton` | 추천/추천 취소 |
| `CommentList` | 댓글 목록 |
| `CommentItem` | 댓글 수정/삭제/답글 액션 |
| `ReplyList` | 답글 목록 |
| `CommentComposer` | 댓글/답글 작성 |
| `PostEditor` | 게시글 작성/수정 폼 |

### 인증 규칙

- 비회원: 목록/상세 조회 가능
- 로그인 사용자: 게시글 작성, 댓글/답글 작성, 추천 가능
- 작성자: 본인 게시글/댓글/답글 수정 및 삭제 가능
- 관리자: 부적절한 게시글/댓글/답글 삭제 가능

## 10. 관리자

Pages: `/admin`, `/admin/users`, `/admin/posts`, `/admin/comments`

### Components

| Component | 책임 |
| --- | --- |
| `AdminNav` | 관리자 메뉴 |
| `AdminSummaryCards` | 관리 대상 요약 |
| `UserManagementTable` | 회원 목록과 상태 관리 |
| `PostModerationTable` | 게시글 목록과 삭제 |
| `CommentModerationTable` | 댓글/답글 목록과 삭제 |
| `AdminDeleteDialog` | 관리자 삭제 확인 |

### 작업 메모

- 관리자 화면은 일반 사용자와 명확히 분리한다.
- 추천 기록 통계는 선택 요구사항이므로 MVP 일정에 따라 별도 작업으로 분리한다.

## 11. 데이터 모델 초안

프론트엔드 mock과 타입 정의는 아래 형태를 기준으로 시작한다. 실제 필드는 백엔드 serializer 확정 후 조정한다.

```ts
type HealthGoal = {
  id: number;
  name: string;
  normalized_name: string;
};

type SurveyInput = {
  age: number;
  gender: string;
  health_goals: Array<{ goal_id: number; priority: number }>;
  medications: number[];
  special_conditions: number[];
  additional_info: string;
};

type IngredientLink = {
  ingredient_name_ko: string;
  ingredient_name_en: string;
  normalized_name: string;
  iherb_url: string | null;
  iherb_category_name: string | null;
};

type Report = {
  report_id: number;
  title: string;
  created_at: string;
  input_summary: Record<string, unknown>;
  recommended_ingredients: IngredientReport[];
  lifestyle_tips: string[];
  disclaimer: string;
};

type IngredientReport = {
  ingredient_name_ko: string;
  ingredient_name_en: string;
  recommendation_reason: string;
  functionality: string;
  dosage: string;
  side_effects: string;
  precautions: string;
  external_link: IngredientLink | null;
};
```

## 12. 작업 분해 제안

1. 라우팅/레이아웃: 공개, 인증, 관리자 레이아웃과 가드 구현
2. 인증: 회원가입, 로그인, JWT 저장/로그아웃 흐름
3. 설문: 선택지 조회, 목표 선택/우선순위, 입력 검증
4. 리포트 생성: 생성 요청, 대기 화면, 실패/재시도 처리
5. 리포트: 상세 표시, iHerb 성분 링크, 의료 고지
6. 리포트 채팅: 메시지 목록, 질문 전송, 제한/차단 상태
7. 추천 기록: 목록, 상세, 제목 수정, 삭제
8. 마이페이지: 회원 정보, 내 게시글/댓글
9. 커뮤니티: 목록/상세/작성/수정/댓글/답글/추천
10. 관리자: 회원/게시글/댓글 관리
