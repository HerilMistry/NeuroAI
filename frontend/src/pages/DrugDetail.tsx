import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'
import {
    ArrowLeft,
    AlertTriangle,
    Check,
    X,
    Target,
    GitBranch,
    Info,
    TrendingUp,
    TrendingDown,
    Minus
} from 'lucide-react'

export function DrugDetail() {
    const { id } = useParams<{ id: string }>()

    const { data: drug, isLoading, error } = useQuery({
        queryKey: ['drug', id],
        queryFn: () => api.getDrug(Number(id)),
        enabled: !!id,
    })

    if (isLoading) {
        return <div className="text-center py-12 text-muted-foreground">Loading drug details...</div>
    }

    if (error || !drug) {
        return <div className="text-center py-12 text-destructive">Failed to load drug</div>
    }

    return (
        <div className="space-y-6">
            {/* Back link */}
            <Link to="/drugs" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
                <ArrowLeft className="w-4 h-4" />
                Back to Drug Explorer
            </Link>

            {/* Header */}
            <div className="flex items-start justify-between">
                <div>
                    <h1 className="text-2xl font-bold">{drug.name}</h1>
                    <p className="text-muted-foreground font-mono">{drug.drugbank_id}</p>
                </div>
                <div className="flex items-center gap-2">
                    {drug.is_approved && (
                        <span className="px-3 py-1 bg-success/10 text-success text-sm font-medium rounded-full">
                            Approved
                        </span>
                    )}
                    {drug.cns_viable ? (
                        <span className="px-3 py-1 bg-primary/10 text-primary text-sm font-medium rounded-full">
                            CNS Viable
                        </span>
                    ) : (
                        <span className="px-3 py-1 bg-muted text-muted-foreground text-sm font-medium rounded-full">
                            Non-CNS
                        </span>
                    )}
                </div>
            </div>

            {/* Safety Warnings */}
            {drug.safety_summary.has_warnings && (
                <div className="warning-panel">
                    <div className="flex items-start gap-3">
                        <AlertTriangle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
                        <div>
                            <h3 className="font-semibold text-warning">Safety Considerations</h3>
                            <ul className="mt-2 space-y-1 text-sm">
                                {drug.safety_summary.warnings.map((w, i) => (
                                    <li key={i} className="text-muted-foreground">• {w.message}</li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            )}

            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* CNS MPO Score */}
                <div className="scientific-panel">
                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        CNS MPO Score
                        <Info className="w-4 h-4 text-muted-foreground" />
                    </h2>

                    <div className="flex items-center gap-4 mb-4">
                        <div className={`text-4xl font-bold ${(drug.cns_mpo_score ?? 0) >= 5 ? 'text-success' :
                                (drug.cns_mpo_score ?? 0) >= 4 ? 'text-warning' : 'text-destructive'
                            }`}>
                            {drug.cns_mpo_score?.toFixed(2) ?? 'N/A'}
                        </div>
                        <div className="text-sm text-muted-foreground">
                            / 6.00 max<br />
                            <span className="font-medium">Threshold: ≥4.00</span>
                        </div>
                    </div>

                    {/* Component breakdown */}
                    <div className="space-y-2">
                        {Object.entries(drug.cns_score_explanation).map(([key, val]) => (
                            <div key={key} className="flex items-center justify-between text-sm">
                                <span className="capitalize">{key.replace('_', ' ')}</span>
                                <div className="flex items-center gap-2">
                                    <span className="text-muted-foreground">{val.value ?? 'N/A'}</span>
                                    <div className="w-20 bg-muted rounded-full h-2">
                                        <div
                                            className="h-full bg-primary rounded-full"
                                            style={{ width: `${(val.score ?? 0) * 100}%` }}
                                        />
                                    </div>
                                    <span className="w-10 text-right font-mono">{val.score?.toFixed(2)}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Physicochemical Properties */}
                <div className="scientific-panel">
                    <h2 className="text-lg font-semibold mb-4">Physicochemical Properties</h2>
                    <div className="grid grid-cols-2 gap-4">
                        <PropertyItem label="Molecular Weight" value={drug.molecular_weight} unit="Da" />
                        <PropertyItem label="LogP" value={drug.logp} />
                        <PropertyItem label="HBD" value={drug.hbd} />
                        <PropertyItem label="HBA" value={drug.hba} />
                        <PropertyItem label="TPSA" value={drug.tpsa} unit="Å²" />
                        <PropertyItem label="pKa" value={drug.pka} />
                        <PropertyItem label="Rotatable Bonds" value={drug.rotatable_bonds} />
                        <PropertyItem label="PAINS Alerts" value={drug.pains_alerts} warn={drug.pains_alerts > 0} />
                    </div>
                </div>
            </div>

            {/* Target Interactions */}
            <div className="scientific-panel">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    Target Interactions ({drug.target_interactions.length})
                </h2>

                {drug.target_interactions.length === 0 ? (
                    <p className="text-muted-foreground">No target interactions recorded</p>
                ) : (
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Target</th>
                                <th>Activity</th>
                                <th>Affinity</th>
                                <th>Confidence</th>
                                <th>Toxicity</th>
                            </tr>
                        </thead>
                        <tbody>
                            {drug.target_interactions.map((ti) => (
                                <tr key={ti.id}>
                                    <td>
                                        <span className="font-medium">{ti.target_gene_symbol}</span>
                                        {ti.target_name && (
                                            <span className="text-muted-foreground ml-2 text-xs">
                                                {ti.target_name}
                                            </span>
                                        )}
                                    </td>
                                    <td className="capitalize">{ti.activity_type}</td>
                                    <td>
                                        {ti.affinity_nm ? (
                                            <span className="font-mono">{ti.affinity_nm} nM</span>
                                        ) : (
                                            <span className="text-muted-foreground">—</span>
                                        )}
                                    </td>
                                    <td>
                                        <div className="flex items-center gap-2">
                                            <div className="w-16 bg-muted rounded-full h-2">
                                                <div
                                                    className="h-full bg-primary rounded-full"
                                                    style={{ width: `${ti.confidence_score * 100}%` }}
                                                />
                                            </div>
                                            <span className="text-xs">{(ti.confidence_score * 100).toFixed(0)}%</span>
                                        </div>
                                    </td>
                                    <td>
                                        {ti.is_toxicity_associated ? (
                                            <span className="inline-flex items-center gap-1 text-warning">
                                                <AlertTriangle className="w-4 h-4" /> Flagged
                                            </span>
                                        ) : (
                                            <span className="text-muted-foreground">—</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Pathway Effects */}
            <div className="scientific-panel">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <GitBranch className="w-5 h-5" />
                    Pathway Perturbations ({drug.pathway_effects.length})
                </h2>

                {drug.pathway_effects.length === 0 ? (
                    <p className="text-muted-foreground">No pathway effects computed</p>
                ) : (
                    <div className="space-y-3">
                        {drug.pathway_effects.map((pe) => (
                            <div key={pe.id} className="border border-border rounded-lg p-4">
                                <div className="flex items-start justify-between mb-2">
                                    <div>
                                        <h3 className="font-medium">{pe.pathway_name}</h3>
                                        <p className="text-xs text-muted-foreground capitalize">{pe.pathway_category}</p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <DirectionIcon direction={pe.direction} />
                                        <ImpactBadge impact={pe.disease_impact} />
                                    </div>
                                </div>
                                <p className="text-sm text-muted-foreground">{pe.explanation}</p>
                                {pe.has_safety_concern && (
                                    <div className="mt-2 flex items-center gap-1 text-warning text-sm">
                                        <AlertTriangle className="w-4 h-4" />
                                        Contains toxicity-associated target(s)
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}

function PropertyItem({
    label,
    value,
    unit,
    warn
}: {
    label: string
    value: number | null | undefined
    unit?: string
    warn?: boolean
}) {
    return (
        <div>
            <p className="text-sm text-muted-foreground">{label}</p>
            <p className={`font-medium ${warn ? 'text-warning' : ''}`}>
                {value != null ? (
                    <>
                        {typeof value === 'number' && !Number.isInteger(value)
                            ? value.toFixed(2)
                            : value}
                        {unit && <span className="text-muted-foreground ml-1">{unit}</span>}
                    </>
                ) : (
                    <span className="text-muted-foreground">—</span>
                )}
            </p>
        </div>
    )
}

function DirectionIcon({ direction }: { direction: string }) {
    switch (direction) {
        case 'activation':
            return <TrendingUp className="w-4 h-4 text-success" />
        case 'inhibition':
            return <TrendingDown className="w-4 h-4 text-destructive" />
        default:
            return <Minus className="w-4 h-4 text-muted-foreground" />
    }
}

function ImpactBadge({ impact }: { impact: string }) {
    const styles: Record<string, string> = {
        beneficial: 'bg-success/10 text-success',
        detrimental: 'bg-destructive/10 text-destructive',
        uncertain: 'bg-warning/10 text-warning',
        neutral: 'bg-muted text-muted-foreground',
    }

    return (
        <span className={`px-2 py-1 rounded text-xs font-medium capitalize ${styles[impact] || styles.neutral}`}>
            {impact}
        </span>
    )
}
