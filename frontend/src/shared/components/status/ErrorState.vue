<template>
  <section class="error-state" role="alert">
    <p class="error-state__title">{{ title }}</p>
    <p v-if="description" class="error-state__description">{{ description }}</p>
    <div v-if="$slots.action" class="error-state__action">
      <slot name="action" />
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: '문제가 발생했습니다',
  },
  description: {
    type: String,
    default: '',
  },
})
</script>

<style scoped>
.error-state {
  padding: 20px;
  border: 1px solid #efc8c2;
  border-radius: 8px;
  background: #fff7f5;
}

.error-state__title {
  margin: 0;
  color: #8f2f23;
  font-weight: 700;
}

.error-state__description {
  margin: 8px 0 0;
  color: #6f3f38;
  line-height: 1.6;
}

.error-state__action {
  margin-top: 16px;
}
</style>
