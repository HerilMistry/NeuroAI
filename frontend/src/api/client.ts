/**
 * API client for NeuroDegenRx backend.
 */
const API_BASE = '/api/v1'

interface PaginatedResponse<T> {
    count: number
    next: string | null
    previous: string | null
    results: T[]
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${url}`, {
        headers: {
            'Content-Type': 'application/json',
            ...options?.headers,
        },
        ...options,
    })

    if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }

    return response.json()
}

// Types
export interface Drug {
    id: number
    drugbank_id: string
    chembl_id: string | null
    name: string
    is_approved: boolean
    molecular_weight: number | null
    logp: number | null
    cns_mpo_score: number | null
    cns_viable: boolean
    pains_alerts: number
}

export interface DrugDetail extends Drug {
    synonyms: string[]
    smiles: string | null
    hbd: number | null
    hba: number | null
    tpsa: number | null
    pka: number | null
    rotatable_bonds: number | null
    cns_score_explanation: Record<string, { value: number | null; score: number }>
    structural_alerts: string[]
    description: string | null
    categories: string[]
    target_interactions: TargetInteraction[]
    pathway_effects: PathwayEffect[]
    safety_summary: SafetySummary
}

export interface TargetInteraction {
    id: number
    target: number
    target_gene_symbol: string
    target_name: string | null
    affinity_nm: number | null
    affinity_type: string
    activity_type: string
    confidence_score: number
    evidence_level: string
    source: string
    is_off_target: boolean
    is_toxicity_associated: boolean
}

export interface Target {
    id: number
    gene_symbol: string
    gene_name: string | null
    uniprot_id: string | null
    protein_name: string | null
    protein_class: string | null
    disease_relevance_score: number | null
    is_toxicity_associated: boolean
    toxicity_categories: string[]
    brain_expression_level: string
}

export interface Pathway {
    id: number
    pathway_id: string
    name: string
    description: string | null
    category: string
    disease_relevance: string
    activation_effect: string
    source: string
    target_count: number
}

export interface PathwayEffect {
    id: number
    drug: number
    drug_name: string
    pathway: number
    pathway_name: string
    pathway_category: string
    perturbation_score: number
    direction: string
    disease_impact: string
    confidence: number
    contributing_targets: ContributingTarget[]
    explanation: string
    has_safety_concern: boolean
    computed_at: string
}

export interface ContributingTarget {
    target_id: number
    gene_symbol: string
    contribution_score: number
    has_toxicity_flag: boolean
}

export interface SafetySummary {
    has_warnings: boolean
    warning_count: number
    warnings: Array<{
        level: string
        message: string
    }>
}

export interface DiseaseState {
    id: number
    name: string
    description: string | null
    disease_type: string
    parameters: Record<string, number>
    baseline_trajectory: Record<string, unknown>
    is_default: boolean
}

export interface SimulationRequest {
    drug_id?: number | null
    disease_state_id?: number | null
    initial_parameters?: Record<string, number>
    time_steps?: number
}

export interface SimulationResponse {
    baseline: TrajectoryResult
    intervention: TrajectoryResult | null
    comparison: Record<string, number>
    overall_assessment: string
    caveats: string[]
}

export interface TrajectoryResult {
    label: string
    time_steps: number
    trajectory: Array<{
        time_step: number
        parameters: Record<string, number>
        uncertainty: Record<string, number>
    }>
    final_state: Record<string, number>
    key_changes: Record<string, number>
    explanation: string
}

export interface SystemInfo {
    platform: string
    version: string
    description: string
    statistics: {
        drug_count: number
        target_count: number
        pathway_count: number
        cns_viable_drugs: number
    }
    data_sources: string[]
    disclaimers: string[]
}

// API Functions
export const api = {
    // System
    getSystemInfo: () => fetchJson<SystemInfo>('/system/'),

    // Drugs
    getDrugs: (params?: { search?: string; cns_viable?: boolean; page?: number }) => {
        const searchParams = new URLSearchParams()
        if (params?.search) searchParams.set('search', params.search)
        if (params?.cns_viable !== undefined) searchParams.set('cns_viable', String(params.cns_viable))
        if (params?.page) searchParams.set('page', String(params.page))
        const query = searchParams.toString()
        return fetchJson<PaginatedResponse<Drug>>(`/drugs/${query ? '?' + query : ''}`)
    },

    getDrug: (id: number) => fetchJson<DrugDetail>(`/drugs/${id}/`),

    getDrugTargets: (id: number) => fetchJson<TargetInteraction[]>(`/drugs/${id}/targets/`),

    getDrugPathwayEffects: (id: number) => fetchJson<PathwayEffect[]>(`/drugs/${id}/pathway_effects/`),

    getCNSViableDrugs: () => fetchJson<PaginatedResponse<Drug>>('/drugs/cns_viable/'),

    // Targets
    getTargets: (params?: { search?: string; page?: number }) => {
        const searchParams = new URLSearchParams()
        if (params?.search) searchParams.set('search', params.search)
        if (params?.page) searchParams.set('page', String(params.page))
        const query = searchParams.toString()
        return fetchJson<PaginatedResponse<Target>>(`/targets/${query ? '?' + query : ''}`)
    },

    getTarget: (id: number) => fetchJson<Target>(`/targets/${id}/`),

    // Pathways
    getPathways: (params?: { category?: string; page?: number }) => {
        const searchParams = new URLSearchParams()
        if (params?.category) searchParams.set('category', params.category)
        if (params?.page) searchParams.set('page', String(params.page))
        const query = searchParams.toString()
        return fetchJson<PaginatedResponse<Pathway>>(`/pathways/${query ? '?' + query : ''}`)
    },

    getPathway: (id: number) => fetchJson<Pathway>(`/pathways/${id}/`),

    // Disease States
    getDiseaseStates: () => fetchJson<PaginatedResponse<DiseaseState>>('/disease-states/'),

    getDefaultDiseaseState: () => fetchJson<DiseaseState>('/disease-states/default/'),

    // Simulation
    runSimulation: (request: SimulationRequest) =>
        fetchJson<SimulationResponse>('/simulate/', {
            method: 'POST',
            body: JSON.stringify(request),
        }),
}
