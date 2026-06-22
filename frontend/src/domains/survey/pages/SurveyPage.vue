<template>
  <SurveyLayout>
    <section class="progress-panel" aria-labelledby="survey-progress-title">
      <div>
        <p class="progress-panel__step">1 / 4</p>
        <h2 id="survey-progress-title">건강 목표 선택</h2>
      </div>
      <progress max="4" value="1">1 / 4</progress>
    </section>

    <section class="survey-section" aria-labelledby="health-goal-title">
      <header>
        <h2 id="health-goal-title">건강 목표</h2>
        <p>1개 이상, 최대 5개까지 선택할 수 있습니다.</p>
      </header>
      <div class="chip-grid">
        <label v-for="goal in healthGoals" :key="goal">
          <input type="checkbox" name="health_goals" :value="goal" />
          <span>{{ goal }}</span>
        </label>
      </div>
    </section>

    <section class="survey-section" aria-labelledby="priority-title">
      <header>
        <h2 id="priority-title">목표 우선순위</h2>
        <p>선택한 건강 목표의 중요도를 중복 없이 지정합니다.</p>
      </header>
      <ol class="priority-list">
        <li>선택한 목표가 여기에 표시됩니다.</li>
        <li>드래그 또는 순서 선택 UI는 상태 연결 시 추가합니다.</li>
      </ol>
    </section>

    <section class="survey-section" aria-labelledby="medication-title">
      <header>
        <h2 id="medication-title">복용 약</h2>
        <p>해당 항목이 없으면 미선택 또는 없음 상태를 명확히 구분합니다.</p>
      </header>
      <div class="chip-grid">
        <label v-for="medication in medications" :key="medication">
          <input type="checkbox" name="medications" :value="medication" />
          <span>{{ medication }}</span>
        </label>
      </div>
    </section>

    <section class="survey-section" aria-labelledby="condition-title">
      <header>
        <h2 id="condition-title">특이사항</h2>
        <p>임신/수유, 간/신장 질환, 항응고제 등 고위험 항목은 안전 안내를 강화합니다.</p>
      </header>
      <div class="chip-grid">
        <label v-for="condition in specialConditions" :key="condition">
          <input type="checkbox" name="special_conditions" :value="condition" />
          <span>{{ condition }}</span>
        </label>
      </div>
    </section>

    <section class="survey-section" aria-labelledby="additional-info-title">
      <header>
        <h2 id="additional-info-title">추가 정보</h2>
        <p>선택지에 없는 복용 약, 질환, 알레르기, 생활 습관을 입력합니다.</p>
      </header>
      <textarea
        name="additional_info"
        rows="5"
        placeholder="과도한 개인정보는 입력하지 마세요."
      />
    </section>

    <SafetyNotice />

    <div class="action-bar" aria-label="설문 이동">
      <button type="button">이전</button>
      <button type="button">다음</button>
      <RouterLink class="action-bar__primary" to="/reports/generating">리포트 생성 요청</RouterLink>
    </div>
  </SurveyLayout>
</template>

<script setup>
import { SafetyNotice, SurveyLayout } from '../../../shared/components'

const healthGoals = ['피로', '수면', '눈 건강', '장 건강', '면역', '피부', '스트레스', '혈행', '관절', '기억력']
const medications = ['고혈압약', '당뇨약', '항응고제', '항우울제', '피임약', '진통소염제', '위장약', '갑상선약']
const specialConditions = ['임신 또는 수유', '간 질환', '신장 질환', '심혈관 질환', '알레르기', '수술 예정', '미성년자 또는 고령자']
</script>

<style scoped>
.progress-panel,
.survey-section,
.action-bar {
  padding: 24px;
  border: 1px solid #dde7e2;
  border-radius: 8px;
  background: #ffffff;
}

.progress-panel {
  display: grid;
  gap: 14px;
}

.progress-panel__step {
  margin: 0 0 6px;
  color: #4e6f61;
  font-weight: 700;
}

.progress-panel h2,
.survey-section h2 {
  margin: 0;
  font-size: 1.25rem;
}

.progress-panel progress {
  width: 100%;
  height: 10px;
}

.survey-section header {
  margin-bottom: 16px;
}

.survey-section p {
  margin: 8px 0 0;
  color: #5b6b65;
  line-height: 1.6;
}

.chip-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip-grid label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid #c9d8d1;
  border-radius: 8px;
  color: #31443d;
}

.priority-list {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 20px;
  color: #31443d;
}

textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 12px;
  border: 1px solid #c9d8d1;
  border-radius: 8px;
  font: inherit;
  resize: vertical;
}

.action-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: flex-end;
}

.action-bar button,
.action-bar__primary {
  display: inline-flex;
  align-items: center;
  min-height: 40px;
  padding: 0 16px;
  border: 1px solid #b9cbc3;
  border-radius: 8px;
  background: #ffffff;
  color: #165a46;
  font: inherit;
  font-weight: 700;
  text-decoration: none;
}

.action-bar__primary {
  border-color: #165a46;
  background: #165a46;
  color: #ffffff;
}
</style>
