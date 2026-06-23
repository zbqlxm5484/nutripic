<template>
  <ReportLayout title="저장된 추천 리포트 상세">
    <template #actions>
      <div class="report-actions">
        <BaseButton>제목 수정</BaseButton>
        <BaseButton variant="danger">삭제</BaseButton>
        <BaseButton to="/reports">목록 이동</BaseButton>
      </div>
    </template>

    <ContentSection title-id="report-header-title" title="리포트 제목 영역" eyebrow="생성일 영역">
      <p>API 연결 후 저장 리포트의 제목, 생성일, 액션을 표시합니다.</p>
    </ContentSection>

    <ContentSection title-id="summary-title" title="사용자 입력 요약">
      <p>건강 목표, 복용 약, 특이사항, 추가 입력 요약 영역입니다.</p>
    </ContentSection>

    <ContentSection title-id="ingredient-title" title="추천 성분 상세">
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
    </ContentSection>

    <ContentSection title-id="evidence-title" title="근거 출처와 생활 팁">
      <ul>
        <li>iDISK 증상/성분 데이터 기반 RAG 검색 결과</li>
        <li>건강기능식품 기능성원료 인정현황의 기능성 및 섭취 시 주의사항</li>
        <li>규칙적인 수면 시간과 복용 기록을 함께 관리합니다.</li>
      </ul>
    </ContentSection>

    <MedicalDisclaimer />

    <template #aside>
      <ReportChatPanel
        title="저장된 채팅"
        description="이 리포트 범위 안에서 후속 질문을 이어갈 수 있습니다."
        :messages="chatMessages"
      />
    </template>
  </ReportLayout>
</template>

<script setup>
import { BaseButton, ContentSection, MedicalDisclaimer, ReportChatPanel, ReportLayout } from '../../../shared/components'

const chatMessages = [
  { id: 'user', text: '사용자 메시지 영역', variant: 'user' },
  { id: 'ai', text: 'AI 답변 영역' },
]
</script>

<style scoped>
p {
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

ul {
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

</style>
