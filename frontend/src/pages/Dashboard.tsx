import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'
import { AlertTriangle, Pill, GitBranch, Activity, Brain } from 'lucide-react'

export function Dashboard() {
    const { data: systemInfo, isLoading } = useQuery({
        queryKey: ['system-info'],
        queryFn: api.getSystemInfo,
    })

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold">Disease Overview</h1>
                <p className="text-muted-foreground mt-1">
                    Mechanism-aware decision support for neurodegenerative drug discovery
                </p>
            </div>

            {/* Critical Disclaimer */}
            <div className="caution-panel">
                <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                    <div>
                        <h3 className="font-semibold text-destructive">Important Limitations</h3>
                        <ul className="mt-2 text-sm space-y-1 text-muted-foreground">
                            <li>• This platform does NOT provide clinical predictions or efficacy estimates</li>
                            <li>• All simulations are for mechanistic exploration only</li>
                            <li>• Results should be reviewed by domain experts</li>
                            <li>• No diagnostic or treatment recommendations are made</li>
                        </ul>
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    icon={Pill}
                    label="Total Drugs"
                    value={systemInfo?.statistics.drug_count ?? '—'}
                    loading={isLoading}
                />
                <StatCard
                    icon={Brain}
                    label="CNS-Viable Drugs"
                    value={systemInfo?.statistics.cns_viable_drugs ?? '—'}
                    loading={isLoading}
                    highlight
                />
                <StatCard
                    icon={Activity}
                    label="Targets"
                    value={systemInfo?.statistics.target_count ?? '—'}
                    loading={isLoading}
                />
                <StatCard
                    icon={GitBranch}
                    label="Pathways"
                    value={systemInfo?.statistics.pathway_count ?? '—'}
                    loading={isLoading}
                />
            </div>

            {/* Biology Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="scientific-panel">
                    <h2 className="text-lg font-semibold mb-4">Modeled Disease Mechanisms</h2>
                    <div className="space-y-3 text-sm">
                        <MechanismItem
                            name="Neuroinflammation"
                            description="Chronic activation of microglia and astrocytes, release of pro-inflammatory cytokines"
                        />
                        <MechanismItem
                            name="Mitochondrial Dysfunction"
                            description="Impaired energy metabolism, oxidative stress, calcium dysregulation"
                        />
                        <MechanismItem
                            name="Protein Aggregation"
                            description="Accumulation of misfolded proteins (Aβ, tau, α-synuclein)"
                        />
                        <MechanismItem
                            name="Synaptic Dysfunction"
                            description="Loss of synaptic plasticity, neurotransmitter imbalances"
                        />
                        <MechanismItem
                            name="Autophagy Impairment"
                            description="Reduced clearance of damaged organelles and protein aggregates"
                        />
                    </div>
                </div>

                <div className="scientific-panel">
                    <h2 className="text-lg font-semibold mb-4">Platform Approach</h2>
                    <div className="space-y-4 text-sm">
                        <ApproachItem
                            title="Biological Plausibility > Prediction"
                            description="We model known mechanisms rather than attempting to predict clinical outcomes."
                        />
                        <ApproachItem
                            title="Explicit Uncertainty"
                            description="All scores include confidence intervals and data quality indicators."
                        />
                        <ApproachItem
                            title="Safety First"
                            description="Toxicity-associated targets and structural alerts are prominently flagged."
                        />
                        <ApproachItem
                            title="Transparent Logic"
                            description="All calculations use rule-based scoring with visible parameters."
                        />
                    </div>
                </div>
            </div>

            {/* Data Sources */}
            {systemInfo?.data_sources && systemInfo.data_sources.length > 0 && (
                <div className="scientific-panel">
                    <h2 className="text-lg font-semibold mb-3">Data Sources</h2>
                    <div className="flex flex-wrap gap-2">
                        {systemInfo.data_sources.map((source) => (
                            <span
                                key={source}
                                className="px-3 py-1 bg-muted rounded-full text-xs font-medium"
                            >
                                {source}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}

function StatCard({
    icon: Icon,
    label,
    value,
    loading,
    highlight,
}: {
    icon: React.ElementType
    label: string
    value: string | number
    loading: boolean
    highlight?: boolean
}) {
    return (
        <div className={`scientific-panel ${highlight ? 'ring-1 ring-primary/30' : ''}`}>
            <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${highlight ? 'bg-primary/10' : 'bg-muted'}`}>
                    <Icon className={`w-5 h-5 ${highlight ? 'text-primary' : 'text-muted-foreground'}`} />
                </div>
                <div>
                    <p className="text-sm text-muted-foreground">{label}</p>
                    <p className={`text-2xl font-bold ${loading ? 'animate-pulse' : ''}`}>
                        {loading ? '...' : value}
                    </p>
                </div>
            </div>
        </div>
    )
}

function MechanismItem({ name, description }: { name: string; description: string }) {
    return (
        <div className="border-l-2 border-primary/30 pl-3">
            <p className="font-medium">{name}</p>
            <p className="text-muted-foreground">{description}</p>
        </div>
    )
}

function ApproachItem({ title, description }: { title: string; description: string }) {
    return (
        <div>
            <p className="font-medium text-primary">{title}</p>
            <p className="text-muted-foreground">{description}</p>
        </div>
    )
}
