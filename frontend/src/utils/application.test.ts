import { describe, expect, it } from 'vitest'
import { applicationStages, displayStatus } from './application'

describe('application presentation', () => {
  it('keeps the candidate timeline in hiring order', () => expect(applicationStages).toEqual(['applied', 'under_review', 'shortlisted', 'interview', 'offer', 'hired']))
  it('formats API status values for people', () => expect(displayStatus('under_review')).toBe('under review'))
})
