import { http } from './http'

export interface SampleRecord {
  sample_id: string
  sample_code: string
  owner: string
  category_count: number
  review_rounds: number
  quantity: number
  created_at: string
}

export async function getSamples() {
  const response = await http.get<SampleRecord[]>('/samples')
  return response.data
}
