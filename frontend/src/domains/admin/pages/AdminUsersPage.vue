<template>
  <AdminLayout title="회원 관리">
    <AdminTablePanel title="회원 목록" description="회원 상태와 기본 정보를 확인합니다." title-id="users-title">
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
            <td><BaseButton size="sm">상태 변경</BaseButton></td>
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
</style>
