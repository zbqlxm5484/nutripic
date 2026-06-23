<template>
  <MyPageLayout>
    <ContentSection title-id="profile-summary-title" title="회원 정보">
      <p>API 연결 후 회원 기본 정보와 최근 추천 목표를 표시합니다.</p>
      <RouterLink to="/mypage/profile">회원 정보 수정</RouterLink>
    </ContentSection>

    <ContentSection title-id="report-history-title" title="추천 기록">
      <p>저장된 리포트 목록과 상세 이동 링크 영역입니다.</p>
    </ContentSection>

    <ContentSection title-id="community-activity-title" title="내 게시글과 댓글">
      <p>내가 작성한 게시글과 댓글 목록 영역입니다.</p>
    </ContentSection>
  </MyPageLayout>
</template>

<script setup>
import { ContentSection, MyPageLayout } from '../../../shared/components'
</script>

<style scoped>
dl,
dd {
  margin: 0;
}

dl {
  display: grid;
  gap: 12px;
}

dt,
.activity-list span {
  color: #5b6b65;
  font-size: 0.875rem;
}

.activity-list {
  display: grid;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.activity-list li {
  display: grid;
  gap: 4px;
}

a {
  color: #165a46;
  font-weight: 700;
}
</style>
