import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api, Drug } from '@/api/client'
import { Search, Filter, ChevronRight, Brain, AlertTriangle, Check, X } from 'lucide-react'

export function DrugExplorer() {
    const [search, setSearch] = useState('')
    const [cnsFilter, setCnsFilter] = useState<boolean | undefined>(undefined)
    const [page, setPage] = useState(1)

    const { data, isLoading, error } = useQuery({
        queryKey: ['drugs', search, cnsFilter, page],
        queryFn: () => api.getDrugs({ search, cns_viable: cnsFilter, page }),
    })

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold">Drug Explorer</h1>
                <p className="text-muted-foreground mt-1">
                    Browse and filter drugs by CNS viability and safety indicators
                </p>
            </div>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Search by name or DrugBank ID..."
                        value={search}
                        onChange={(e) => {
                            setSearch(e.target.value)
                            setPage(1)
                        }}
                        className="w-full pl-10 pr-4 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={() => setCnsFilter(undefined)}
                        className={`px-3 py-2 text-sm rounded-md border transition-colors ${cnsFilter === undefined
                                ? 'bg-primary text-primary-foreground border-primary'
                                : 'border-input hover:bg-muted'
                            }`}
                    >
                        All
                    </button>
                    <button
                        onClick={() => setCnsFilter(true)}
                        className={`px-3 py-2 text-sm rounded-md border transition-colors flex items-center gap-2 ${cnsFilter === true
                                ? 'bg-primary text-primary-foreground border-primary'
                                : 'border-input hover:bg-muted'
                            }`}
                    >
                        <Brain className="w-4 h-4" />
                        CNS Viable
                    </button>
                    <button
                        onClick={() => setCnsFilter(false)}
                        className={`px-3 py-2 text-sm rounded-md border transition-colors ${cnsFilter === false
                                ? 'bg-primary text-primary-foreground border-primary'
                                : 'border-input hover:bg-muted'
                            }`}
                    >
                        Non-CNS
                    </button>
                </div>
            </div>

            {/* Results */}
            {isLoading ? (
                <div className="text-center py-12 text-muted-foreground">Loading drugs...</div>
            ) : error ? (
                <div className="text-center py-12 text-destructive">Failed to load drugs</div>
            ) : data?.results.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">No drugs found</div>
            ) : (
                <>
                    <div className="scientific-panel overflow-x-auto">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>DrugBank ID</th>
                                    <th>MW (Da)</th>
                                    <th>LogP</th>
                                    <th>CNS MPO</th>
                                    <th>CNS Viable</th>
                                    <th>Alerts</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                                {data?.results.map((drug) => (
                                    <DrugRow key={drug.id} drug={drug} />
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination */}
                    <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">
                            Showing {data?.results.length} of {data?.count} drugs
                        </p>
                        <div className="flex gap-2">
                            <button
                                onClick={() => setPage((p) => Math.max(1, p - 1))}
                                disabled={!data?.previous}
                                className="px-3 py-1 text-sm border rounded-md disabled:opacity-50"
                            >
                                Previous
                            </button>
                            <button
                                onClick={() => setPage((p) => p + 1)}
                                disabled={!data?.next}
                                className="px-3 py-1 text-sm border rounded-md disabled:opacity-50"
                            >
                                Next
                            </button>
                        </div>
                    </div>
                </>
            )}

            {/* Legend */}
            <div className="scientific-panel">
                <h3 className="font-medium mb-2">Understanding the Indicators</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                        <span className="font-medium">CNS MPO Score (0-6):</span>
                        <span className="text-muted-foreground ml-2">
                            Multiparameter optimization score for CNS drug-likeness. ≥4.0 is considered viable.
                        </span>
                    </div>
                    <div>
                        <span className="font-medium">PAINS Alerts:</span>
                        <span className="text-muted-foreground ml-2">
                            Structural patterns associated with assay interference.
                        </span>
                    </div>
                </div>
            </div>
        </div>
    )
}

function DrugRow({ drug }: { drug: Drug }) {
    const mpoClass = drug.cns_mpo_score
        ? drug.cns_mpo_score >= 5 ? 'score-high'
            : drug.cns_mpo_score >= 4 ? 'score-medium'
                : 'score-low'
        : 'text-muted-foreground'

    return (
        <tr className="hover:bg-muted/50">
            <td className="font-medium">{drug.name}</td>
            <td className="font-mono text-xs">{drug.drugbank_id}</td>
            <td>{drug.molecular_weight?.toFixed(1) ?? '—'}</td>
            <td>{drug.logp?.toFixed(2) ?? '—'}</td>
            <td className={mpoClass}>
                {drug.cns_mpo_score?.toFixed(2) ?? '—'}
            </td>
            <td>
                {drug.cns_viable ? (
                    <span className="inline-flex items-center gap-1 text-success">
                        <Check className="w-4 h-4" /> Yes
                    </span>
                ) : (
                    <span className="inline-flex items-center gap-1 text-muted-foreground">
                        <X className="w-4 h-4" /> No
                    </span>
                )}
            </td>
            <td>
                {drug.pains_alerts > 0 ? (
                    <span className="inline-flex items-center gap-1 text-warning">
                        <AlertTriangle className="w-4 h-4" />
                        {drug.pains_alerts}
                    </span>
                ) : (
                    <span className="text-muted-foreground">0</span>
                )}
            </td>
            <td>
                <Link
                    to={`/drugs/${drug.id}`}
                    className="inline-flex items-center gap-1 text-primary hover:underline"
                >
                    Details <ChevronRight className="w-4 h-4" />
                </Link>
            </td>
        </tr>
    )
}
