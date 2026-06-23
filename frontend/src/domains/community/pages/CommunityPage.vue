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

      <form class="search-bar" aria-label="게시글 정렬" @submit.prevent="applyOrdering">
        <select v-model="selectedOrdering" class="form-control" name="ordering">
          <option value="latest">최신순</option>
          <option value="likes">추천순</option>
        </select>
        <BaseButton>적용</BaseButton>
      </form>

      <LoadingState v-if="isLoading" label="게시글 목록을 불러오는 중입니다" />

      <ErrorState
        v-else-if="loadError"
        title="게시글 목록을 불러오지 못했습니다"
        :description="loadError"
      >
        <template #action>
          <BaseButton size="sm" @click="loadPosts">다시 시도</BaseButton>
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
          <article v-for="post in posts" :key="post.id" class="post-card">
            <div>
              <p>{{ formatAuthor(post.author) }}</p>
              <h2>
                <RouterLink :to="`/community/${post.id}`">{{ post.title }}</RouterLink>
              </h2>
              <span>{{ formatDate(post.created_at) }}</span>
            </div>
            <dl class="post-card__stats">
              <div>
                <dt>추천</dt>
                <dd>{{ post.like_count ?? 0 }}</dd>
              </div>
              <div>
                <dt>댓글</dt>
                <dd>{{ post.comment_count ?? 0 }}</dd>
              </div>
            </dl>
          </article>
        </div>

        <nav class="pagination" aria-label="게시글 페이지">
          <BaseButton size="sm" :disabled="currentPage <= 1" @click="setPage(currentPage - 1)">
            이전
          </BaseButton>
          <span>{{ currentPage }}페이지 · 총 {{ totalCount }}개</span>
          <BaseButton size="sm" :disabled="!hasNextPage" @click="setPage(currentPage + 1)">
            다음
          </BaseButton>
        </nav>
      </template>
    </section>
  </AppLayout>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { communityApi } from '../../../shared/api'
import { AppLayout, BaseButton, EmptyState, ErrorState, LoadingState, PageHeader } from '../../../shared/components'

const route = useRoute()
const router = useRouter()

const posts = ref([])
const isLoading = ref(true)
const loadError = ref('')
const selectedOrdering = ref(normalizeOrdering(route.query.ordering))
const totalCount = ref(0)
const hasNextPage = ref(false)

const currentPage = computed(() => normalizePage(route.query.page))

watch(
  () => [route.query.ordering, route.query.page],
  () => {
    selectedOrdering.value = normalizeOrdering(route.query.ordering)
    loadPosts()
  },
  { immediate: true },
)

async function loadPosts() {
  isLoading.value = true
  loadError.value = ''

  try {
    const response = await communityApi.listPosts({
      ordering: selectedOrdering.value,
      page: currentPage.value,
    })

    posts.value = Array.isArray(response?.results) ? response.results : []
    totalCount.value = response?.count ?? posts.value.length
    hasNextPage.value = Boolean(response?.next)
  } catch (error) {
    loadError.value = error?.message || '잠시 후 다시 시도해 주세요.'
  } finally {
    isLoading.value = false
  }
}

function applyOrdering() {
  router.replace({
    path: '/community',
    query: {
      ordering: selectedOrdering.value,
      page: 1,
    },
  })
}

function setPage(page) {
  router.replace({
    path: '/community',
    query: {
      ordering: selectedOrdering.value,
      page,
    },
  })
}

function normalizeOrdering(value) {
  return value === 'likes' ? 'likes' : 'latest'
}

function normalizePage(value) {
  const page = Number.parseInt(value, 10)
  return Number.isFinite(page) && page > 0 ? page : 1
}

function formatAuthor(author) {
  return author?.username ? `작성자 ${author.username}` : '작성자 알 수 없음'
}

function formatDate(value) {
  if (!value) return '작성일 없음'

  return new Intl.DateTimeFormat('ko-KR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}
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
  grid-template-columns: minmax(0, 180px) auto;
  gap: 10px;
  justify-content: start;
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
  display: flex;
  justify-content: space-between;
  gap: 16px;
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

.post-card__stats {
  display: flex;
  gap: 16px;
  margin: 0;
  text-align: right;
}

.post-card__stats dt {
  color: #5b6b65;
  font-size: 0.875rem;
}

.post-card__stats dd {
  margin: 4px 0 0;
  color: #31443d;
  font-weight: 700;
}

.pagination {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  justify-content: center;
}

.pagination span {
  color: #5b6b65;
}

a {
  color: #165a46;
}

@media (max-width: 760px) {
  .search-bar {
    grid-template-columns: 1fr;
  }

  .post-card {
    flex-direction: column;
  }

  .post-card__stats {
    text-align: left;
  }
}
</style>
