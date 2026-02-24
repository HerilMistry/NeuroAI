import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api, SimulationResult } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import { Activity, Loader2, TrendingDown, TrendingUp } from "lucide-react";
import { motion } from "framer-motion";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

export default function Simulation() {
  const [drugId, setDrugId] = useState("");
  const [diseaseStateId, setDiseaseStateId] = useState("");
  const [timeSteps, setTimeSteps] = useState("10");

  const { data: diseaseStates } = useQuery({
    queryKey: ["diseaseStates"],
    queryFn: api.getDiseaseStates,
  });

  const simMutation = useMutation({
    mutationFn: () =>
      api.simulate({
        drug_id: Number(drugId),
        disease_state_id: Number(diseaseStateId),
        time_steps: Number(timeSteps),
      }),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!drugId || !diseaseStateId) return;
    simMutation.mutate();
  };

  const result = simMutation.data;

  // Build chart data from trajectories
  const chartData = result
    ? result.baseline.trajectory.map((bt, i) => {
        const it = result.intervention.trajectory[i];
        const params: Record<string, number> = {};
        Object.keys(bt.parameters).forEach((k) => {
          params[`baseline_${k}`] = bt.parameters[k];
          if (it) params[`intervention_${k}`] = it.parameters[k];
        });
        return { time_step: bt.time_step, ...params };
      })
    : [];

  const paramKeys = result ? Object.keys(result.baseline.trajectory[0]?.parameters ?? {}) : [];
  const COLORS = ["hsl(187, 72%, 53%)", "hsl(152, 60%, 45%)", "hsl(36, 90%, 55%)", "hsl(0, 72%, 51%)", "hsl(270, 60%, 55%)"];

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Disease Simulation</h1>
        <p className="text-sm text-muted-foreground">Compare disease progression with and without drug intervention</p>
      </div>

      <DisclaimerBanner />

      <div className="grid gap-5 lg:grid-cols-3">
        {/* Config */}
        <div className="glass-card p-5">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-muted-foreground">Drug ID *</label>
              <Input
                type="number"
                placeholder="e.g. 5"
                value={drugId}
                onChange={(e) => setDrugId(e.target.value)}
                className="bg-secondary border-border"
                required
              />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-muted-foreground">Disease State ID *</label>
              <Input
                type="number"
                placeholder="e.g. 1"
                value={diseaseStateId}
                onChange={(e) => setDiseaseStateId(e.target.value)}
                className="bg-secondary border-border"
                required
              />
              {diseaseStates?.results && (
                <div className="mt-2 space-y-1">
                  {diseaseStates.results.map((ds) => (
                    <button
                      type="button"
                      key={ds.id}
                      onClick={() => setDiseaseStateId(String(ds.id))}
                      className={`block w-full text-left rounded-md border px-3 py-2 text-xs transition-all ${
                        diseaseStateId === String(ds.id) ? "border-primary/40 bg-primary/10 text-primary" : "border-border text-muted-foreground hover:bg-secondary"
                      }`}
                    >
                      <span className="font-medium">{ds.name}</span>
                      <span className="block text-[10px] mt-0.5">{ds.disease_type}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-muted-foreground">Time Steps</label>
              <Input
                type="number"
                value={timeSteps}
                onChange={(e) => setTimeSteps(e.target.value)}
                className="bg-secondary border-border"
                min={1}
                max={50}
              />
            </div>
            <Button type="submit" disabled={simMutation.isPending} className="w-full bg-primary text-primary-foreground hover:bg-primary/90">
              {simMutation.isPending ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Simulating...</> : "Run Simulation"}
            </Button>
          </form>
        </div>

        {/* Results */}
        <div className="lg:col-span-2 space-y-5">
          {result ? (
            <>
              {/* Chart */}
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card p-5">
                <h3 className="text-sm font-semibold text-foreground mb-4">Disease Progression Trajectories</h3>
                <div className="h-[320px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(222, 30%, 18%)" />
                      <XAxis dataKey="time_step" stroke="hsl(215, 20%, 55%)" tick={{ fontSize: 11 }} />
                      <YAxis stroke="hsl(215, 20%, 55%)" tick={{ fontSize: 11 }} />
                      <Tooltip
                        contentStyle={{ backgroundColor: "hsl(222, 44%, 9%)", border: "1px solid hsl(222, 30%, 18%)", borderRadius: "8px", fontSize: 12 }}
                        labelStyle={{ color: "hsl(210, 40%, 92%)" }}
                      />
                      <Legend wrapperStyle={{ fontSize: 11 }} />
                      {paramKeys.map((key, i) => (
                        <Line key={`baseline_${key}`} type="monotone" dataKey={`baseline_${key}`} stroke={COLORS[i % COLORS.length]} strokeDasharray="5 5" strokeWidth={1.5} dot={false} name={`Baseline: ${key}`} />
                      ))}
                      {paramKeys.map((key, i) => (
                        <Line key={`intervention_${key}`} type="monotone" dataKey={`intervention_${key}`} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={false} name={`Intervention: ${key}`} />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </motion.div>

              {/* Comparison */}
              <div className="grid gap-4 sm:grid-cols-3">
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-4">
                  <p className="text-xs text-muted-foreground">Improvement</p>
                  <p className="text-lg font-bold text-success mt-1"><TrendingDown className="inline h-4 w-4 mr-1" />{result.comparison.improvement}</p>
                </motion.div>
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card p-4">
                  <p className="text-xs text-muted-foreground">Time Benefit</p>
                  <p className="text-lg font-bold text-primary mt-1">{result.comparison.time_benefit}</p>
                </motion.div>
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card p-4">
                  <p className="text-xs text-muted-foreground">Assessment</p>
                  <p className="text-sm text-foreground mt-1">{result.overall_assessment}</p>
                </motion.div>
              </div>

              {/* Key changes side by side */}
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="glass-card p-4">
                  <p className="text-xs font-semibold text-muted-foreground mb-2">{result.baseline.label}</p>
                  <ul className="space-y-1">
                    {result.baseline.key_changes.map((c, i) => (
                      <li key={i} className="text-xs text-foreground">• {c}</li>
                    ))}
                  </ul>
                </div>
                <div className="glass-card p-4">
                  <p className="text-xs font-semibold text-muted-foreground mb-2">{result.intervention.label}</p>
                  <ul className="space-y-1">
                    {result.intervention.key_changes.map((c, i) => (
                      <li key={i} className="text-xs text-success">• {c}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Caveats */}
              {result.caveats?.length > 0 && (
                <div className="glass-card border-warning/20 bg-warning/5 p-4">
                  <p className="text-xs font-semibold text-warning mb-2">Important Caveats</p>
                  <ul className="space-y-1">
                    {result.caveats.map((c, i) => (
                      <li key={i} className="text-xs text-muted-foreground">• {c}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          ) : simMutation.isError ? (
            <div className="glass-card border-destructive/30 bg-destructive/5 p-5">
              <p className="text-sm text-destructive">Simulation failed: {(simMutation.error as Error).message}</p>
            </div>
          ) : (
            <div className="glass-card flex flex-col items-center justify-center py-20 text-center">
              <Activity className="h-10 w-10 text-muted-foreground/30 mb-3" />
              <p className="text-sm text-muted-foreground">Configure and run a simulation</p>
              <p className="text-xs text-muted-foreground mt-1">Compare baseline disease progression vs. drug intervention</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
