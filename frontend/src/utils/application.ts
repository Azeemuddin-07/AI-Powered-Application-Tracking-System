export const applicationStages = ['applied', 'under_review', 'shortlisted', 'interview', 'offer', 'hired'] as const
export function displayStatus(value: string) { return value.replaceAll('_', ' ') }
