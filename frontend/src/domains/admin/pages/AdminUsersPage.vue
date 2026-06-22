<template>
  <AdminLayout title="회원 관리">
    <section class="admin-table-panel" aria-labelledby="users-title">
      <header>
        <h2 id="users-title">회원 목록</h2>
        <p>회원 상태와 기본 정보를 확인합니다.</p>
      </header>

      <table>
        <thead>
          <tr>
            <th scope="col">회원</th>
            <th scope="col">나이 / 성별</th>
            <th scope="col">상태</th>
            <th scope="col">가입일</th>
            <th scope="col">액션</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>회원 식별자 영역</td>
            <td>나이 / 성별 영역</td>
            <td>상태 영역</td>
            <td>가입일 영역</td>
            <td><button type="button">상태 변경</button></td>
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
  min-width: 680px;
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
  border: 1px solid #c9d8d1;
  border-radius: 8px;
  background: #ffffff;
  color: #165a46;
  font: inherit;
  font-weight: 700;
}
</style>
