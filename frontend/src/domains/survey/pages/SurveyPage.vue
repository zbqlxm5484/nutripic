<template>
  <SurveyLayout>
    <section v-if="isLoading" class="progress-panel" aria-labelledby="survey-progress-title">
      <LoadingState label="설문 선택지를 불러오는 중입니다" />
    </section>

    <ErrorState
      v-else-if="loadError"
      title="설문을 불러오지 못했습니다"
      :description="loadError"
    >
      <template #action>
        <BaseButton size="sm" @click="loadSurveyOptions">다시 시도</BaseButton>
      </template>
    </ErrorState>

    <template v-else>
      <section class="progress-panel" aria-labelledby="survey-progress-title">
        <div>
          <p class="progress-panel__step">{{ progressValue }} / {{ surveySteps.length }}</p>
          <h2 id="survey-progress-title">{{ currentStep.title }}</h2>
        </div>
        <progress :max="surveySteps.length" :value="progressValue">
          {{ progressValue }} / {{ surveySteps.length }}
        </progress>
      </section>

      <ContentSection
        :title-id="`${currentStep.id}-title`"
        :title="currentStep.title"
        :description="currentStep.description"
      >
        <template v-if="currentStep.inputType === 'multi_select'">
          <EmptyState
            v-if="currentOptions.length === 0"
            title="선택지가 없습니다"
            description="현재 단계에서 표시할 선택지가 없습니다."
          />
          <div v-else class="chip-grid">
            <label
              v-for="option in currentOptions"
              :key="option.code"
              :class="{ 'chip-grid__item--checked': state[currentStep.field].includes(option.code) }"
            >
              <input
                type="checkbox"
                :name="currentStep.field"
                :value="option.code"
                :checked="state[currentStep.field].includes(option.code)"
                @change="selectStepOption(currentStep, option.code)"
              />
              <span>{{ option.name }}</span>
            </label>
          </div>

          <p class="step-help">
            선택 {{ state[currentStep.field].length }}개
            <span v-if="currentStep.max">/ 최대 {{ currentStep.max }}개</span>
          </p>

          <FormErrorMessage
            v-if="canShowError(currentStep.id) && !currentValidation.isValid"
            :message="currentValidation.message"
          />
        </template>

        <template v-else-if="currentStep.inputType === 'textarea'">
          <textarea
            v-model="state.additional_notes"
            class="form-control"
            name="additional_notes"
            rows="5"
            placeholder="과도한 개인정보는 입력하지 마세요."
          />
        </template>
      </ContentSection>

      <ContentSection
        v-if="state.health_goals.length > 0"
        title-id="priority-title"
        title="목표 우선순위"
        description="선택한 순서대로 우선순위가 자동 지정됩니다."
      >
        <ol class="priority-list">
          <li v-for="goalCode in state.health_goals" :key="goalCode">
            {{ getOptionName('health_goals', goalCode) }}
          </li>
        </ol>
      </ContentSection>

      <SafetyNotice />

      <div class="action-bar" aria-label="설문 이동">
        <BaseButton :disabled="isFirstStep" @click="previous">이전</BaseButton>
        <BaseButton v-if="!isLastStep" variant="primary" @click="next">다음</BaseButton>
        <BaseButton v-else variant="primary" @click="handleCreateReportRequest">
          리포트 생성 요청
        </BaseButton>
      </div>
    </template>
  </SurveyLayout>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  BaseButton,
  ContentSection,
  EmptyState,
  ErrorState,
  FormErrorMessage,
  LoadingState,
  SafetyNotice,
  SurveyLayout,
} from '../../../shared/components'
import { surveySteps } from '../config/surveyDefinition'
import { useSurveyFunnel } from '../composables/surveyFlow'
import { useSurveyOptions } from '../composables/useSurveyOptions'
import { buildReportPayload } from '../mappers/surveyReportPayload'

const router = useRouter()
const {
  state,
  currentStep,
  progressValue,
  isFirstStep,
  isLastStep,
  currentValidation,
  surveyValidation,
  selectStepOption,
  next,
  previous,
  showValidationFor,
  canShowError,
} = useSurveyFunnel(surveySteps)
const {
  optionGroups,
  isLoading,
  loadError,
  loadSurveyOptions,
  getOptionName,
} = useSurveyOptions(surveySteps)

const currentOptions = computed(() => {
  return optionGroups[currentStep.value.optionGroup] ?? []
})

onMounted(() => {
  loadSurveyOptions()
})

function handleCreateReportRequest() {
  if (!surveyValidation.value.isValid) {
    showValidationFor(surveyValidation.value.stepId)
    return
  }

  window.sessionStorage.setItem(
    'neutripic:survey_payload',
    JSON.stringify(buildReportPayload(state, optionGroups)),
  )
  router.push('/reports/generating')
}
</script>

<style scoped>
.progress-panel,
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

.progress-panel h2 {
  margin: 0;
  font-size: 1.25rem;
}

.progress-panel progress {
  width: 100%;
  height: 10px;
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

.chip-grid__item--checked {
  border-color: #4e8f70;
  background: #edf7f2;
  font-weight: 700;
}

.step-help {
  margin: 12px 0 0;
  color: #4e6f61;
  font-size: 0.875rem;
}

.priority-list {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 20px;
  color: #31443d;
}

textarea.form-control {
  width: 100%;
  box-sizing: border-box;
}

.action-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: flex-end;
}

</style>
