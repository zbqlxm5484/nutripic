<template>
  <section class="empty-state">
    <p class="empty-state__title">{{ title }}</p>
    <p v-if="description" class="empty-state__description">{{ description }}</p>
    <div v-if="$slots.action" class="empty-state__action">
      <slot name="action" />
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: '표시할 내용이 없습니다',
  },
  description: {
    type: String,
    default: '',
  },
})
</script>

<style scoped>
.empty-state {
  padding: 24px;
  border: 1px dashed #c9d8d1;
  border-radius: 8px;
  background: #ffffff;
  text-align: center;
}

.empty-state__title {
  margin: 0;
  color: #17231f;
  font-weight: 700;
}

.empty-state__description {
  margin: 8px auto 0;
  max-width: 520px;
  color: #5b6b65;
  line-height: 1.6;
}

.empty-state__action {
  margin-top: 16px;
}
</style>
