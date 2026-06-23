<template>
  <MyPageLayout title="회원 정보 수정">
    <BaseForm aria-label="회원 정보 수정 폼">
      <FormField label="나이">
        <input class="form-control" type="number" name="age" min="14" max="120" placeholder="나이" />
      </FormField>
      <FormField label="성별">
        <select class="form-control" name="gender">
          <option value="female">여성</option>
          <option value="male">남성</option>
          <option value="other">기타 또는 응답하지 않음</option>
        </select>
      </FormField>
      <FormField label="새 비밀번호">
        <input class="form-control" type="password" name="password" autocomplete="new-password" placeholder="변경할 때만 입력" />
      </FormField>
      <FormErrorMessage message="" />
      <FormActions>
        <BaseButton variant="primary">저장</BaseButton>
        <BaseButton to="/mypage">취소</BaseButton>
      </FormActions>
    </BaseForm>
  </MyPageLayout>
</template>

<script setup>
import { BaseButton, BaseForm, FormActions, FormErrorMessage, FormField, MyPageLayout } from '../../../shared/components'
</script>
