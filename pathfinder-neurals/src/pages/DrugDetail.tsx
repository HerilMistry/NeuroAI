import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ArrowLeft, AlertTriangle, Check, Brain, Shield, ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import { motion } from "framer-motion";

function ScoreBar({ label, value, max = 1.5 }: { label: string; value: number; max?: number }) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-mono text-foreground">{value.toFixed(2)}</span>
      </div>
      <div className="h-1.5 rounded-full bg-secondary">
        <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default function DrugDetail() {
  const { id } = useParams();
  const { data: drug, isLoading } = useQuery({
    queryKey: ["drug", id],
    queryFn: () => api.getDrug(Number(id)),
    enabled: !!id,
  });

  if (isLoading) return <div className="flex items-center justify-center py-20 text-muted-foreground">Loading...</div>;
  if (!drug) return <div className="py-20 text-center text-muted-foreground">Drug not found</div>;

  return (
    <div className="space-y-6">
      <Link to="/drugs" className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors">
        <ArrowLeft className="h-4 w-4" /> Back to drugs
      </Link>

      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">{drug.name}</h1>
          <p className="font-mono text-sm text-muted-foreground mt-1">
            {drug.drugbank_id} {drug.chembl_id && `· ${drug.chembl_id}`}
          </p>
          {drug.description && <p className="mt-2 max-w-2xl text-sm text-muted-foreground">{drug.description}</p>}
        </div>
        <div className="flex gap-2">
          {drug.cns_viable && <Badge variant="outline" className="border-success/40 text-success"><Brain className="mr-1 h-3 w-3" /> CNS Viable</Badge>}
          {drug.is_approved && <Badge variant="outline" className="border-primary/40 text-primary"><Check className="mr-1 h-3 w-3" /> {drug.approval_status}</Badge>}
          {drug.safety_summary?.has_warnings && <Badge variant="outline" className="border-destructive/40 text-destructive"><AlertTriangle className="mr-1 h-3 w-3" /> Warnings</Badge>}
        </div>
      </motion.div>

      <div className="grid gap-5 lg:grid-cols-3">
        {/* Properties */}
        <div className="glass-card p-5 space-y-4">
          <h2 className="text-sm font-semibold text-foreground">Molecular Properties</h2>
          <div className="grid grid-cols-2 gap-3">
            {[
              ["MW", drug.molecular_weight?.toFixed(1)],
              ["LogP", drug.logp?.toFixed(2)],
              ["HBD", drug.hbd],
              ["HBA", drug.hba],
              ["TPSA", drug.tpsa?.toFixed(1)],
              ["Rot. Bonds", drug.rotatable_bonds],
              ["PAINS", drug.pains_alerts],
              ["pKa", drug.pka?.toFixed(2)],
            ].map(([label, val]) => (
              <div key={String(label)}>
                <p className="text-[10px] text-muted-foreground">{label}</p>
                <p className="font-mono text-sm text-foreground">{val ?? "—"}</p>
              </div>
            ))}
          </div>
          {drug.smiles && (
            <div>
              <p className="text-[10px] text-muted-foreground mb-1">SMILES</p>
              <p className="smiles-text">{drug.smiles}</p>
            </div>
          )}
        </div>

        {/* CNS Score */}
        <div className="glass-card p-5 space-y-4">
          <h2 className="text-sm font-semibold text-foreground">CNS MPO Score</h2>
          <div className="text-center">
            <p className={`stat-value ${drug.cns_mpo_score >= 4 ? "text-success" : "text-warning"}`}>
              {drug.cns_mpo_score?.toFixed(1)} <span className="text-base text-muted-foreground">/ 6.0</span>
            </p>
          </div>
          {drug.cns_score_explanation && (
            <div className="space-y-3 mt-4">
              {Object.entries(drug.cns_score_explanation).map(([key, val]) => (
                <ScoreBar key={key} label={key.replace(/_/g, " ")} value={val} />
              ))}
            </div>
          )}
        </div>

        {/* Safety */}
        <div className="glass-card p-5 space-y-4">
          <h2 className="text-sm font-semibold text-foreground">Safety Summary</h2>
          {drug.safety_summary?.has_warnings ? (
            <div className="space-y-2">
              {drug.safety_summary.warnings.map((w, i) => (
                <div key={i} className="flex items-start gap-2 rounded-lg border border-destructive/20 bg-destructive/5 p-2.5">
                  <AlertTriangle className="mt-0.5 h-3.5 w-3.5 text-destructive shrink-0" />
                  <p className="text-xs text-foreground">{w}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center gap-2 rounded-lg border border-success/20 bg-success/5 p-3">
              <Shield className="h-4 w-4 text-success" />
              <p className="text-sm text-success">No safety warnings detected</p>
            </div>
          )}
          {drug.categories?.length > 0 && (
            <div>
              <p className="text-[10px] text-muted-foreground mb-2">Categories</p>
              <div className="flex flex-wrap gap-1.5">
                {drug.categories.map((c) => (
                  <Badge key={c} variant="secondary" className="text-[10px]">{c}</Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Target Interactions */}
      {drug.target_interactions?.length > 0 && (
        <div className="glass-card overflow-hidden">
          <div className="border-b border-border px-5 py-3">
            <h2 className="text-sm font-semibold text-foreground">Target Interactions ({drug.target_interactions.length})</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-xs text-muted-foreground">
                  <th className="px-5 py-2.5 text-left">Target</th>
                  <th className="px-5 py-2.5 text-left">Type</th>
                  <th className="px-5 py-2.5 text-right">Affinity (nM)</th>
                  <th className="px-5 py-2.5 text-right">Confidence</th>
                  <th className="px-5 py-2.5 text-left">Evidence</th>
                  <th className="px-5 py-2.5 text-left">Source</th>
                </tr>
              </thead>
              <tbody>
                {drug.target_interactions.map((t) => (
                  <tr key={t.id} className="border-b border-border/50 hover:bg-secondary/20">
                    <td className="px-5 py-2.5">
                      <Link to={`/targets/${t.target}`} className="font-semibold text-primary hover:underline">{t.target_gene_symbol}</Link>
                      <p className="text-xs text-muted-foreground">{t.target_name}</p>
                    </td>
                    <td className="px-5 py-2.5 capitalize text-muted-foreground">{t.activity_type}</td>
                    <td className="px-5 py-2.5 text-right font-mono">{t.affinity_nm?.toFixed(1)}</td>
                    <td className="px-5 py-2.5 text-right font-mono">{(t.confidence_score * 100).toFixed(0)}%</td>
                    <td className="px-5 py-2.5">
                      <Badge variant="outline" className={`text-[10px] ${t.evidence_level === "high" ? "text-success border-success/30" : "text-warning border-warning/30"}`}>
                        {t.evidence_level}
                      </Badge>
                    </td>
                    <td className="px-5 py-2.5 text-xs text-muted-foreground">{t.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Pathway Effects */}
      {drug.pathway_effects?.length > 0 && (
        <div className="glass-card overflow-hidden">
          <div className="border-b border-border px-5 py-3">
            <h2 className="text-sm font-semibold text-foreground">Pathway Effects ({drug.pathway_effects.length})</h2>
          </div>
          <div className="divide-y divide-border">
            {drug.pathway_effects.map((pe) => (
              <div key={pe.id} className="px-5 py-3.5 hover:bg-secondary/20">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-foreground">{pe.pathway_name}</p>
                    <p className="text-xs text-muted-foreground capitalize">{pe.pathway_category}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className={`text-[10px] ${pe.direction === "activation" ? "text-info border-info/30" : pe.direction === "inhibition" ? "text-warning border-warning/30" : "text-muted-foreground"}`}>
                      {pe.direction}
                    </Badge>
                    <Badge variant="outline" className={`text-[10px] ${pe.disease_impact === "beneficial" ? "text-success border-success/30" : pe.disease_impact === "detrimental" ? "text-destructive border-destructive/30" : "text-muted-foreground"}`}>
                      {pe.disease_impact}
                    </Badge>
                  </div>
                </div>
                {pe.explanation && <p className="mt-1.5 text-xs text-muted-foreground">{pe.explanation}</p>}
                <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
                  <span>Perturbation: <span className="font-mono text-foreground">{pe.perturbation_score?.toFixed(2)}</span></span>
                  <span>Confidence: <span className="font-mono text-foreground">{(pe.confidence * 100).toFixed(0)}%</span></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <DisclaimerBanner compact />
    </div>
  );
}
