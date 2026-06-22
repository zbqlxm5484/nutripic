<template>
  <AppLayout>
    <section class="mypage-layout" aria-labelledby="mypage-layout-title">
      <aside class="mypage-layout__side">
        <p class="mypage-layout__eyebrow">마이페이지</p>
        <h1 id="mypage-layout-title">{{ title }}</h1>
        <nav aria-label="마이페이지 메뉴">
          <RouterLink to="/mypage">내 활동</RouterLink>
          <RouterLink to="/mypage/profile">회원 정보 수정</RouterLink>
          <RouterLink to="/reports">추천 기록</RouterLink>
        </nav>
      </aside>
      <div class="mypage-layout__content">
        <slot />
      </div>
    </section>
  </AppLayout>
</template>

<script setup>
import AppLayout from './AppLayout.vue'

defineProps({
  title: {
    type: String,
    default: '내 정보와 추천 기록',
  },
})
</script>

<style scoped>
.mypage-layout {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  gap: 28px;
  align-items: start;
}

.mypage-layout__side {
  display: grid;
  gap: 16px;
}

.mypage-layout__eyebrow {
  margin: 0;
  color: #4e6f61;
  font-weight: 700;
}

.mypage-layout__side h1 {
  margin: 0;
  font-size: 1.75rem;
}

.mypage-layout__side nav,
.mypage-layout__content {
  display: grid;
  gap: 14px;
}

.mypage-layout__side a {
  color: #31443d;
  text-decoration: none;
}

@media (max-width: 760px) {
  .mypage-layout {
    grid-template-columns: 1fr;
  }
}
</style>
