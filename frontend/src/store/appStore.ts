/**
 * Zustand store for global application state.
 */
import { create } from 'zustand'

interface AppState {
    // Selected drug for comparison or simulation
    selectedDrugIds: number[]
    addSelectedDrug: (id: number) => void
    removeSelectedDrug: (id: number) => void
    clearSelectedDrugs: () => void

    // UI preferences
    sidebarCollapsed: boolean
    toggleSidebar: () => void
}

export const useAppStore = create<AppState>((set) => ({
    selectedDrugIds: [],
    addSelectedDrug: (id) => set((state) => ({
        selectedDrugIds: state.selectedDrugIds.includes(id)
            ? state.selectedDrugIds
            : [...state.selectedDrugIds, id]
    })),
    removeSelectedDrug: (id) => set((state) => ({
        selectedDrugIds: state.selectedDrugIds.filter((drugId) => drugId !== id)
    })),
    clearSelectedDrugs: () => set({ selectedDrugIds: [] }),

    sidebarCollapsed: false,
    toggleSidebar: () => set((state) => ({
        sidebarCollapsed: !state.sidebarCollapsed
    })),
}))
