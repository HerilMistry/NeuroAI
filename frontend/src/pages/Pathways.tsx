import { useQuery } from '@tanstack/react-query'
import { api, Pathway } from '@/api/client'
import { GitBranch, TrendingUp, TrendingDown, HelpCircle } from 'lucide-react'

const categoryColors: Record<string, string> = {
    neuroinflammation: 'bg-orange-500/10 text-orange-600 border-orange-500/20',
    mitochondrial: 'bg-green-500/10 text-green-600 border-green-500/20',
    protein_aggregation: 'bg-purple-500/10 text-purple-600 border-purple-500/20',
    synaptic: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
    autophagy: 'bg-cyan-500/10 text-cyan-600 border-cyan-500/20',
    oxidative_stress: 'bg-red-500/10 text-red-600 border-red-500/20',
    apoptosis: 'bg-pink-500/10 text-pink-600 border-pink-500/20',
    neurotransmission: 'bg-indigo-500/10 text-indigo-600 border-indigo-500/20',
    metabolism: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20',
    other: 'bg-gray-500/10 text-gray-600 border-gray-500/20',
}

export function Pathways() {
    const { data, isLoading, error } = useQuery({
        queryKey: ['pathways'],
        queryFn: () => api.getPathways(),
    })

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold">Disease Pathways</h1>
                <p className="text-muted-foreground mt-1">
                    Curated biological pathways relevant to neurodegeneration
                </p>
            </div>

            {/* Explanation */}
            <div className="scientific-panel">
                <h2 className="text-lg font-semibold mb-3">How Pathways Are Used</h2>
                <div className="text-sm text-muted-foreground space-y-2">
                    <p>
                        Pathways represent biological processes affected in neurodegenerative diseases.
                        Drug effects are computed by aggregating target interactions within each pathway.
                    </p>
                    <p>
                        <strong>Activation Effect:</strong> Indicates whether pathway activation is
                        generally beneficial or detrimental for disease progression. This helps
                        interpret drug perturbation directions.
                    </p>
                </div>
            </div>

            {/* Pathways Grid */}
            {isLoading ? (
                <div className="text-center py-12 text-muted-foreground">Loading pathways...</div>
            ) : error ? (
                <div className="text-center py-12 text-destructive">Failed to load pathways</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {data?.results.map((pathway) => (
                        <PathwayCard key={pathway.id} pathway={pathway} />
                    ))}
                </div>
            )}

            {/* Legend */}
            <div className="scientific-panel">
                <h3 className="font-medium mb-3">Pathway Categories</h3>
                <div className="flex flex-wrap gap-2">
                    {Object.entries(categoryColors).map(([category, classes]) => (
                        <span
                            key={category}
                            className={`px-3 py-1 rounded-full text-xs font-medium border ${classes}`}
                        >
                            {category.replace('_', ' ')}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    )
}

function PathwayCard({ pathway }: { pathway: Pathway }) {
    const colorClass = categoryColors[pathway.category] || categoryColors.other

    return (
        <div className="scientific-panel hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
                <div className={`p-2 rounded-lg border ${colorClass}`}>
                    <GitBranch className="w-5 h-5" />
                </div>
                <RelevanceBadge relevance={pathway.disease_relevance} />
            </div>

            <h3 className="font-semibold mb-1">{pathway.name}</h3>
            <p className="text-xs text-muted-foreground capitalize mb-3">
                {pathway.category.replace('_', ' ')}
            </p>

            {pathway.description && (
                <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                    {pathway.description}
                </p>
            )}

            <div className="flex items-center justify-between text-sm pt-3 border-t border-border">
                <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">Activation:</span>
                    <ActivationEffect effect={pathway.activation_effect} />
                </div>
                <div className="text-muted-foreground">
                    {pathway.target_count} targets
                </div>
            </div>
        </div>
    )
}

function RelevanceBadge({ relevance }: { relevance: string }) {
    const styles: Record<string, string> = {
        high: 'bg-primary/10 text-primary',
        medium: 'bg-muted text-muted-foreground',
        low: 'bg-muted text-muted-foreground/70',
    }

    return (
        <span className={`px-2 py-1 rounded text-xs font-medium ${styles[relevance] || styles.medium}`}>
            {relevance} relevance
        </span>
    )
}

function ActivationEffect({ effect }: { effect: string }) {
    switch (effect) {
        case 'beneficial':
            return (
                <span className="inline-flex items-center gap-1 text-success">
                    <TrendingUp className="w-3 h-3" /> Beneficial
                </span>
            )
        case 'detrimental':
            return (
                <span className="inline-flex items-center gap-1 text-destructive">
                    <TrendingDown className="w-3 h-3" /> Detrimental
                </span>
            )
        case 'complex':
            return (
                <span className="inline-flex items-center gap-1 text-warning">
                    <HelpCircle className="w-3 h-3" /> Complex
                </span>
            )
        default:
            return (
                <span className="text-muted-foreground">Unknown</span>
            )
    }
}
