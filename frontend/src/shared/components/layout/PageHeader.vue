<template>
  <header class="page-header">
    <div>
      <p v-if="eyebrow" class="page-header__eyebrow">{{ eyebrow }}</p>
      <h1 :id="titleId">{{ title }}</h1>
      <p v-if="description" class="page-header__description">{{ description }}</p>
    </div>
    <slot name="actions" />
  </header>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  titleId: {
    type: String,
    required: true,
  },
  eyebrow: {
    type: String,
    default: '',
  },
  description: {
    type: String,
    default: '',
  },
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-5);
}

.page-header__eyebrow {
  margin: 0 0 var(--space-2);
  color: var(--color-brand-muted);
  font-weight: 700;
}

.page-header h1 {
  margin: 0;
  font-size: 2rem;
}

.page-header__description {
  max-width: 680px;
  margin: 10px 0 0;
  color: var(--color-text-muted);
  line-height: 1.6;
}

@media (max-width: 760px) {
  .page-header {
    flex-direction: column;
  }
}
</style>
