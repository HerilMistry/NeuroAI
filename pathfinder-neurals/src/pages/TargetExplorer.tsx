import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, Target } from "@/lib/api";
import { Link } from "react-router-dom";
import { Search, ChevronLeft, ChevronRight, AlertTriangle, Brain } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { motion } from "framer-motion";

const EXPRESSION_COLORS: Record<string, string> = {
  high: "text-success border-success/30",
  medium: "text-warning border-warning/30",
  low: "text-muted-foreground border-muted-foreground/30",
  not_detected: "text-destructive border-destructive/30",
};

function TargetRow({ target }: { target: Target }) {
  return (
    <Link
      to={`/targets/${target.id}`}
      className="flex items-center gap-4 border-b border-border px-5 py-3.5 transition-colors hover:bg-secondary/30"
    >
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-foreground">{target.gene_symbol}</p>
        <p className="text-xs text-muted-foreground truncate">{target.protein_name}</p>
      </div>
      <div className="hidden sm:block text-right">
        <p className="text-xs text-muted-foreground">Relevance</p>
        <p className="font-mono text-sm font-semibold text-primary">{(target.disease_relevance_score * 100).toFixed(0)}%</p>
      </div>
      <Badge variant="outline" className={`text-[10px] ${EXPRESSION_COLORS[target.brain_expression_level] ?? ""}`}>
        <Brain className="mr-1 h-3 w-3" /> {target.brain_expression_level}
      </Badge>
      {target.is_toxicity_associated && (
        <Badge variant="outline" className="text-[10px] text-destructive border-destructive/30">
          <AlertTriangle className="mr-1 h-3 w-3" /> Toxic
        </Badge>
      )}
    </Link>
  );
}

export default function TargetExplorer() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [expression, setExpression] = useState("");

  const params: Record<string, string> = { page: String(page) };
  if (search) params.search = search;
  if (expression) params.brain_expression_level = expression;

  const { data, isLoading } = useQuery({
    queryKey: ["targets", params],
    queryFn: () => api.getTargets(params),
  });

  const totalPages = data ? Math.ceil(data.count / 20) : 0;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Target Explorer</h1>
        <p className="text-sm text-muted-foreground">Browse biological targets with disease relevance scoring</p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search by gene symbol or protein name..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="pl-9 bg-secondary border-border"
          />
        </div>
        <div className="flex gap-2">
          {["high", "medium", "low"].map((level) => (
            <button
              key={level}
              onClick={() => { setExpression(expression === level ? "" : level); setPage(1); }}
              className={`rounded-lg border px-3 py-2 text-xs font-medium transition-all capitalize ${
                expression === level ? "border-primary/40 bg-primary/10 text-primary" : "border-border text-muted-foreground hover:border-border/80"
              }`}
            >
              {level} Expression
            </button>
          ))}
        </div>
      </div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-20 text-sm text-muted-foreground">Loading targets...</div>
        ) : data?.results?.length ? (
          <>
            <div className="border-b border-border px-5 py-2.5">
              <p className="text-xs text-muted-foreground">{data.count} targets</p>
            </div>
            {data.results.map((t) => <TargetRow key={t.id} target={t} />)}
          </>
        ) : (
          <div className="flex items-center justify-center py-20 text-sm text-muted-foreground">No targets found</div>
        )}
      </motion.div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3">
          <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="rounded-lg border border-border p-2 text-muted-foreground disabled:opacity-30 hover:bg-secondary">
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="text-sm text-muted-foreground">Page {page} of {totalPages}</span>
          <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page === totalPages} className="rounded-lg border border-border p-2 text-muted-foreground disabled:opacity-30 hover:bg-secondary">
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}
