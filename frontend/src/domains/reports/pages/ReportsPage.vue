<template>
  <AppLayout>
    <section class="reports-page" aria-labelledby="reports-title">
      <PageHeader
        title-id="reports-title"
        eyebrow="추천 기록"
        title="저장된 리포트"
        description="생성일, 건강 목표, 주요 추천 성분을 기준으로 최근 리포트를 확인합니다."
      >
        <template #actions>
        <BaseButton to="/survey" variant="primary">다시 설문하기</BaseButton>
        </template>
      </PageHeader>

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
import { AppLayout, BaseButton, EmptyState, PageHeader } from '../../../shared/components'
</script>

<style scoped>
.reports-page {
  display: grid;
  gap: 20px;
}

</style>
