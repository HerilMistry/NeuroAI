import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, Pathway } from "@/lib/api";
import { Search, ChevronLeft, ChevronRight } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { motion } from "framer-motion";

const CATEGORIES = [
  "neuroinflammation", "mitochondrial", "protein_aggregation", "synaptic",
  "autophagy", "oxidative_stress", "apoptosis", "neurotransmission", "metabolism",
];

const CATEGORY_COLORS: Record<string, string> = {
  neuroinflammation: "text-destructive border-destructive/30",
  mitochondrial: "text-warning border-warning/30",
  protein_aggregation: "text-info border-info/30",
  synaptic: "text-primary border-primary/30",
  autophagy: "text-success border-success/30",
  oxidative_stress: "text-warning border-warning/30",
  apoptosis: "text-destructive border-destructive/30",
  neurotransmission: "text-primary border-primary/30",
  metabolism: "text-success border-success/30",
};

function PathwayCard({ pathway }: { pathway: Pathway }) {
  return (
    <div className="glass-card p-4 space-y-3 hover:border-primary/30 transition-colors">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-semibold text-foreground">{pathway.name}</p>
          <p className="font-mono text-[10px] text-muted-foreground">{pathway.pathway_id}</p>
        </div>
        <Badge variant="outline" className={`text-[10px] capitalize ${CATEGORY_COLORS[pathway.category] ?? "text-muted-foreground"}`}>
          {pathway.category?.replace(/_/g, " ")}
        </Badge>
      </div>
      {pathway.description && <p className="text-xs text-muted-foreground line-clamp-2">{pathway.description}</p>}
      <div className="flex items-center gap-4 text-xs text-muted-foreground">
        <span>Targets: <span className="font-mono text-foreground">{pathway.target_count}</span></span>
        <span>Relevance: <Badge variant="outline" className={`text-[10px] ${pathway.disease_relevance === "high" ? "text-success border-success/30" : pathway.disease_relevance === "medium" ? "text-warning border-warning/30" : "text-muted-foreground"}`}>{pathway.disease_relevance}</Badge></span>
        <span className="capitalize">Effect: <span className={pathway.activation_effect === "detrimental" ? "text-destructive" : "text-success"}>{pathway.activation_effect}</span></span>
      </div>
    </div>
  );
}

export default function PathwayBrowser() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [category, setCategory] = useState("");

  const params: Record<string, string> = { page: String(page) };
  if (search) params.search = search;
  if (category) params.category = category;

  const { data, isLoading } = useQuery({
    queryKey: ["pathways", params],
    queryFn: () => api.getPathways(params),
  });

  const totalPages = data ? Math.ceil(data.count / 20) : 0;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Pathway Browser</h1>
        <p className="text-sm text-muted-foreground">Explore disease-relevant biological pathways</p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search pathways..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="pl-9 bg-secondary border-border"
          />
        </div>
      </div>

      {/* Category pills */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => { setCategory(""); setPage(1); }}
          className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-all ${!category ? "border-primary/40 bg-primary/10 text-primary" : "border-border text-muted-foreground hover:border-border/80"}`}
        >
          All
        </button>
        {CATEGORIES.map((c) => (
          <button
            key={c}
            onClick={() => { setCategory(category === c ? "" : c); setPage(1); }}
            className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-all capitalize ${
              category === c ? "border-primary/40 bg-primary/10 text-primary" : "border-border text-muted-foreground hover:border-border/80"
            }`}
          >
            {c.replace(/_/g, " ")}
          </button>
        ))}
      </div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        {isLoading ? (
          <div className="flex items-center justify-center py-20 text-sm text-muted-foreground">Loading pathways...</div>
        ) : data?.results?.length ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {data.results.map((p) => <PathwayCard key={p.id} pathway={p} />)}
          </div>
        ) : (
          <div className="flex items-center justify-center py-20 text-sm text-muted-foreground">No pathways found</div>
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
