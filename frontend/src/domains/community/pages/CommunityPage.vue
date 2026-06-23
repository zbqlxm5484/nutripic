<template>
  <AppLayout>
    <section class="community-page" aria-labelledby="community-title">
      <PageHeader
        title-id="community-title"
        eyebrow="커뮤니티"
        title="건강 고민과 영양제 경험 공유"
        description="목록과 상세 조회는 비회원도 가능하며, 작성과 댓글은 로그인이 필요합니다."
      >
        <template #actions>
        <BaseButton to="/community/new" variant="primary">게시글 작성</BaseButton>
        </template>
      </PageHeader>

      <form class="search-bar" aria-label="게시글 검색">
        <input class="form-control" type="search" name="search" placeholder="검색어 입력" />
        <select class="form-control" name="sort">
          <option value="latest">최신순</option>
          <option value="popular">추천순</option>
        </select>
        <BaseButton>검색</BaseButton>
      </form>

      <EmptyState
        title="게시글 목록 영역"
        description="API 연결 후 카테고리, 제목, 작성자, 댓글 수, 추천 수와 상세 이동 링크를 표시합니다."
      />
    </section>
  </AppLayout>
</template>

<script setup>
import { AppLayout, BaseButton, EmptyState, PageHeader } from '../../../shared/components'
</script>

<style scoped>
.community-page {
  display: grid;
  gap: 20px;
}

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

@media (max-width: 760px) {
  .search-bar {
    grid-template-columns: 1fr;
  }
}
</style>
