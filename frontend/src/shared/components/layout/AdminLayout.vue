<template>
  <AppLayout>
    <section class="admin-layout" aria-labelledby="admin-layout-title">
      <header class="admin-layout__header">
        <p class="admin-layout__eyebrow">관리자</p>
        <h1 id="admin-layout-title">{{ title }}</h1>
      </header>
      <nav class="admin-layout__nav" aria-label="관리자 메뉴">
        <RouterLink to="/admin">대시보드</RouterLink>
        <RouterLink to="/admin/users">회원 관리</RouterLink>
        <RouterLink to="/admin/posts">게시글 관리</RouterLink>
        <RouterLink to="/admin/comments">댓글 관리</RouterLink>
      </nav>
      <div class="admin-layout__content">
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
    default: '관리자 대시보드',
  },
})
</script>

<style scoped>
.admin-layout__header {
  margin-bottom: 20px;
}

.admin-layout__eyebrow {
  margin: 0 0 8px;
  color: #4e6f61;
  font-weight: 700;
}

.admin-layout__header h1 {
  margin: 0;
  font-size: 2rem;
}

.admin-layout__nav {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 24px;
}

.admin-layout__nav a {
  padding: 10px 14px;
  border: 1px solid #c9d8d1;
  border-radius: 8px;
  color: #31443d;
  text-decoration: none;
}

.admin-layout__content {
  display: grid;
  gap: 18px;
}
</style>
