<template>
  <AdminLayout>
    <section class="admin-panel" aria-labelledby="admin-notice-title">
      <h2 id="admin-notice-title">관리 범위</h2>
      <p>회원 상태, 게시글, 댓글과 답글을 조회하고 필요한 경우 삭제 액션을 수행하는 화면입니다.</p>
      <nav class="admin-links" aria-label="관리자 바로가기">
        <RouterLink to="/admin/users">회원 관리</RouterLink>
        <RouterLink to="/admin/posts">게시글 관리</RouterLink>
        <RouterLink to="/admin/comments">댓글 관리</RouterLink>
      </nav>
    </section>
  </AdminLayout>
</template>

<script setup>
import { AdminLayout } from '../../../shared/components'
</script>

<style scoped>
.admin-panel {
  display: grid;
  gap: 16px;
  padding: 24px;
  border: 1px solid #dde7e2;
  border-radius: 8px;
  background: #ffffff;
}

.admin-panel p {
  margin: 0;
  color: #5b6b65;
}

.admin-panel h2 {
  margin: 0 0 10px;
  font-size: 1.25rem;
}

.admin-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.admin-links a {
  color: #165a46;
  font-weight: 700;
}
</style>
