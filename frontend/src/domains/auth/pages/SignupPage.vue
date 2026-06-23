<template>
  <AuthLayout
    title="회원가입"
    eyebrow="리포트 저장을 위한 계정 생성"
    description="기본 정보는 성분 추천 조건과 추천 기록 관리에 사용됩니다."
  >
    <BaseForm aria-label="회원가입 폼">
      <FormField label="아이디 또는 이메일">
        <input class="form-control" type="email" name="email" autocomplete="email" placeholder="아이디 또는 이메일" />
      </FormField>
      <FormField label="비밀번호">
        <input class="form-control" type="password" name="password" autocomplete="new-password" placeholder="비밀번호" />
      </FormField>
      <FormField label="비밀번호 확인">
        <input class="form-control" type="password" name="password_confirm" autocomplete="new-password" placeholder="비밀번호 확인" />
      </FormField>
      <FormField label="나이">
        <input class="form-control" type="number" name="age" min="14" max="120" placeholder="나이" />
      </FormField>
      <FormField label="성별">
        <select class="form-control" name="gender">
          <option value="">선택</option>
          <option value="female">여성</option>
          <option value="male">남성</option>
          <option value="other">기타 또는 응답하지 않음</option>
        </select>
      </FormField>
      <FormErrorMessage message="" />
      <BaseButton class="auth-submit" variant="primary">회원가입</BaseButton>
    </BaseForm>

    <p class="auth-link">
      이미 계정이 있나요?
      <RouterLink to="/login">로그인</RouterLink>
    </p>
  </AuthLayout>
</template>

<script setup>
import { AuthLayout, BaseButton, BaseForm, FormErrorMessage, FormField } from '../../../shared/components'
</script>

<style scoped>
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
