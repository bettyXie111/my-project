import { http } from './http'

export interface HealthResponse {
  status: string
}

export async function getHealthStatus() {
  const response = await http.get<HealthResponse>('/health')
  return response.data
}
