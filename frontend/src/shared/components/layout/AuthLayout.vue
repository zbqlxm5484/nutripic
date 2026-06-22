<template>
  <main class="auth-layout">
    <section class="auth-layout__panel" :aria-labelledby="titleId">
      <RouterLink class="auth-layout__brand" to="/">Neutripic</RouterLink>
      <header class="auth-layout__header">
        <p v-if="eyebrow" class="auth-layout__eyebrow">{{ eyebrow }}</p>
        <h1 :id="titleId">{{ title }}</h1>
        <p v-if="description" class="auth-layout__description">{{ description }}</p>
      </header>
      <slot />
    </section>
  </main>
</template>

<script setup>
const props = defineProps({
  title: {
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

const titleId = `auth-layout-${props.title.replace(/\s+/g, '-').toLowerCase()}`
</script>

<style scoped>
.auth-layout {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 32px 16px;
  background: #f8faf9;
  color: #17231f;
}

.auth-layout__panel {
  width: min(440px, 100%);
  padding: 32px;
  border: 1px solid #dde7e2;
  border-radius: 8px;
  background: #ffffff;
}

.auth-layout__brand {
  display: inline-block;
  margin-bottom: 28px;
  color: #165a46;
  font-weight: 700;
  text-decoration: none;
}

.auth-layout__header {
  margin-bottom: 28px;
}

.auth-layout__eyebrow {
  margin: 0 0 8px;
  color: #4e6f61;
  font-size: 0.875rem;
  font-weight: 700;
}

.auth-layout__header h1 {
  margin: 0;
  font-size: 1.75rem;
}

.auth-layout__description {
  margin: 10px 0 0;
  color: #5b6b65;
  line-height: 1.6;
}
</style>
