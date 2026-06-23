<template>
  <AppLayout>
    <section class="generation-page" aria-labelledby="generation-title">
      <PageHeader
        title-id="generation-title"
        eyebrow="리포트 생성"
        title="성분 중심 리포트를 준비하고 있습니다"
        description="실제 진행률을 알 수 없을 때는 단계형 상태로 안내합니다."
      />

      <ContentSection title-id="status-title" title="생성 단계">
        <ol class="step-list">
          <li class="step-list__item step-list__item--done">입력 검증</li>
          <li class="step-list__item step-list__item--active">사용자 입력 정규화</li>
          <li class="step-list__item">RAG 검색</li>
          <li class="step-list__item">리포트 작성</li>
          <li class="step-list__item">저장</li>
        </ol>
      </ContentSection>

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
            <BaseButton to="/reports/generating" size="sm">재시도</BaseButton>
            <BaseButton to="/survey" size="sm">설문 수정</BaseButton>
          </div>
        </template>
      </ErrorState>

      <SafetyNotice />
    </section>
  </AppLayout>
</template>

<script setup>
import { AppLayout, BaseButton, ContentSection, ErrorState, LoadingState, PageHeader, SafetyNotice } from '../../../shared/components'
</script>

<style scoped>
.generation-page {
  display: grid;
  gap: 20px;
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

</style>
