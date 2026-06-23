<template>
  <ReportLayout title="방금 생성된 추천 리포트">
    <template #actions>
      <div class="report-actions">
        <BaseButton to="/reports">목록 이동</BaseButton>
        <BaseButton to="/survey">다시 설문</BaseButton>
      </div>
    </template>

    <ContentSection title-id="input-summary-title" title="사용자 입력 요약">
      <p>API 연결 후 나이, 성별, 건강 목표, 복용 약, 특이사항 요약을 표시합니다.</p>
    </ContentSection>

    <ContentSection title-id="ingredient-list-title" title="핵심 추천 성분">
      <p>추천 성분명, 추천 이유, 백엔드가 검증한 `iherb_url`이 있는 경우의 외부 링크를 표시합니다.</p>
    </ContentSection>

    <ContentSection title-id="detail-title" title="성분별 상세">
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
    </ContentSection>

    <ContentSection title-id="lifestyle-title" title="생활 습관 관리 팁">
      <ul>
        <li>수면 시간과 카페인 섭취 시간을 함께 기록합니다.</li>
        <li>피로가 지속되거나 악화되면 전문가 상담을 우선합니다.</li>
      </ul>
    </ContentSection>

    <MedicalDisclaimer />

    <template #aside>
      <ReportChatPanel
        title="리포트 기반 채팅"
        description="리포트에 포함된 성분, 복용법, 부작용, 주의사항 범위 안에서 질문할 수 있습니다."
        placeholder="리포트 내용에 대해 질문하세요."
        :messages="chatMessages"
      />
    </template>
  </ReportLayout>
</template>

<script setup>
import { BaseButton, ContentSection, MedicalDisclaimer, ReportChatPanel, ReportLayout } from '../../../shared/components'

const chatMessages = [
  { id: 'empty', text: '채팅 메시지 목록 영역' },
]
</script>

<style scoped>
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
  gap: 12px;
  margin: 0;
  padding-left: 20px;
}

p {
  margin: 0;
  color: #5b6b65;
  line-height: 1.6;
}

.report-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

</style>
