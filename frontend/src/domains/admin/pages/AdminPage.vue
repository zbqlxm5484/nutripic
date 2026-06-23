<template>
  <AdminLayout>
    <ContentSection title-id="admin-notice-title" title="관리 범위">
      <p>회원 상태, 게시글, 댓글과 답글을 조회하고 필요한 경우 삭제 액션을 수행하는 화면입니다.</p>
      <nav class="admin-links" aria-label="관리자 바로가기">
        <RouterLink to="/admin/users">회원 관리</RouterLink>
        <RouterLink to="/admin/posts">게시글 관리</RouterLink>
        <RouterLink to="/admin/comments">댓글 관리</RouterLink>
      </nav>
    </ContentSection>
  </AdminLayout>
</template>

<script setup>
import { AdminLayout, ContentSection } from '../../../shared/components'
</script>

<style scoped>
p {
  margin: 0;
  color: #5b6b65;
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
