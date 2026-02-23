import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { api, SimulationResponse } from '@/api/client'
import {
    Play,
    AlertTriangle,
    Info,
    TrendingUp,
    TrendingDown,
    Minus
} from 'lucide-react'
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts'

export function Simulation() {
    const [selectedDrugId, setSelectedDrugId] = useState<number | null>(null)
    const [timeSteps, setTimeSteps] = useState(10)

    const { data: drugsData } = useQuery({
        queryKey: ['drugs-for-simulation'],
        queryFn: () => api.getCNSViableDrugs(),
    })

    const simulationMutation = useMutation({
        mutationFn: api.runSimulation,
    })

    const handleRunSimulation = () => {
        simulationMutation.mutate({
            drug_id: selectedDrugId,
            time_steps: timeSteps,
        })
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold">Disease Progression Simulator</h1>
                <p className="text-muted-foreground mt-1">
                    Explore mechanistic effects of drugs on disease parameters
                </p>
            </div>

            {/* Critical Warning */}
            <div className="caution-panel">
                <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                    <div>
                        <h3 className="font-semibold text-destructive">Simulation Disclaimer</h3>
                        <ul className="mt-2 text-sm space-y-1 text-muted-foreground">
                            <li>• This is a <strong>mechanistic exploration tool</strong>, NOT a clinical prediction</li>
                            <li>• Results do NOT predict patient outcomes or drug efficacy</li>
                            <li>• Parameters are abstract representations, not clinical biomarkers</li>
                            <li>• Uncertainty increases significantly over time</li>
                        </ul>
                    </div>
                </div>
            </div>

            {/* Controls */}
            <div className="scientific-panel">
                <h2 className="text-lg font-semibold mb-4">Simulation Configuration</h2>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">Select Drug (Optional)</label>
                        <select
                            value={selectedDrugId ?? ''}
                            onChange={(e) => setSelectedDrugId(e.target.value ? Number(e.target.value) : null)}
                            className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                        >
                            <option value="">Baseline only (no intervention)</option>
                            {drugsData?.results.map((drug) => (
                                <option key={drug.id} value={drug.id}>
                                    {drug.name} (MPO: {drug.cns_mpo_score?.toFixed(1) ?? 'N/A'})
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Time Steps</label>
                        <input
                            type="number"
                            min={1}
                            max={50}
                            value={timeSteps}
                            onChange={(e) => setTimeSteps(Number(e.target.value))}
                            className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                        />
                    </div>

                    <div className="flex items-end">
                        <button
                            onClick={handleRunSimulation}
                            disabled={simulationMutation.isPending}
                            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
                        >
                            <Play className="w-4 h-4" />
                            {simulationMutation.isPending ? 'Running...' : 'Run Simulation'}
                        </button>
                    </div>
                </div>
            </div>

            {/* Results */}
            {simulationMutation.data && (
                <SimulationResults result={simulationMutation.data} />
            )}

            {/* Error */}
            {simulationMutation.isError && (
                <div className="text-center py-12 text-destructive">
                    Simulation failed. Please try again.
                </div>
            )}
        </div>
    )
}

function SimulationResults({ result }: { result: SimulationResponse }) {
    // Prepare chart data
    const chartData = result.baseline.trajectory.map((pt, i) => {
        const data: Record<string, number> = {
            time: pt.time_step,
            ...Object.fromEntries(
                Object.entries(pt.parameters).map(([k, v]) => [`baseline_${k}`, v])
            ),
        }

        if (result.intervention && result.intervention.trajectory[i]) {
            Object.entries(result.intervention.trajectory[i].parameters).forEach(([k, v]) => {
                data[`intervention_${k}`] = v
            })
        }

        return data
    })

    const parameters = Object.keys(result.baseline.trajectory[0]?.parameters || {})

    return (
        <div className="space-y-6">
            {/* Assessment */}
            <div className="scientific-panel">
                <h2 className="text-lg font-semibold mb-3">Simulation Assessment</h2>
                <p className="text-muted-foreground">{result.overall_assessment}</p>

                {result.intervention && (
                    <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                        {Object.entries(result.comparison).map(([param, diff]) => (
                            <ComparisonItem key={param} param={param} diff={diff} />
                        ))}
                    </div>
                )}
            </div>

            {/* Chart */}
            <div className="scientific-panel">
                <h2 className="text-lg font-semibold mb-4">Trajectory Visualization</h2>
                <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis
                                dataKey="time"
                                label={{ value: 'Time Step', position: 'bottom' }}
                            />
                            <YAxis
                                domain={[0, 1]}
                                label={{ value: 'Parameter Value', angle: -90, position: 'insideLeft' }}
                            />
                            <Tooltip />
                            <Legend />
                            {parameters.slice(0, 3).map((param, i) => (
                                <Line
                                    key={`baseline_${param}`}
                                    type="monotone"
                                    dataKey={`baseline_${param}`}
                                    name={`Baseline: ${param.replace('_', ' ')}`}
                                    stroke={['#64748b', '#94a3b8', '#cbd5e1'][i]}
                                    strokeDasharray="5 5"
                                    dot={false}
                                />
                            ))}
                            {result.intervention && parameters.slice(0, 3).map((param, i) => (
                                <Line
                                    key={`intervention_${param}`}
                                    type="monotone"
                                    dataKey={`intervention_${param}`}
                                    name={`${result.intervention!.label}: ${param.replace('_', ' ')}`}
                                    stroke={['#3b82f6', '#22c55e', '#f59e0b'][i]}
                                    dot={false}
                                />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </div>
                <p className="text-xs text-muted-foreground mt-2 text-center">
                    Showing first 3 parameters. Dashed lines = baseline, solid lines = intervention.
                </p>
            </div>

            {/* Caveats */}
            <div className="scientific-panel bg-muted/50">
                <div className="flex items-start gap-3">
                    <Info className="w-5 h-5 text-muted-foreground flex-shrink-0 mt-0.5" />
                    <div>
                        <h3 className="font-semibold text-muted-foreground">Important Caveats</h3>
                        <ul className="mt-2 text-sm space-y-1 text-muted-foreground">
                            {result.caveats.map((caveat, i) => (
                                <li key={i}>• {caveat}</li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    )
}

function ComparisonItem({ param, diff }: { param: string; diff: number }) {
    const isPositive = diff > 0.01

    // Determine if change is "good" - depends on parameter semantics
    // For now, assume lower pathology / higher function is better
    const getIcon = () => {
        if (Math.abs(diff) < 0.01) return <Minus className="w-4 h-4 text-muted-foreground" />
        if (isPositive) return <TrendingUp className="w-4 h-4" />
        return <TrendingDown className="w-4 h-4" />
    }

    return (
        <div className="text-center">
            <p className="text-xs text-muted-foreground capitalize mb-1">
                {param.replace('_', ' ')}
            </p>
            <div className={`flex items-center justify-center gap-1 font-mono text-sm ${Math.abs(diff) < 0.01 ? 'text-muted-foreground' :
                    isPositive ? 'text-blue-600' : 'text-orange-600'
                }`}>
                {getIcon()}
                {diff > 0 ? '+' : ''}{diff.toFixed(3)}
            </div>
        </div>
    )
}
