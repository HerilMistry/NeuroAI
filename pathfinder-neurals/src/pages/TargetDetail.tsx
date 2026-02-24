import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ArrowLeft, AlertTriangle, Brain, Shield } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { motion } from "framer-motion";

export default function TargetDetail() {
  const { id } = useParams();
  const { data: target, isLoading } = useQuery({
    queryKey: ["target", id],
    queryFn: () => api.getTarget(Number(id)),
    enabled: !!id,
  });

  if (isLoading) return <div className="flex items-center justify-center py-20 text-muted-foreground">Loading...</div>;
  if (!target) return <div className="py-20 text-center text-muted-foreground">Target not found</div>;

  return (
    <div className="space-y-6">
      <Link to="/targets" className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Back to targets
      </Link>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-3xl font-bold text-foreground">{target.gene_symbol}</h1>
            <p className="text-sm text-muted-foreground">{target.protein_name}</p>
            {target.description && <p className="mt-2 max-w-2xl text-sm text-muted-foreground">{target.description}</p>}
          </div>
          <div className="flex gap-2">
            <Badge variant="outline" className="border-primary/40 text-primary">
              <Brain className="mr-1 h-3 w-3" /> {target.brain_expression_level} expression
            </Badge>
            {target.is_toxicity_associated && (
              <Badge variant="outline" className="border-destructive/40 text-destructive">
                <AlertTriangle className="mr-1 h-3 w-3" /> Toxicity associated
              </Badge>
            )}
          </div>
        </div>
      </motion.div>

      <div className="grid gap-5 lg:grid-cols-3">
        <div className="glass-card p-5 space-y-3">
          <h2 className="text-sm font-semibold text-foreground">Identifiers</h2>
          {[
            ["UniProt", target.uniprot_id],
            ["Ensembl", target.ensembl_id],
            ["Entrez", target.entrez_id],
            ["Class", target.protein_class],
            ["Source", target.data_source],
          ].map(([l, v]) => (
            <div key={String(l)}>
              <p className="text-[10px] text-muted-foreground">{l}</p>
              <p className="font-mono text-sm text-foreground">{v || "—"}</p>
            </div>
          ))}
        </div>

        <div className="glass-card p-5 space-y-3">
          <h2 className="text-sm font-semibold text-foreground">Disease Relevance</h2>
          <p className="stat-value text-primary">{(target.disease_relevance_score * 100).toFixed(0)}%</p>
          {target.disease_associations?.length > 0 && (
            <div className="space-y-2 mt-3">
              {target.disease_associations.map((da, i) => (
                <div key={i} className="flex justify-between text-xs">
                  <span className="text-foreground">{da.disease}</span>
                  <span className="font-mono text-primary">{(da.score * 100).toFixed(0)}%</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="glass-card p-5 space-y-3">
          <h2 className="text-sm font-semibold text-foreground">Stats</h2>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-[10px] text-muted-foreground">Known Drugs</p>
              <p className="stat-value text-info">{target.known_drug_count}</p>
            </div>
            <div>
              <p className="text-[10px] text-muted-foreground">Promiscuous</p>
              <p className="text-sm font-semibold">{target.is_promiscuous_target ? "Yes" : "No"}</p>
            </div>
          </div>
          {target.subcellular_location?.length > 0 && (
            <div>
              <p className="text-[10px] text-muted-foreground mb-1">Subcellular Location</p>
              <div className="flex flex-wrap gap-1">
                {target.subcellular_location.map((l) => (
                  <Badge key={l} variant="secondary" className="text-[10px]">{l}</Badge>
                ))}
              </div>
            </div>
          )}
          {target.is_toxicity_associated && target.toxicity_evidence && (
            <div className="rounded-lg border border-destructive/20 bg-destructive/5 p-2.5">
              <p className="text-xs text-destructive">{target.toxicity_evidence}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
