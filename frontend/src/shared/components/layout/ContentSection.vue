<template>
  <section class="content-section" :aria-labelledby="titleId">
    <header class="content-section__header">
      <p v-if="eyebrow" class="content-section__eyebrow">{{ eyebrow }}</p>
      <h2 :id="titleId">{{ title }}</h2>
      <p v-if="description" class="content-section__description">{{ description }}</p>
    </header>
    <slot />
  </section>
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
.content-section {
  display: grid;
  gap: var(--space-4);
  padding: var(--space-6);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.content-section__header {
  display: grid;
  gap: var(--space-2);
}

.content-section__eyebrow,
.content-section__description {
  margin: 0;
  color: var(--color-text-muted);
  line-height: 1.6;
}

.content-section h2 {
  margin: 0;
  font-size: 1.25rem;
}
</style>
