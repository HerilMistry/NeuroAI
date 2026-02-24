const API_BASE_URL = "http://localhost:8000/api/v1";

async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`API Error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// Types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Drug {
  id: number;
  drugbank_id: string;
  chembl_id: string;
  name: string;
  is_approved: boolean;
  molecular_weight: number;
  logp: number;
  cns_mpo_score: number;
  cns_viable: boolean;
  pains_alerts: number;
}

export interface DrugDetail extends Drug {
  synonyms: string[];
  approval_status: string;
  smiles: string;
  hbd: number;
  hba: number;
  tpsa: number;
  pka: number;
  rotatable_bonds: number;
  cns_score_explanation: Record<string, number>;
  structural_alerts: string[];
  description: string;
  categories: string[];
  target_interactions: TargetInteraction[];
  pathway_effects: DrugPathwayEffect[];
  safety_summary: {
    has_warnings: boolean;
    warning_count: number;
    warnings: string[];
  };
  created_at: string;
  updated_at: string;
}

export interface TargetInteraction {
  id: number;
  target: number;
  target_gene_symbol: string;
  target_name: string;
  affinity_nm: number;
  affinity_type: string;
  activity_type: string;
  confidence_score: number;
  evidence_level: string;
  source: string;
  is_off_target: boolean;
  is_toxicity_associated: boolean;
}

export interface Target {
  id: number;
  gene_symbol: string;
  gene_name: string;
  uniprot_id: string;
  protein_name: string;
  protein_class: string;
  disease_relevance_score: number;
  is_toxicity_associated: boolean;
  toxicity_categories: string[];
  brain_expression_level: string;
}

export interface TargetDetail extends Target {
  ensembl_id: string;
  entrez_id: string;
  subcellular_location: string[];
  disease_associations: { disease: string; score: number; source: string }[];
  toxicity_evidence: string | null;
  known_drug_count: number;
  is_promiscuous_target: boolean;
  description: string;
  created_at: string;
  updated_at: string;
  data_source: string;
}

export interface Pathway {
  id: number;
  pathway_id: string;
  name: string;
  description: string;
  category: string;
  disease_relevance: string;
  activation_effect: string;
  source: string;
  target_count: number;
}

export interface DrugPathwayEffect {
  id: number;
  drug: number;
  drug_name: string;
  pathway: number;
  pathway_name: string;
  pathway_category: string;
  perturbation_score: number;
  direction: string;
  disease_impact: string;
  confidence: number;
  contributing_targets: string[];
  explanation: string;
  has_safety_concern: boolean;
  computed_at: string;
}

export interface DiseaseState {
  id: number;
  name: string;
  description: string;
  disease_type: string;
  parameters: Record<string, number>;
  is_default: boolean;
}

export interface BindingAffinityResult {
  molecule_analysis: {
    smiles: string;
    molecular_weight: number;
    logp: number;
    hbd: number;
    hba: number;
    tpsa: number;
    num_rotatable_bonds: number;
    pains_alerts: number;
    drug_likeness: string;
  };
  binding_affinity: {
    target: string;
    binding_score: number;
    confidence: string;
    method: string;
    reasoning: string;
  };
  status: string;
  model_info: { method: string; paper: string; validation: string };
}

export interface ToxicityResult {
  toxicity: {
    molecule: string;
    toxicity_risk: string;
    mechanism: string;
    confidence: string;
    reasoning: string;
  };
  status: string;
  model: string;
}

export interface DrugResponseResult {
  drug_response_prediction: {
    molecule_analysis: Record<string, unknown>;
    binding_prediction: Record<string, unknown>;
    toxicity_assessment: Record<string, unknown>;
    overall_recommendation: string;
    risk_factors: string[];
    next_steps: string[];
  };
  status: string;
  models_used: string[];
}

export interface SimulationResult {
  baseline: {
    label: string;
    time_steps: number;
    trajectory: { time_step: number; parameters: Record<string, number>; uncertainty: number }[];
    final_state: Record<string, number>;
    key_changes: string[];
    explanation: string;
  };
  intervention: {
    label: string;
    time_steps: number;
    trajectory: { time_step: number; parameters: Record<string, number>; uncertainty: number }[];
    final_state: Record<string, number>;
    key_changes: string[];
    explanation: string;
  };
  comparison: {
    improvement: string;
    time_benefit: string;
    pathway_impact: string[];
  };
  overall_assessment: string;
  caveats: string[];
}

export interface SystemInfo {
  platform: string;
  version: string;
  description: string;
  ml_models: Record<string, string>;
  statistics: {
    drug_count: number;
    target_count: number;
    pathway_count: number;
    cns_viable_drugs: number;
  };
  data_sources: string[];
  disclaimers: string[];
}

// API Functions
export const api = {
  // Drugs
  getDrugs: (params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : "";
    return apiFetch<PaginatedResponse<Drug>>(`/drugs/${query}`);
  },
  getDrug: (id: number) => apiFetch<DrugDetail>(`/drugs/${id}/`),
  getCnsViableDrugs: () => apiFetch<PaginatedResponse<Drug>>("/drugs/cns_viable/"),

  // Targets
  getTargets: (params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : "";
    return apiFetch<PaginatedResponse<Target>>(`/targets/${query}`);
  },
  getTarget: (id: number) => apiFetch<TargetDetail>(`/targets/${id}/`),
  getTargetDrugs: (id: number) => apiFetch<TargetInteraction[]>(`/targets/${id}/drugs/`),

  // Pathways
  getPathways: (params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : "";
    return apiFetch<PaginatedResponse<Pathway>>(`/pathways/${query}`);
  },
  getPathway: (id: number) => apiFetch<Pathway>(`/pathways/${id}/`),
  getPathwayTargets: (id: number, params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : "";
    return apiFetch<PaginatedResponse<{ id: number; target: number; target_gene_symbol: string; role: string; influence_weight: number; evidence_level: string }>>(`/pathways/${id}/targets/${query}`);
  },
  getPathwayDrugEffects: (id: number) => apiFetch<DrugPathwayEffect[]>(`/pathways/${id}/drug_effects/`),

  // Pathway Effects
  getPathwayEffects: (params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : "";
    return apiFetch<PaginatedResponse<DrugPathwayEffect>>(`/pathway-effects/${query}`);
  },

  // Disease States
  getDiseaseStates: () => apiFetch<PaginatedResponse<DiseaseState>>("/disease-states/"),
  getDefaultDiseaseState: () => apiFetch<DiseaseState>("/disease-states/default/"),

  // Predictions
  predictBindingAffinity: (data: { molecule_smiles: string; target_name: string; target_sequence?: string }) =>
    apiFetch<BindingAffinityResult>("/predictions/binding-affinity/", { method: "POST", body: JSON.stringify(data) }),

  predictToxicity: (data: { molecule_smiles: string; molecule_name?: string }) =>
    apiFetch<ToxicityResult>("/predictions/toxicity/", { method: "POST", body: JSON.stringify(data) }),

  predictDrugResponse: (data: { molecule_smiles: string; target_name: string; target_sequence?: string; disease_context?: string }) =>
    apiFetch<DrugResponseResult>("/predictions/drug-response/", { method: "POST", body: JSON.stringify(data) }),

  analyzeMolecule: (data: { molecule_smiles: string }) =>
    apiFetch<{ analysis: Record<string, unknown>; status: string }>("/predictions/molecule-analysis/", { method: "POST", body: JSON.stringify(data) }),

  // Simulation
  simulate: (data: { drug_id: number; disease_state_id: number; time_steps?: number }) =>
    apiFetch<SimulationResult>("/simulate/", { method: "POST", body: JSON.stringify(data) }),

  // System
  getSystemInfo: () => apiFetch<SystemInfo>("/system/"),
};
