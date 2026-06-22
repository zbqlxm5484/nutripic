<template>
  <AdminLayout title="댓글 관리">
    <section class="admin-table-panel" aria-labelledby="comments-title">
      <header>
        <h2 id="comments-title">댓글과 답글 목록</h2>
        <p>게시글별 댓글과 답글을 확인하고 삭제 액션을 수행합니다.</p>
      </header>

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
