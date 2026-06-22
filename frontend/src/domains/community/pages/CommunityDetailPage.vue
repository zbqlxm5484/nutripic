<template>
  <AppLayout>
    <article class="post-detail" aria-labelledby="post-title">
      <header class="post-detail__header">
        <p>카테고리 영역</p>
        <h1 id="post-title">게시글 제목 영역</h1>
        <span>작성자 · 작성일 · 추천 수 영역</span>
      </header>

      <section class="post-detail__body">
        <p>
          API 연결 후 게시글 본문을 표시합니다.
        </p>
      </section>

      <div class="post-detail__actions">
        <button type="button">추천</button>
        <button type="button">수정</button>
        <RouterLink to="/community">목록</RouterLink>
      </div>

      <section class="comments" aria-labelledby="comments-title">
        <h2 id="comments-title">댓글</h2>
        <article class="comment">
          <p>댓글 내용 영역입니다.</p>
          <span>댓글 작성자 영역</span>
        </article>
        <form class="comment-form" aria-label="댓글 작성">
          <textarea rows="4" placeholder="로그인 후 댓글을 작성할 수 있습니다." />
          <button type="button">댓글 작성</button>
        </form>
      </section>
    </article>
  </AppLayout>
</template>

<script setup>
import { AppLayout } from '../../../shared/components'
</script>

<style scoped>
.post-detail {
  display: grid;
  gap: 20px;
}

.post-detail__header,
.post-detail__body,
.comments {
  padding: 24px;
  border: 1px solid #dde7e2;
  border-radius: 8px;
  background: #ffffff;
}

.post-detail__header p {
  margin: 0 0 8px;
  color: #4e6f61;
  font-weight: 700;
}

.post-detail__header h1 {
  margin: 0;
  font-size: 2rem;
}

.post-detail__header span,
.comment span {
  display: block;
  margin-top: 8px;
  color: #5b6b65;
}

.post-detail__body p,
.comment p {
  margin: 0;
  color: #31443d;
  line-height: 1.7;
}

.post-detail__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.post-detail__actions button,
.post-detail__actions a,
.comment-form button {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 0 14px;
  border: 1px solid #c9d8d1;
  border-radius: 8px;
  background: #ffffff;
  color: #165a46;
  font: inherit;
  font-weight: 700;
  text-decoration: none;
}

.comments {
  display: grid;
  gap: 16px;
}

.comments h2 {
  margin: 0;
  font-size: 1.25rem;
}

.comment {
  padding: 16px;
  border-radius: 8px;
  background: #f0f6f3;
}

.comment-form {
  display: grid;
  gap: 10px;
}

.comment-form textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 12px;
  border: 1px solid #c9d8d1;
  border-radius: 8px;
  font: inherit;
  resize: vertical;
}
</style>
