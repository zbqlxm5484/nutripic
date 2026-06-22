<template>
  <aside class="safety-notice" aria-label="건강 정보 안내">
    <strong>{{ title }}</strong>
    <p>{{ message }}</p>
  </aside>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: '건강 정보 안내',
  },
  message: {
    type: String,
    default: '질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.',
  },
})
</script>

<style scoped>
.safety-notice {
  padding: 16px 18px;
  border: 1px solid #d5dfc3;
  border-radius: 8px;
  background: #fbfdf4;
  color: #354421;
}

.safety-notice strong {
  display: block;
  margin-bottom: 6px;
}

.safety-notice p {
  margin: 0;
  line-height: 1.6;
}
</style>
