<template>
  <AdminLayout title="게시글 관리">
    <AdminTablePanel title="게시글 목록" description="게시글을 조회하고 운영 정책에 따라 삭제할 수 있습니다." title-id="posts-title">
      <table>
        <thead>
          <tr>
            <th scope="col">제목</th>
            <th scope="col">작성자</th>
            <th scope="col">댓글</th>
            <th scope="col">추천</th>
            <th scope="col">액션</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>게시글 제목 영역</td>
            <td>작성자 영역</td>
            <td>댓글 수 영역</td>
            <td>추천 수 영역</td>
            <td><BaseButton size="sm" variant="danger">삭제</BaseButton></td>
          </tr>
        </tbody>
      </table>
    </AdminTablePanel>
  </AdminLayout>
</template>

<script setup>
import { AdminLayout, AdminTablePanel, BaseButton } from '../../../shared/components'
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
  min-width: 640px;
}

th,
td {
  padding: 12px;
  border-top: 1px solid #edf2ef;
  text-align: left;
}

th {
  color: #5b6b65;
  font-size: 0.875rem;
}
</style>
