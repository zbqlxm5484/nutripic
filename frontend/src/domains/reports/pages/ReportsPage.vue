<template>
  <AppLayout>
    <section class="reports-page" aria-labelledby="reports-title">
      <header class="reports-page__header">
        <div>
          <p>추천 기록</p>
          <h1 id="reports-title">저장된 리포트</h1>
          <span>생성일, 건강 목표, 주요 추천 성분을 기준으로 최근 리포트를 확인합니다.</span>
        </div>
        <RouterLink class="button button--primary" to="/survey">다시 설문하기</RouterLink>
      </header>

      <EmptyState
        title="추천 기록 목록 영역"
        description="API 연결 후 생성일, 건강 목표, 주요 추천 성분, 상세 보기, 제목 수정, 삭제 액션을 표시합니다."
      >
        <template #action>
          <RouterLink class="button" to="/survey">추천 설문 시작</RouterLink>
        </template>
      </EmptyState>
    </section>
  </AppLayout>
</template>

<script setup>
import { AppLayout, EmptyState } from '../../../shared/components'
</script>

<style scoped>
.reports-page {
  display: grid;
  gap: 20px;
}

.reports-page__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.reports-page__header p {
  margin: 0 0 8px;
  color: #4e6f61;
  font-weight: 700;
}

.reports-page__header h1 {
  margin: 0;
  font-size: 2rem;
}

.reports-page__header span {
  display: block;
  margin-top: 8px;
  color: #5b6b65;
}

.button {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.button {
  align-items: center;
  min-height: 38px;
  padding: 0 14px;
  border: 1px solid #c9d8d1;
  border-radius: 8px;
  background: #ffffff;
  color: #165a46;
  font: inherit;
  font-weight: 700;
  text-decoration: none;
}

.button {
  display: inline-flex;
}

.button--primary {
  border-color: #165a46;
  background: #165a46;
  color: #ffffff;
}

@media (max-width: 720px) {
  .reports-page__header {
    flex-direction: column;
  }
}
</style>
