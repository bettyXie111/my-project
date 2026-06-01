import { create } from 'zustand'

type MenuPath = '/' | '/samples' | '/alerts' | '/reports'

interface AppState {
  activeMenu: MenuPath
  visits: number
  selectedSampleId: string
  alertAcknowledgedCount: number
  syncRoute: (path: string) => void
  selectSample: (sampleId: string) => void
  acknowledgeAlert: () => void
}

const normalizePath = (path: string): MenuPath => {
  if (path.startsWith('/samples')) {
    return '/samples'
  }
  if (path.startsWith('/alerts')) {
    return '/alerts'
  }
  if (path.startsWith('/reports')) {
    return '/reports'
  }
  return '/'
}

export const useAppStore = create<AppState>((set) => ({
  activeMenu: '/',
  visits: 1,
  selectedSampleId: 'SMP-0001',
  alertAcknowledgedCount: 0,
  syncRoute: (path) =>
    set((state) => ({
      activeMenu: normalizePath(path),
      visits: path === state.activeMenu ? state.visits : state.visits + 1,
    })),
  selectSample: (sampleId) => set({ selectedSampleId: sampleId }),
  acknowledgeAlert: () =>
    set((state) => ({
      alertAcknowledgedCount: state.alertAcknowledgedCount + 1,
    })),
}))
