<template>
  <AppLayout>
    <section class="survey-layout" aria-labelledby="survey-layout-title">
      <header class="survey-layout__header">
        <p class="survey-layout__eyebrow">추천 설문</p>
        <h1 id="survey-layout-title">{{ title }}</h1>
        <p>{{ description }}</p>
      </header>
      <div class="survey-layout__body">
        <slot />
      </div>
    </section>
  </AppLayout>
</template>

<script setup>
import AppLayout from './AppLayout.vue'

defineProps({
  title: {
    type: String,
    default: '건강 목표와 주의사항을 알려주세요',
  },
  description: {
    type: String,
    default: '입력한 정보는 성분 중심 리포트와 안전 안내를 구성하는 데 사용됩니다.',
  },
})
</script>

<style scoped>
.survey-layout__header {
  margin-bottom: 28px;
}

.survey-layout__eyebrow {
  margin: 0 0 8px;
  color: #4e6f61;
  font-weight: 700;
}

.survey-layout__header h1 {
  margin: 0;
  font-size: 2rem;
}

.survey-layout__header p:last-child {
  max-width: 680px;
  color: #5b6b65;
  line-height: 1.6;
}

.survey-layout__body {
  display: grid;
  gap: 20px;
}
</style>
