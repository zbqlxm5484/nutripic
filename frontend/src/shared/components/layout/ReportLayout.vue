<template>
  <AppLayout>
    <section class="report-layout" aria-labelledby="report-layout-title">
      <header class="report-layout__header">
        <div>
          <p class="report-layout__eyebrow">추천 리포트</p>
          <h1 id="report-layout-title">{{ title }}</h1>
        </div>
        <slot name="actions" />
      </header>
      <div class="report-layout__content">
        <article class="report-layout__main">
          <slot />
        </article>
        <aside v-if="$slots.aside" class="report-layout__aside">
          <slot name="aside" />
        </aside>
      </div>
    </section>
  </AppLayout>
</template>

<script setup>
import AppLayout from './AppLayout.vue'

defineProps({
  title: {
    type: String,
    default: '성분 중심 추천 리포트',
  },
})
</script>

<style scoped>
.report-layout__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 28px;
}

.report-layout__eyebrow {
  margin: 0 0 8px;
  color: #4e6f61;
  font-weight: 700;
}

.report-layout__header h1 {
  margin: 0;
  font-size: 2rem;
}

.report-layout__content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 24px;
  align-items: start;
}

.report-layout__main,
.report-layout__aside {
  display: grid;
  gap: 20px;
}

@media (max-width: 920px) {
  .report-layout__header {
    flex-direction: column;
  }

  .report-layout__content {
    grid-template-columns: 1fr;
  }
}
</style>
