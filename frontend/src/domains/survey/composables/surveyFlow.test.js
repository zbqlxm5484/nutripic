import { describe, expect, it } from 'vitest'
import {
  createInitialSurveyState,
  getNextStepId,
  getPreviousStepId,
  toggleSelectedCode,
  useSurveyFunnel,
  validateSurveyStep,
} from './surveyFlow'
import { surveySteps } from '../config/surveyDefinition'

describe('surveyFlow', () => {
  it('moves through configured steps in order', () => {
    expect(getNextStepId(surveySteps, 'health_goals')).toBe('medications')
    expect(getPreviousStepId(surveySteps, 'medications')).toBe('health_goals')
    expect(getNextStepId(surveySteps, 'additional_notes')).toBeNull()
  })

  it('requires at least one and at most five health goals', () => {
    const state = createInitialSurveyState()

    expect(validateSurveyStep(surveySteps[0], state).isValid).toBe(false)

    state.health_goals = ['fatigue', 'sleep', 'eye', 'gut', 'immune']
    expect(validateSurveyStep(surveySteps[0], state).isValid).toBe(true)

    state.health_goals = ['fatigue', 'sleep', 'eye', 'gut', 'immune', 'skin']
    expect(validateSurveyStep(surveySteps[0], state).isValid).toBe(false)
  })

  it('does not add more selected codes than the configured max', () => {
    const current = ['fatigue', 'sleep', 'eye', 'gut', 'immune']

    expect(toggleSelectedCode(current, 'skin', { max: 5 })).toEqual(current)
    expect(toggleSelectedCode(current, 'immune', { max: 5 })).toEqual(['fatigue', 'sleep', 'eye', 'gut'])
  })

  it('keeps users on an invalid required step until the step is valid', () => {
    const funnel = useSurveyFunnel(surveySteps)

    expect(funnel.next()).toBe(false)
    expect(funnel.currentStepId.value).toBe('health_goals')
    expect(funnel.canShowError('health_goals')).toBe(true)

    funnel.selectStepOption(surveySteps[0], 'fatigue')

    expect(funnel.next()).toBe(true)
    expect(funnel.currentStepId.value).toBe('medications')
  })
})
