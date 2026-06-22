<template>
  <div class="app-layout">
    <header class="app-layout__header">
      <RouterLink class="app-layout__brand" to="/">Neutripic</RouterLink>
      <nav class="app-layout__nav" aria-label="주요 메뉴">
        <RouterLink to="/survey">추천 설문</RouterLink>
        <RouterLink to="/reports">추천 기록</RouterLink>
        <RouterLink to="/community">커뮤니티</RouterLink>
        <RouterLink to="/mypage">마이페이지</RouterLink>
      </nav>
      <RouterLink class="app-layout__login" to="/login">로그인</RouterLink>
    </header>

    <main class="app-layout__main">
      <slot />
    </main>

    <footer class="app-layout__footer">
      건강기능식품 성분 정보를 제공하며, 진단이나 처방을 대체하지 않습니다.
    </footer>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: #f8faf9;
  color: #17231f;
}

.app-layout__header {
  display: flex;
  align-items: center;
  gap: 24px;
  min-height: 64px;
  padding: 0 32px;
  border-bottom: 1px solid #dde7e2;
  background: #ffffff;
}

.app-layout__brand {
  font-weight: 700;
  color: #165a46;
  text-decoration: none;
}

.app-layout__nav {
  display: flex;
  flex: 1;
  flex-wrap: wrap;
  gap: 16px;
}

.app-layout__nav a,
.app-layout__login {
  color: #31443d;
  text-decoration: none;
}

.app-layout__main {
  width: min(1120px, calc(100% - 32px));
  margin: 0 auto;
  padding: 40px 0;
}

.app-layout__footer {
  padding: 24px 32px 32px;
  border-top: 1px solid #dde7e2;
  color: #5b6b65;
  text-align: center;
}

@media (max-width: 720px) {
  .app-layout__header {
    align-items: flex-start;
    flex-direction: column;
    gap: 12px;
    padding: 16px;
  }

  .app-layout__nav {
    gap: 10px 14px;
  }
}
</style>
