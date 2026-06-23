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

      <LoadingState v-if="isInitialLoading" label="게시글 목록을 불러오는 중입니다" />

      <ErrorState
        v-else-if="loadError && posts.length === 0"
        title="게시글 목록을 불러오지 못했습니다"
        :description="loadError"
      >
        <template #action>
          <BaseButton size="sm" @click="loadInitialPosts">다시 시도</BaseButton>
        </template>
      </ErrorState>

      <EmptyState
        v-else-if="posts.length === 0"
        title="게시글이 없습니다"
        description="첫 번째 건강 고민이나 영양제 경험을 공유해 보세요."
      >
        <template #action>
          <BaseButton to="/community/new">게시글 작성</BaseButton>
        </template>
      </EmptyState>

      <template v-else>
        <div class="post-list" aria-live="polite">
          <article v-for="post in posts" :key="post.id" class="thread-post">
            <div class="thread-post__rail" aria-hidden="true">
              <span class="thread-post__avatar">{{ getAuthorInitial(post.author) }}</span>
              <span class="thread-post__line"></span>
            </div>
            <div class="thread-post__body">
              <p class="thread-post__meta">
                <strong>{{ formatAuthor(post.author) }}</strong>
                <span>{{ formatDate(post.created_at) }}</span>
              </p>
              <h2>
                <RouterLink :to="`/community/${post.id}`">{{ post.title }}</RouterLink>
              </h2>
              <p v-if="post.content" class="thread-post__content">{{ truncateContent(post.content) }}</p>
              <RouterLink class="thread-post__reply" :to="`/community/${post.id}`">
                답글 {{ post.comment_count ?? 0 }}개 보기
              </RouterLink>
            </div>
          </article>
        </div>

        <ErrorState
          v-if="loadError"
          title="다음 게시글을 불러오지 못했습니다"
          :description="loadError"
        >
          <template #action>
            <BaseButton size="sm" @click="loadMorePosts">다시 시도</BaseButton>
          </template>
        </ErrorState>

        <div ref="sentinel" class="feed-sentinel" aria-hidden="true"></div>

        <div class="feed-status" role="status">
          <LoadingState v-if="isLoadingMore" label="다음 게시글을 불러오는 중입니다" />
          <BaseButton v-else-if="hasMore" size="sm" @click="loadMorePosts">더 보기</BaseButton>
          <span v-else>모든 게시글을 확인했습니다.</span>
        </div>
      </template>
    </section>
  </AppLayout>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { communityApi } from '../../../shared/api'
import { AppLayout, BaseButton, EmptyState, ErrorState, LoadingState, PageHeader } from '../../../shared/components'
import { useThreadFeed } from '../composables/useThreadFeed'

const route = useRoute()

const {
  items: posts,
  isInitialLoading,
  isLoadingMore,
  loadError,
  hasMore,
  sentinel,
  loadInitialItems: loadInitialPosts,
  loadMoreItems: loadMorePosts,
} = useThreadFeed({
  loadItems: communityApi.listPosts,
  initialQuery: {
    ordering: 'latest',
  },
  getRouteKey: () => route.fullPath,
})

function formatAuthor(author) {
  return author?.username || '알 수 없음'
}

function getAuthorInitial(author) {
  return formatAuthor(author).slice(0, 1).toUpperCase()
}

function formatDate(value) {
  if (!value) return '작성일 없음'

  return new Intl.DateTimeFormat('ko-KR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function truncateContent(value) {
  const normalized = String(value).replace(/\s+/g, ' ').trim()
  return normalized.length > 160 ? `${normalized.slice(0, 160)}...` : normalized
}

</script>

<style scoped>
.community-page {
  display: grid;
  gap: 20px;
}

.post-list {
  display: grid;
  margin: 0 auto;
  width: min(100%, 680px);
}

.thread-post {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  gap: 14px;
  padding: 18px 0;
  border-bottom: 1px solid #dde7e2;
  background: #ffffff;
}

.thread-post__rail {
  display: grid;
  justify-items: center;
  grid-template-rows: 40px 1fr;
}

.thread-post__avatar {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 999px;
  background: #e4f1eb;
  color: #165a46;
  font-weight: 800;
}

.thread-post__line {
  width: 2px;
  min-height: 100%;
  background: #edf2ef;
}

.thread-post__body {
  display: grid;
  gap: 8px;
}

.thread-post__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: baseline;
  margin: 0;
  color: #5b6b65;
  font-size: 0.875rem;
}

.thread-post__meta strong {
  color: #31443d;
}

.thread-post h2 {
  margin: 0;
  font-size: 1.125rem;
  line-height: 1.4;
}

.thread-post__content {
  display: -webkit-box;
  overflow: hidden;
  margin: 0;
  color: #31443d;
  line-height: 1.6;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 4;
}

.thread-post__reply {
  width: fit-content;
  color: #5b6b65;
  font-size: 0.875rem;
  font-weight: 700;
}

.feed-sentinel {
  height: 1px;
}

.feed-status {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  justify-content: center;
  min-height: 48px;
}

.feed-status span {
  color: #5b6b65;
}

a {
  color: #165a46;
}

@media (max-width: 760px) {
  .thread-post {
    grid-template-columns: 40px minmax(0, 1fr);
    gap: 10px;
  }
}
</style>
