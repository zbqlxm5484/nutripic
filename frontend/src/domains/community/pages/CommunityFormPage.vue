<template>
  <section class="community-form-page" :aria-labelledby="titleId">
    <header>
      <p>커뮤니티</p>
      <h1 :id="titleId">{{ title }}</h1>
      <span>게시글 작성과 수정은 로그인 상태에서만 가능합니다.</span>
    </header>

    <form class="community-form" aria-label="커뮤니티 게시글 폼">
      <label>
        카테고리
        <select name="category">
          <option value="sleep">수면</option>
          <option value="fatigue">피로</option>
          <option value="immune">면역</option>
          <option value="etc">기타</option>
        </select>
      </label>
      <label>
        제목
        <input type="text" name="title" placeholder="제목을 입력하세요" />
      </label>
      <label>
        내용
        <textarea rows="10" name="content" placeholder="건강 고민이나 영양제 경험을 공유하세요." />
      </label>
      <FormErrorMessage message="" />
      <div class="community-form__actions">
        <button type="button">{{ submitLabel }}</button>
        <RouterLink to="/community">취소</RouterLink>
      </div>
    </form>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { FormErrorMessage } from '../../../shared/components'

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

.community-form {
  display: grid;
  gap: 16px;
  padding: 24px;
  border: 1px solid #dde7e2;
  border-radius: 8px;
  background: #ffffff;
}

.community-form label {
  display: grid;
  gap: 8px;
  color: #31443d;
  font-weight: 700;
}

.community-form input,
.community-form select,
.community-form textarea {
  padding: 0 12px;
  border: 1px solid #c9d8d1;
  border-radius: 8px;
  background: #ffffff;
  font: inherit;
}

.community-form input,
.community-form select {
  min-height: 42px;
}

.community-form textarea {
  padding-top: 12px;
  resize: vertical;
}

.community-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.community-form__actions button,
.community-form__actions a {
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

.community-form__actions button {
  border-color: #165a46;
  background: #165a46;
  color: #ffffff;
}
</style>
