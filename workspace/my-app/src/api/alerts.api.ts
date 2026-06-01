import { http } from './http'

export interface AlertRecord {
  alert_id: string
  sample_id: string
  alert_level: string
  reason: string
  status: string
  created_at: string
  acknowledged_at: string | null
}

export interface AcknowledgeAlertResponse {
  alert_id: string
  status: string
}

export async function getAlerts() {
  const response = await http.get<AlertRecord[]>('/alerts')
  return response.data
}

export async function acknowledgeAlert(alertId: string) {
  const response = await http.post<AcknowledgeAlertResponse>(`/alerts/${alertId}/acknowledge`)
  return response.data
}
