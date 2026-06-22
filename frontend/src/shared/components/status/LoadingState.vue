<template>
  <section class="status-state" role="status" aria-live="polite">
    <p class="status-state__label">{{ label }}</p>
    <p v-if="description" class="status-state__description">{{ description }}</p>
  </section>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    default: '불러오는 중입니다',
  },
  description: {
    type: String,
    default: '',
  },
})
</script>

<style scoped>
.status-state {
  padding: 20px;
  border: 1px solid #dde7e2;
  border-radius: 8px;
  background: #ffffff;
}

.status-state__label {
  margin: 0;
  color: #17231f;
  font-weight: 700;
}

.status-state__description {
  margin: 8px 0 0;
  color: #5b6b65;
  line-height: 1.6;
}
</style>
