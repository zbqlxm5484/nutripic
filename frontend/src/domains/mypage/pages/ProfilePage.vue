<template>
  <MyPageLayout title="회원 정보 수정">
    <form class="profile-form" aria-label="회원 정보 수정 폼">
      <label>
        나이
        <input type="number" name="age" min="14" max="120" placeholder="나이" />
      </label>
      <label>
        성별
        <select name="gender">
          <option value="female">여성</option>
          <option value="male">남성</option>
          <option value="other">기타 또는 응답하지 않음</option>
        </select>
      </label>
      <label>
        새 비밀번호
        <input type="password" name="password" autocomplete="new-password" placeholder="변경할 때만 입력" />
      </label>
      <FormErrorMessage message="" />
      <div class="profile-form__actions">
        <button type="button">저장</button>
        <RouterLink to="/mypage">취소</RouterLink>
      </div>
    </form>
  </MyPageLayout>
</template>

<script setup>
import { FormErrorMessage, MyPageLayout } from '../../../shared/components'
</script>

<style scoped>
.profile-form {
  display: grid;
  gap: 16px;
  padding: 24px;
  border: 1px solid #dde7e2;
  border-radius: 8px;
  background: #ffffff;
}

.profile-form label {
  display: grid;
  gap: 8px;
  color: #31443d;
  font-weight: 700;
}

.profile-form input,
.profile-form select {
  min-height: 42px;
  padding: 0 12px;
  border: 1px solid #c9d8d1;
  border-radius: 8px;
  background: #ffffff;
  font: inherit;
}

.profile-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.profile-form button,
.profile-form a {
  display: inline-flex;
  align-items: center;
  min-height: 40px;
  padding: 0 14px;
  border: 1px solid #c9d8d1;
  border-radius: 8px;
  background: #ffffff;
  color: #165a46;
  font: inherit;
  font-weight: 700;
  text-decoration: none;
}

.profile-form button {
  border-color: #165a46;
  background: #165a46;
  color: #ffffff;
}
</style>
