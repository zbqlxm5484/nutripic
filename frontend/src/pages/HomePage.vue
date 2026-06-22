<template>
  <AppLayout>
    <section class="hero-section" aria-labelledby="home-title">
      <p class="hero-section__eyebrow">성분 중심 AI 리포트</p>
      <h1 id="home-title">Neutripic</h1>
      <p class="hero-section__description">
        건강 목표, 복용 약, 특이사항을 바탕으로 제품이 아닌 성분 중심의 개인화 리포트를 제공합니다.
      </p>
      <div class="hero-section__actions">
        <RouterLink class="button button--primary" to="/login?redirect_to=/survey">추천 시작</RouterLink>
        <RouterLink class="button" to="/community">커뮤니티 보기</RouterLink>
      </div>
    </section>

    <section class="section-grid" aria-label="서비스 가치">
      <article class="info-block">
        <h2>RAG 기반 근거</h2>
        <p>iDISK와 건강기능식품 기능성원료 인정현황 데이터를 바탕으로 성분 추천 이유를 설명합니다.</p>
      </article>
      <article class="info-block">
        <h2>안전 가드레일</h2>
        <p>복용 약, 특이사항, 서비스 범위를 확인해 고위험 요청은 안전 안내로 전환합니다.</p>
      </article>
      <article class="info-block">
        <h2>검증된 성분 링크</h2>
        <p>iHerb는 상품 정보가 아니라 백엔드가 검증한 성분 외부 링크로만 연결합니다.</p>
      </article>
    </section>

    <section class="flow-preview" aria-labelledby="flow-title">
      <h2 id="flow-title">추천 리포트 흐름</h2>
      <ol>
        <li>건강 목표와 우선순위를 선택합니다.</li>
        <li>복용 약과 특이사항을 입력합니다.</li>
        <li>성분 중심 리포트와 주의사항을 확인합니다.</li>
        <li>리포트 기반 채팅으로 후속 질문을 남깁니다.</li>
      </ol>
    </section>

    <SafetyNotice />

    <section class="community-preview" aria-labelledby="community-title">
      <div>
        <h2 id="community-title">커뮤니티</h2>
        <p>건강 고민과 영양제 경험을 공유하는 공간입니다. 목록과 상세 조회는 비회원도 가능합니다.</p>
      </div>
      <RouterLink class="button" to="/community">게시글 보러가기</RouterLink>
    </section>
  </AppLayout>
</template>

<script setup>
import { AppLayout, SafetyNotice } from '../shared/components'
</script>

<style scoped>
.hero-section {
  display: grid;
  gap: 18px;
  padding: 56px 0 48px;
}

.hero-section__eyebrow {
  margin: 0;
  color: #4e6f61;
  font-weight: 700;
}

.hero-section h1 {
  margin: 0;
  color: #165a46;
  font-size: 3rem;
}

.hero-section__description {
  max-width: 720px;
  margin: 0;
  color: #31443d;
  font-size: 1.125rem;
  line-height: 1.7;
}

.hero-section__actions,
.community-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 16px;
  border: 1px solid #b9cbc3;
  border-radius: 8px;
  color: #165a46;
  font-weight: 700;
  text-decoration: none;
}

.button--primary {
  border-color: #165a46;
  background: #165a46;
  color: #ffffff;
}

.section-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.info-block,
.flow-preview,
.community-preview {
  padding: 24px;
  border: 1px solid #dde7e2;
  border-radius: 8px;
  background: #ffffff;
}

.info-block h2,
.flow-preview h2,
.community-preview h2 {
  margin: 0 0 10px;
  font-size: 1.125rem;
}

.info-block p,
.community-preview p {
  margin: 0;
  color: #5b6b65;
  line-height: 1.6;
}

.flow-preview {
  margin-bottom: 24px;
}

.flow-preview ol {
  display: grid;
  gap: 10px;
  margin: 0;
  padding-left: 20px;
  color: #31443d;
}

.community-preview {
  justify-content: space-between;
  margin-top: 24px;
}

@media (max-width: 820px) {
  .section-grid {
    grid-template-columns: 1fr;
  }

  .hero-section h1 {
    font-size: 2.375rem;
  }
}
</style>
