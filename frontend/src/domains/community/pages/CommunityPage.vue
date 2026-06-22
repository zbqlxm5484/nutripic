<template>
  <AppLayout>
    <section class="community-page" aria-labelledby="community-title">
      <header class="community-page__header">
        <div>
          <p>커뮤니티</p>
          <h1 id="community-title">건강 고민과 영양제 경험 공유</h1>
          <span>목록과 상세 조회는 비회원도 가능하며, 작성과 댓글은 로그인이 필요합니다.</span>
        </div>
        <RouterLink class="button button--primary" to="/community/new">게시글 작성</RouterLink>
      </header>

      <form class="search-bar" aria-label="게시글 검색">
        <input type="search" name="search" placeholder="검색어 입력" />
        <select name="sort">
          <option value="latest">최신순</option>
          <option value="popular">추천순</option>
        </select>
        <button type="button">검색</button>
      </form>

      <EmptyState
        title="게시글 목록 영역"
        description="API 연결 후 카테고리, 제목, 작성자, 댓글 수, 추천 수와 상세 이동 링크를 표시합니다."
      />
    </section>
  </AppLayout>
</template>

<script setup>
import { AppLayout, EmptyState } from '../../../shared/components'
</script>

<style scoped>
.community-page {
  display: grid;
  gap: 20px;
}

.community-page__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.community-page__header p {
  margin: 0 0 8px;
  color: #4e6f61;
  font-weight: 700;
}

.community-page__header h1 {
  margin: 0;
  font-size: 2rem;
}

.community-page__header span,
.post-card span {
  display: block;
  margin-top: 8px;
  color: #5b6b65;
}

.search-bar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 160px auto;
  gap: 10px;
  padding: 16px;
  border: 1px solid #dde7e2;
  border-radius: 8px;
  background: #ffffff;
}

.search-bar input,
.search-bar select {
  min-height: 40px;
  padding: 0 12px;
  border: 1px solid #c9d8d1;
  border-radius: 8px;
  background: #ffffff;
  font: inherit;
}

.post-list {
  display: grid;
  gap: 14px;
}

.post-card {
  padding: 22px;
  border: 1px solid #dde7e2;
  border-radius: 8px;
  background: #ffffff;
}

.post-card p {
  margin: 0 0 8px;
  color: #4e6f61;
  font-weight: 700;
}

.post-card h2 {
  margin: 0;
  font-size: 1.25rem;
}

a {
  color: #165a46;
}

.button,
.search-bar button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
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

.button--primary {
  border-color: #165a46;
  background: #165a46;
  color: #ffffff;
}

@media (max-width: 760px) {
  .community-page__header,
  .search-bar {
    grid-template-columns: 1fr;
  }

  .community-page__header {
    flex-direction: column;
  }
}
</style>
