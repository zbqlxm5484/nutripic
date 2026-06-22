<template>
  <AppLayout>
    <section class="generation-page" aria-labelledby="generation-title">
      <header class="generation-page__header">
        <p>리포트 생성</p>
        <h1 id="generation-title">성분 중심 리포트를 준비하고 있습니다</h1>
        <span>실제 진행률을 알 수 없을 때는 단계형 상태로 안내합니다.</span>
      </header>

      <section class="status-panel" aria-labelledby="status-title">
        <h2 id="status-title">생성 단계</h2>
        <ol class="step-list">
          <li class="step-list__item step-list__item--done">입력 검증</li>
          <li class="step-list__item step-list__item--active">사용자 입력 정규화</li>
          <li class="step-list__item">RAG 검색</li>
          <li class="step-list__item">리포트 작성</li>
          <li class="step-list__item">저장</li>
        </ol>
      </section>

      <LoadingState
        label="리포트 생성 중"
        description="잠시 후 신규 리포트 결과 화면으로 이동합니다. 새로고침 복구 정책은 백엔드 계약 확정 후 연결합니다."
      />

      <ErrorState
        title="생성 실패 시 표시 영역"
        description="API 또는 AI 생성 실패가 발생하면 재시도와 설문 수정 CTA를 제공합니다."
      >
        <template #action>
          <div class="error-actions">
            <RouterLink to="/reports/generating">재시도</RouterLink>
            <RouterLink to="/survey">설문 수정</RouterLink>
          </div>
        </template>
      </ErrorState>

      <SafetyNotice />
    </section>
  </AppLayout>
</template>

<script setup>
import { AppLayout, ErrorState, LoadingState, SafetyNotice } from '../../../shared/components'
</script>

<style scoped>
.generation-page {
  display: grid;
  gap: 20px;
}

.generation-page__header {
  display: grid;
  gap: 8px;
}

.generation-page__header p {
  margin: 0;
  color: #4e6f61;
  font-weight: 700;
}

.generation-page__header h1 {
  margin: 0;
  font-size: 2rem;
}

.generation-page__header span {
  color: #5b6b65;
  line-height: 1.6;
}

.status-panel {
  padding: 24px;
  border: 1px solid #dde7e2;
  border-radius: 8px;
  background: #ffffff;
}

.status-panel h2 {
  margin: 0 0 16px;
  font-size: 1.25rem;
}

.step-list {
  display: grid;
  gap: 10px;
  margin: 0;
  padding-left: 20px;
}

.step-list__item {
  color: #5b6b65;
}

.step-list__item--done {
  color: #165a46;
  font-weight: 700;
}

.step-list__item--active {
  color: #17231f;
  font-weight: 700;
}

.error-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.error-actions a {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 0 14px;
  border: 1px solid #c9d8d1;
  border-radius: 8px;
  color: #165a46;
  font-weight: 700;
  text-decoration: none;
}
</style>
