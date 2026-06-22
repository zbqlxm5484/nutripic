<template>
  <AuthLayout
    title="회원가입"
    eyebrow="리포트 저장을 위한 계정 생성"
    description="기본 정보는 성분 추천 조건과 추천 기록 관리에 사용됩니다."
  >
    <form class="auth-form" aria-label="회원가입 폼">
      <label>
        아이디 또는 이메일
        <input type="email" name="email" autocomplete="email" placeholder="아이디 또는 이메일" />
      </label>
      <label>
        비밀번호
        <input type="password" name="password" autocomplete="new-password" placeholder="비밀번호" />
      </label>
      <label>
        비밀번호 확인
        <input type="password" name="password_confirm" autocomplete="new-password" placeholder="비밀번호 확인" />
      </label>
      <label>
        나이
        <input type="number" name="age" min="14" max="120" placeholder="나이" />
      </label>
      <label>
        성별
        <select name="gender">
          <option value="">선택</option>
          <option value="female">여성</option>
          <option value="male">남성</option>
          <option value="other">기타 또는 응답하지 않음</option>
        </select>
      </label>
      <FormErrorMessage message="" />
      <button type="button">회원가입</button>
    </form>

    <p class="auth-link">
      이미 계정이 있나요?
      <RouterLink to="/login">로그인</RouterLink>
    </p>
  </AuthLayout>
</template>

<script setup>
import { AuthLayout, FormErrorMessage } from '../../../shared/components'
</script>

<style scoped>
.auth-form {
  display: grid;
  gap: 16px;
}

.auth-form label {
  display: grid;
  gap: 8px;
  color: #31443d;
  font-weight: 700;
}

.auth-form input,
.auth-form select {
  min-height: 42px;
  padding: 0 12px;
  border: 1px solid #c9d8d1;
  border-radius: 8px;
  background: #ffffff;
  font: inherit;
}

.auth-form button {
  min-height: 44px;
  border: 0;
  border-radius: 8px;
  background: #165a46;
  color: #ffffff;
  font: inherit;
  font-weight: 700;
}

.auth-link {
  margin: 18px 0 0;
  color: #5b6b65;
}

.auth-link a {
  color: #165a46;
  font-weight: 700;
}
</style>
