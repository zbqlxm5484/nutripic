<template>
  <AuthLayout
    title="로그인"
    eyebrow="다시 오신 것을 환영합니다"
    description="추천 설문, 리포트 저장, 리포트 기반 채팅은 로그인 후 이용할 수 있습니다."
  >
    <RedirectNotice />

    <form class="auth-form" aria-label="로그인 폼">
      <label>
        아이디 또는 이메일
        <input type="text" name="login_id" autocomplete="username" placeholder="아이디 또는 이메일" />
      </label>
      <label>
        비밀번호
        <input type="password" name="password" autocomplete="current-password" placeholder="비밀번호" />
      </label>
      <FormErrorMessage message="" />
      <button type="button">로그인</button>
    </form>

    <p class="auth-link">
      아직 계정이 없나요?
      <RouterLink to="/signup">회원가입</RouterLink>
    </p>
  </AuthLayout>
</template>

<script setup>
import { AuthLayout, FormErrorMessage } from '../../../shared/components'

const RedirectNotice = {
  template: `
    <p class="redirect-notice">
      로그인 후 이전에 시도한 페이지로 돌아갈 수 있습니다.
    </p>
  `,
}
</script>

<style scoped>
.redirect-notice {
  margin: 0 0 18px;
  padding: 12px 14px;
  border-radius: 8px;
  background: #f0f6f3;
  color: #31443d;
}

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

.auth-form input {
  min-height: 42px;
  padding: 0 12px;
  border: 1px solid #c9d8d1;
  border-radius: 8px;
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
