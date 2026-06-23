<template>
  <ContentSection :title="title" :title-id="titleId" :description="description" class="report-chat-panel">
    <div class="report-chat-panel__messages">
      <div
        v-for="message in messages"
        :key="message.id ?? message.text"
        class="report-chat-panel__message"
        :class="{ 'report-chat-panel__message--user': message.variant === 'user' }"
      >
        {{ message.text }}
      </div>
    </div>
    <textarea class="form-control" rows="4" :placeholder="placeholder" />
    <BaseButton variant="primary">{{ submitLabel }}</BaseButton>
  </ContentSection>
</template>

<script setup>
import BaseButton from '../base/BaseButton.vue'
import ContentSection from '../layout/ContentSection.vue'

defineProps({
  title: {
    type: String,
    required: true,
  },
  titleId: {
    type: String,
    default: 'chat-title',
  },
  description: {
    type: String,
    default: '',
  },
  messages: {
    type: Array,
    default: () => [],
  },
  placeholder: {
    type: String,
    default: '리포트 기반 질문을 입력하세요.',
  },
  submitLabel: {
    type: String,
    default: '질문 보내기',
  },
})
</script>

<style scoped>
.report-chat-panel__messages {
  display: grid;
  gap: var(--space-3);
}

.report-chat-panel__message {
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: #f0f6f3;
  color: var(--color-text-soft);
}

.report-chat-panel__message--user {
  background: #edf2ef;
}

.report-chat-panel :deep(.form-control) {
  width: 100%;
  box-sizing: border-box;
}
</style>
