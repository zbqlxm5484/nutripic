<template>
  <ReportLayout title="방금 생성된 추천 리포트">
    <template #actions>
      <div class="report-actions">
        <BaseButton to="/reports">목록 이동</BaseButton>
        <BaseButton to="/survey">다시 설문</BaseButton>
      </div>
    </template>

    <section class="report-section" aria-labelledby="input-summary-title">
      <h2 id="input-summary-title">사용자 입력 요약</h2>
      <p>API 연결 후 나이, 성별, 건강 목표, 복용 약, 특이사항 요약을 표시합니다.</p>
    </section>

    <section class="report-section" aria-labelledby="ingredient-list-title">
      <h2 id="ingredient-list-title">핵심 추천 성분</h2>
      <p>추천 성분명, 추천 이유, 백엔드가 검증한 `iherb_url`이 있는 경우의 외부 링크를 표시합니다.</p>
    </section>

    <section class="report-section" aria-labelledby="detail-title">
      <h2 id="detail-title">성분별 상세</h2>
      <dl class="summary-list">
        <div>
          <dt>추천 이유</dt>
          <dd>API 연결 후 성분별 추천 이유를 표시합니다.</dd>
        </div>
        <div>
          <dt>기능성</dt>
          <dd>기능성 설명 영역입니다.</dd>
        </div>
        <div>
          <dt>복용법 및 권장 용량</dt>
          <dd>일일섭취량과 복용법 안내 영역입니다.</dd>
        </div>
        <div>
          <dt>주의사항과 부작용 가능성</dt>
          <dd>사용자 입력 조건과 연결된 안전 안내 영역입니다.</dd>
        </div>
      </dl>
    </section>

    <section class="report-section" aria-labelledby="lifestyle-title">
      <h2 id="lifestyle-title">생활 습관 관리 팁</h2>
      <ul>
        <li>수면 시간과 카페인 섭취 시간을 함께 기록합니다.</li>
        <li>피로가 지속되거나 악화되면 전문가 상담을 우선합니다.</li>
      </ul>
    </section>

    <MedicalDisclaimer />

    <template #aside>
      <section class="chat-panel" aria-labelledby="chat-title">
        <h2 id="chat-title">리포트 기반 채팅</h2>
        <p>리포트에 포함된 성분, 복용법, 부작용, 주의사항 범위 안에서 질문할 수 있습니다.</p>
        <div class="chat-message">채팅 메시지 목록 영역</div>
        <textarea rows="4" placeholder="리포트 내용에 대해 질문하세요." />
        <BaseButton variant="primary">질문 보내기</BaseButton>
      </section>
    </template>
  </ReportLayout>
</template>

<script setup>
import { BaseButton, MedicalDisclaimer, ReportLayout } from '../../../shared/components'
</script>

<style scoped>
.report-section,
.chat-panel {
  padding: 24px;
  border: 1px solid #dde7e2;
  border-radius: 8px;
  background: #ffffff;
}

.report-section h2,
.chat-panel h2 {
  margin: 0 0 16px;
  font-size: 1.25rem;
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

.report-section ul {
  display: grid;
  gap: 12px;
  margin: 0;
  padding-left: 20px;
}

.report-section p,
.chat-panel p {
  color: #5b6b65;
  line-height: 1.6;
}

.report-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chat-panel {
  display: grid;
  gap: 14px;
}

.chat-message {
  padding: 12px;
  border-radius: 8px;
  background: #f0f6f3;
  color: #31443d;
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

</style>
