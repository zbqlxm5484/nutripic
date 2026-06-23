<template>
  <AppLayout>
    <section class="reports-page" aria-labelledby="reports-title">
      <header class="reports-page__header">
        <div>
          <p>추천 기록</p>
          <h1 id="reports-title">저장된 리포트</h1>
          <span>생성일, 건강 목표, 주요 추천 성분을 기준으로 최근 리포트를 확인합니다.</span>
        </div>
        <BaseButton to="/survey" variant="primary">다시 설문하기</BaseButton>
      </header>

      <EmptyState
        title="추천 기록 목록 영역"
        description="API 연결 후 생성일, 건강 목표, 주요 추천 성분, 상세 보기, 제목 수정, 삭제 액션을 표시합니다."
      >
        <template #action>
          <BaseButton to="/survey">추천 설문 시작</BaseButton>
        </template>
      </EmptyState>
    </section>
  </AppLayout>
</template>

<script setup>
import { AppLayout, BaseButton, EmptyState } from '../../../shared/components'
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

@media (max-width: 720px) {
  .reports-page__header {
    flex-direction: column;
  }
}
</style>
