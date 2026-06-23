<template>
  <section class="community-form-page" :aria-labelledby="titleId">
    <header>
      <p>커뮤니티</p>
      <h1 :id="titleId">{{ title }}</h1>
      <span>게시글 작성과 수정은 로그인 상태에서만 가능합니다.</span>
    </header>

    <BaseForm aria-label="커뮤니티 게시글 폼">
      <FormField label="카테고리">
        <select class="form-control" name="category">
          <option value="sleep">수면</option>
          <option value="fatigue">피로</option>
          <option value="immune">면역</option>
          <option value="etc">기타</option>
        </select>
      </FormField>
      <FormField label="제목">
        <input class="form-control" type="text" name="title" placeholder="제목을 입력하세요" />
      </FormField>
      <FormField label="내용">
        <textarea class="form-control" rows="10" name="content" placeholder="건강 고민이나 영양제 경험을 공유하세요." />
      </FormField>
      <FormErrorMessage message="" />
      <FormActions>
        <BaseButton variant="primary">{{ submitLabel }}</BaseButton>
        <BaseButton to="/community">취소</BaseButton>
      </FormActions>
    </BaseForm>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { BaseButton, BaseForm, FormActions, FormErrorMessage, FormField } from '../../../shared/components'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  submitLabel: {
    type: String,
    required: true,
  },
})

const titleId = computed(() => `community-form-${props.title.replace(/\s+/g, '-').toLowerCase()}`)
</script>

<style scoped>
.community-form-page {
  display: grid;
  gap: 20px;
}

.community-form-page header p {
  margin: 0 0 8px;
  color: #4e6f61;
  font-weight: 700;
}

.community-form-page header h1 {
  margin: 0;
  font-size: 2rem;
}

.community-form-page header span {
  display: block;
  margin-top: 8px;
  color: #5b6b65;
}

</style>
