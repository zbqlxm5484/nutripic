<template>
  <AdminLayout title="게시글 관리">
    <section class="admin-table-panel" aria-labelledby="posts-title">
      <header>
        <h2 id="posts-title">게시글 목록</h2>
        <p>게시글을 조회하고 운영 정책에 따라 삭제할 수 있습니다.</p>
      </header>

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
            <td><button type="button">삭제</button></td>
          </tr>
        </tbody>
      </table>
    </section>
  </AdminLayout>
</template>

<script setup>
import { AdminLayout } from '../../../shared/components'
</script>

<style scoped>
.admin-table-panel {
  overflow-x: auto;
  padding: 24px;
  border: 1px solid #dde7e2;
  border-radius: 8px;
  background: #ffffff;
}

header {
  margin-bottom: 16px;
}

h2 {
  margin: 0 0 8px;
  font-size: 1.25rem;
}

p {
  margin: 0;
  color: #5b6b65;
}

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

button {
  min-height: 34px;
  padding: 0 12px;
  border: 1px solid #efc8c2;
  border-radius: 8px;
  background: #fff7f5;
  color: #8f2f23;
  font: inherit;
  font-weight: 700;
}
</style>
