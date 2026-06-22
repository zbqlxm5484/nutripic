<template>
  <ReportLayout title="저장된 추천 리포트 상세">
    <template #actions>
      <div class="report-actions">
        <button type="button">제목 수정</button>
        <button type="button">삭제</button>
        <RouterLink to="/reports">목록 이동</RouterLink>
      </div>
    </template>

    <section class="report-section" aria-labelledby="report-header-title">
      <p class="report-date">생성일 영역</p>
      <h2 id="report-header-title">리포트 제목 영역</h2>
      <p>API 연결 후 저장 리포트의 제목, 생성일, 액션을 표시합니다.</p>
    </section>

    <section class="report-section" aria-labelledby="summary-title">
      <h2 id="summary-title">사용자 입력 요약</h2>
      <p>건강 목표, 복용 약, 특이사항, 추가 입력 요약 영역입니다.</p>
    </section>

    <section class="report-section" aria-labelledby="ingredient-title">
      <h2 id="ingredient-title">추천 성분 상세</h2>
      <dl class="summary-list">
        <div>
          <dt>성분명과 추천 이유</dt>
          <dd>성분별 추천 근거와 사용자 목표 연결 설명을 표시합니다.</dd>
        </div>
        <div>
          <dt>기능성</dt>
          <dd>식약처 기준 기능성 설명 영역입니다.</dd>
        </div>
        <div>
          <dt>복용법 및 권장 용량</dt>
          <dd>일일섭취량과 복용법 안내 영역입니다.</dd>
        </div>
        <div>
          <dt>부작용 가능성과 주의사항</dt>
          <dd>복용 약 또는 특이사항 관련 주의 문구를 표시합니다.</dd>
        </div>
        <div>
          <dt>성분 외부 링크</dt>
          <dd>`iherb_url`이 있는 성분만 검증된 외부 링크로 표시합니다.</dd>
        </div>
      </dl>
    </section>

    <section class="report-section" aria-labelledby="evidence-title">
      <h2 id="evidence-title">근거 출처와 생활 팁</h2>
      <ul>
        <li>iDISK 증상/성분 데이터 기반 RAG 검색 결과</li>
        <li>건강기능식품 기능성원료 인정현황의 기능성 및 섭취 시 주의사항</li>
        <li>규칙적인 수면 시간과 복용 기록을 함께 관리합니다.</li>
      </ul>
    </section>

    <MedicalDisclaimer />

    <template #aside>
      <section class="chat-panel" aria-labelledby="chat-title">
        <h2 id="chat-title">저장된 채팅</h2>
        <p>이 리포트 범위 안에서 후속 질문을 이어갈 수 있습니다.</p>
        <div class="chat-message chat-message--user">사용자 메시지 영역</div>
        <div class="chat-message">AI 답변 영역</div>
        <textarea rows="4" placeholder="리포트 기반 질문을 입력하세요." />
        <button type="button">질문 보내기</button>
      </section>
    </template>
  </ReportLayout>
</template>

<script setup>
import { MedicalDisclaimer, ReportLayout } from '../../../shared/components'
</script>

<style scoped>
.report-section,
.chat-panel {
  padding: 24px;
  border: 1px solid #dde7e2;
  border-radius: 8px;
  background: #ffffff;
}

.report-date {
  margin: 0 0 8px;
  color: #5b6b65;
}

.report-section h2,
.chat-panel h2 {
  margin: 0 0 16px;
  font-size: 1.25rem;
}

.report-section p {
  margin: 0;
  color: #5b6b65;
  line-height: 1.6;
}

.summary-list {
  display: grid;
  gap: 12px;
  margin: 0;
}

.summary-list div {
  display: grid;
  gap: 4px;
}

dt {
  color: #5b6b65;
  font-size: 0.875rem;
}

dd {
  margin: 0;
  color: #31443d;
}

.report-actions a {
  color: #165a46;
  font-weight: 700;
}

.report-section ul {
  display: grid;
  gap: 10px;
  margin: 0;
  padding-left: 20px;
  color: #31443d;
}

.report-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.report-actions a,
.report-actions button,
.chat-panel button {
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

.chat-panel {
  display: grid;
  gap: 14px;
}

.chat-panel p {
  margin: 0;
  color: #5b6b65;
  line-height: 1.6;
}

.chat-message {
  padding: 12px;
  border-radius: 8px;
  background: #f0f6f3;
  color: #31443d;
}

.chat-message--user {
  background: #edf2ef;
}

.chat-panel textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 12px;
  border: 1px solid #c9d8d1;
  border-radius: 8px;
  font: inherit;
  resize: vertical;
}

.chat-panel button {
  justify-content: center;
  border-color: #165a46;
  background: #165a46;
  color: #ffffff;
}
</style>
