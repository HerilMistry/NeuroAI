import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import { FlaskConical, Loader2, Zap, Shield, Microscope } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

type PredictionTab = "binding" | "toxicity" | "response" | "analyze";

const TABS: { id: PredictionTab; label: string; icon: React.ElementType }[] = [
  { id: "binding", label: "Binding Affinity", icon: Zap },
  { id: "toxicity", label: "Toxicity", icon: Shield },
  { id: "response", label: "Drug Response", icon: Microscope },
  { id: "analyze", label: "Molecule Analysis", icon: FlaskConical },
];

function ResultCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5 space-y-3">
      <h3 className="text-sm font-semibold text-foreground">{title}</h3>
      {children}
    </motion.div>
  );
}

function KV({ label, value, mono = false, color }: { label: string; value: string | number | undefined; mono?: boolean; color?: string }) {
  return (
    <div className="flex justify-between text-xs">
      <span className="text-muted-foreground">{label}</span>
      <span className={`${mono ? "font-mono" : ""} ${color ?? "text-foreground"}`}>{value ?? "—"}</span>
    </div>
  );
}

export default function Predictions() {
  const [tab, setTab] = useState<PredictionTab>("binding");
  const [smiles, setSmiles] = useState("");
  const [targetName, setTargetName] = useState("");
  const [moleculeName, setMoleculeName] = useState("");
  const [diseaseContext, setDiseaseContext] = useState("");

  const bindingMutation = useMutation({
    mutationFn: () => api.predictBindingAffinity({ molecule_smiles: smiles, target_name: targetName }),
  });
  const toxicityMutation = useMutation({
    mutationFn: () => api.predictToxicity({ molecule_smiles: smiles, molecule_name: moleculeName || undefined }),
  });
  const responseMutation = useMutation({
    mutationFn: () => api.predictDrugResponse({ molecule_smiles: smiles, target_name: targetName, disease_context: diseaseContext || undefined }),
  });
  const analyzeMutation = useMutation({
    mutationFn: () => api.analyzeMolecule({ molecule_smiles: smiles }),
  });

  const isLoading = bindingMutation.isPending || toxicityMutation.isPending || responseMutation.isPending || analyzeMutation.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!smiles.trim()) return;
    if (tab === "binding") bindingMutation.mutate();
    else if (tab === "toxicity") toxicityMutation.mutate();
    else if (tab === "response") responseMutation.mutate();
    else analyzeMutation.mutate();
  };

  const riskColor = (risk: string) => risk === "low" ? "text-success" : risk === "medium" ? "text-warning" : "text-destructive";

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Prediction Tools</h1>
        <p className="text-sm text-muted-foreground">Run AI-powered molecular predictions</p>
      </div>

      <DisclaimerBanner />

      {/* Tabs */}
      <div className="flex flex-wrap gap-2">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={`flex items-center gap-2 rounded-lg border px-4 py-2.5 text-sm font-medium transition-all ${
              tab === id ? "border-primary/40 bg-primary/10 text-primary" : "border-border text-muted-foreground hover:bg-secondary"
            }`}
          >
            <Icon className="h-4 w-4" /> {label}
          </button>
        ))}
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        {/* Input Form */}
        <div className="glass-card p-5">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-muted-foreground">SMILES String *</label>
              <Textarea
                placeholder="e.g. NC(Cc1ccc(O)c(O)c1)C(O)=O"
                value={smiles}
                onChange={(e) => setSmiles(e.target.value)}
                className="font-mono text-sm bg-secondary border-border min-h-[80px]"
                required
              />
            </div>

            {(tab === "binding" || tab === "response") && (
              <div>
                <label className="mb-1.5 block text-xs font-medium text-muted-foreground">Target Name *</label>
                <Input
                  placeholder="e.g. TNF-alpha"
                  value={targetName}
                  onChange={(e) => setTargetName(e.target.value)}
                  className="bg-secondary border-border"
                  required
                />
              </div>
            )}

            {tab === "toxicity" && (
              <div>
                <label className="mb-1.5 block text-xs font-medium text-muted-foreground">Molecule Name (optional)</label>
                <Input
                  placeholder="e.g. Levodopa"
                  value={moleculeName}
                  onChange={(e) => setMoleculeName(e.target.value)}
                  className="bg-secondary border-border"
                />
              </div>
            )}

            {tab === "response" && (
              <div>
                <label className="mb-1.5 block text-xs font-medium text-muted-foreground">Disease Context (optional)</label>
                <Input
                  placeholder="e.g. Neuroinflammation"
                  value={diseaseContext}
                  onChange={(e) => setDiseaseContext(e.target.value)}
                  className="bg-secondary border-border"
                />
              </div>
            )}

            <Button type="submit" disabled={isLoading || !smiles.trim()} className="w-full bg-primary text-primary-foreground hover:bg-primary/90">
              {isLoading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Running Prediction...</> : "Run Prediction"}
            </Button>
          </form>
        </div>

        {/* Results */}
        <div className="space-y-4">
          <AnimatePresence mode="wait">
            {/* Binding Result */}
            {tab === "binding" && bindingMutation.data && (
              <ResultCard title="Binding Affinity Result">
                <div className="space-y-2">
                  <KV label="Target" value={bindingMutation.data.binding_affinity.target} />
                  <KV label="Binding Score" value={bindingMutation.data.binding_affinity.binding_score.toFixed(2)} mono color="text-primary" />
                  <KV label="Confidence" value={bindingMutation.data.binding_affinity.confidence} color={riskColor(bindingMutation.data.binding_affinity.confidence === "high" ? "low" : "medium")} />
                  <KV label="Method" value={bindingMutation.data.binding_affinity.method} />
                  {bindingMutation.data.binding_affinity.reasoning && (
                    <p className="text-xs text-muted-foreground mt-2">{bindingMutation.data.binding_affinity.reasoning}</p>
                  )}
                </div>
                <div className="border-t border-border pt-3 mt-3">
                  <p className="text-[10px] font-semibold text-muted-foreground mb-2">Molecule Properties</p>
                  <div className="grid grid-cols-2 gap-1">
                    <KV label="MW" value={bindingMutation.data.molecule_analysis.molecular_weight?.toFixed(1)} mono />
                    <KV label="LogP" value={bindingMutation.data.molecule_analysis.logp?.toFixed(2)} mono />
                    <KV label="HBD" value={bindingMutation.data.molecule_analysis.hbd} mono />
                    <KV label="HBA" value={bindingMutation.data.molecule_analysis.hba} mono />
                    <KV label="Drug Likeness" value={bindingMutation.data.molecule_analysis.drug_likeness} />
                    <KV label="PAINS" value={bindingMutation.data.molecule_analysis.pains_alerts} mono />
                  </div>
                </div>
              </ResultCard>
            )}

            {/* Toxicity Result */}
            {tab === "toxicity" && toxicityMutation.data && (
              <ResultCard title="Toxicity Assessment">
                <div className="space-y-2">
                  <KV label="Molecule" value={toxicityMutation.data.toxicity.molecule} />
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Risk Level</span>
                    <Badge variant="outline" className={`text-[10px] ${riskColor(toxicityMutation.data.toxicity.toxicity_risk)} border-current/30`}>
                      {toxicityMutation.data.toxicity.toxicity_risk}
                    </Badge>
                  </div>
                  <KV label="Confidence" value={toxicityMutation.data.toxicity.confidence} />
                  <KV label="Model" value={toxicityMutation.data.model} />
                </div>
                {toxicityMutation.data.toxicity.mechanism && (
                  <div className="border-t border-border pt-3">
                    <p className="text-[10px] font-semibold text-muted-foreground mb-1">Mechanism</p>
                    <p className="text-xs text-foreground">{toxicityMutation.data.toxicity.mechanism}</p>
                  </div>
                )}
                {toxicityMutation.data.toxicity.reasoning && (
                  <div>
                    <p className="text-[10px] font-semibold text-muted-foreground mb-1">Reasoning</p>
                    <p className="text-xs text-muted-foreground">{toxicityMutation.data.toxicity.reasoning}</p>
                  </div>
                )}
              </ResultCard>
            )}

            {/* Drug Response Result */}
            {tab === "response" && responseMutation.data && (
              <ResultCard title="Drug Response Prediction">
                <p className="text-sm text-foreground">{responseMutation.data.drug_response_prediction.overall_recommendation}</p>
                {responseMutation.data.drug_response_prediction.risk_factors?.length > 0 && (
                  <div>
                    <p className="text-[10px] font-semibold text-muted-foreground mb-1">Risk Factors</p>
                    <ul className="space-y-1">
                      {responseMutation.data.drug_response_prediction.risk_factors.map((r, i) => (
                        <li key={i} className="text-xs text-warning">• {r}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {responseMutation.data.drug_response_prediction.next_steps?.length > 0 && (
                  <div>
                    <p className="text-[10px] font-semibold text-muted-foreground mb-1">Next Steps</p>
                    <ul className="space-y-1">
                      {responseMutation.data.drug_response_prediction.next_steps.map((s, i) => (
                        <li key={i} className="text-xs text-muted-foreground">• {s}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="border-t border-border pt-3">
                  <p className="text-[10px] font-semibold text-muted-foreground mb-1">Models Used</p>
                  <div className="flex flex-wrap gap-1">
                    {responseMutation.data.models_used.map((m) => (
                      <Badge key={m} variant="secondary" className="text-[10px] font-mono">{m}</Badge>
                    ))}
                  </div>
                </div>
              </ResultCard>
            )}

            {/* Molecule Analysis Result */}
            {tab === "analyze" && analyzeMutation.data && (
              <ResultCard title="Molecule Analysis">
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(analyzeMutation.data.analysis).map(([k, v]) => (
                    <KV key={k} label={k.replace(/_/g, " ")} value={String(v)} mono />
                  ))}
                </div>
              </ResultCard>
            )}

            {/* Error */}
            {[bindingMutation, toxicityMutation, responseMutation, analyzeMutation].map((m, i) =>
              m.isError ? (
                <motion.div key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card border-destructive/30 bg-destructive/5 p-4">
                  <p className="text-sm text-destructive">Prediction failed: {(m.error as Error).message}</p>
                </motion.div>
              ) : null
            )}
          </AnimatePresence>

          {!bindingMutation.data && !toxicityMutation.data && !responseMutation.data && !analyzeMutation.data && !isLoading && (
            <div className="glass-card flex flex-col items-center justify-center py-16 text-center">
              <FlaskConical className="h-10 w-10 text-muted-foreground/30 mb-3" />
              <p className="text-sm text-muted-foreground">Enter a SMILES string and run a prediction</p>
              <p className="text-xs text-muted-foreground mt-1">Example: NC(Cc1ccc(O)c(O)c1)C(O)=O</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
