<template>
  <AuthLayout
    title="로그인"
    eyebrow="다시 오신 것을 환영합니다"
    description="추천 설문, 리포트 저장, 리포트 기반 채팅은 로그인 후 이용할 수 있습니다."
  >
    <RedirectNotice />

    <BaseForm aria-label="로그인 폼">
      <FormField label="아이디 또는 이메일">
        <input class="form-control" type="text" name="login_id" autocomplete="username" placeholder="아이디 또는 이메일" />
      </FormField>
      <FormField label="비밀번호">
        <input class="form-control" type="password" name="password" autocomplete="current-password" placeholder="비밀번호" />
      </FormField>
      <FormErrorMessage message="" />
      <BaseButton class="auth-submit" variant="primary">로그인</BaseButton>
    </BaseForm>

    <p class="auth-link">
      아직 계정이 없나요?
      <RouterLink to="/signup">회원가입</RouterLink>
    </p>
  </AuthLayout>
</template>

<script setup>
import { AuthLayout, BaseButton, BaseForm, FormErrorMessage, FormField } from '../../../shared/components'

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

.auth-submit {
  min-height: 44px;
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
