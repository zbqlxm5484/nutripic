<template>
  <MyPageLayout>
    <section class="mypage-section" aria-labelledby="profile-summary-title">
      <h2 id="profile-summary-title">회원 정보</h2>
      <p>API 연결 후 회원 기본 정보와 최근 추천 목표를 표시합니다.</p>
      <RouterLink to="/mypage/profile">회원 정보 수정</RouterLink>
    </section>

    <section class="mypage-section" aria-labelledby="report-history-title">
      <h2 id="report-history-title">추천 기록</h2>
      <p>저장된 리포트 목록과 상세 이동 링크 영역입니다.</p>
    </section>

    <section class="mypage-section" aria-labelledby="community-activity-title">
      <h2 id="community-activity-title">내 게시글과 댓글</h2>
      <p>내가 작성한 게시글과 댓글 목록 영역입니다.</p>
    </section>
  </MyPageLayout>
</template>

<script setup>
import { MyPageLayout } from '../../../shared/components'
</script>

<style scoped>
.mypage-section {
  display: grid;
  gap: 14px;
  padding: 24px;
  border: 1px solid #dde7e2;
  border-radius: 8px;
  background: #ffffff;
}

.mypage-section h2 {
  margin: 0;
  font-size: 1.25rem;
}

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
