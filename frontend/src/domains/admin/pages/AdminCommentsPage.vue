<template>
  <AdminLayout title="댓글 관리">
    <AdminTablePanel title="댓글과 답글 목록" description="게시글별 댓글과 답글을 확인하고 삭제 액션을 수행합니다." title-id="comments-title">
      <table>
        <thead>
          <tr>
            <th scope="col">내용</th>
            <th scope="col">게시글</th>
            <th scope="col">작성자</th>
            <th scope="col">작성일</th>
            <th scope="col">액션</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>댓글 내용 영역</td>
            <td>게시글 제목 영역</td>
            <td>작성자 영역</td>
            <td>작성일 영역</td>
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
  min-width: 720px;
}

th,
td {
  padding: 12px;
  border-top: 1px solid #edf2ef;
  text-align: left;
  vertical-align: top;
}

th {
  color: #5b6b65;
  font-size: 0.875rem;
}
</style>
