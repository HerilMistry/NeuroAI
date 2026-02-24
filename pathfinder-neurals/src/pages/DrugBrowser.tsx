import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, Drug } from "@/lib/api";
import { Link } from "react-router-dom";
import { Search, Filter, Check, X, Brain, ChevronLeft, ChevronRight } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { motion } from "framer-motion";

function DrugRow({ drug }: { drug: Drug }) {
  return (
    <Link
      to={`/drugs/${drug.id}`}
      className="flex items-center gap-4 border-b border-border px-5 py-3.5 transition-colors hover:bg-secondary/30"
    >
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-foreground truncate">{drug.name}</p>
        <p className="font-mono text-xs text-muted-foreground">
          {drug.drugbank_id} {drug.chembl_id && `· ${drug.chembl_id}`}
        </p>
      </div>
      <div className="hidden sm:flex items-center gap-3">
        <div className="text-right">
          <p className="text-xs text-muted-foreground">MW</p>
          <p className="font-mono text-xs text-foreground">{drug.molecular_weight?.toFixed(1)}</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-muted-foreground">LogP</p>
          <p className="font-mono text-xs text-foreground">{drug.logp?.toFixed(2)}</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-muted-foreground">CNS MPO</p>
          <p className={`font-mono text-xs font-semibold ${drug.cns_mpo_score >= 4 ? "text-success" : "text-warning"}`}>
            {drug.cns_mpo_score?.toFixed(1)}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        {drug.cns_viable && (
          <Badge variant="outline" className="border-success/40 text-success text-[10px]">
            <Brain className="mr-1 h-3 w-3" /> CNS
          </Badge>
        )}
        {drug.is_approved ? (
          <Badge variant="outline" className="border-primary/40 text-primary text-[10px]">
            <Check className="mr-1 h-3 w-3" /> Approved
          </Badge>
        ) : (
          <Badge variant="outline" className="border-muted-foreground/40 text-muted-foreground text-[10px]">
            <X className="mr-1 h-3 w-3" /> Unapproved
          </Badge>
        )}
      </div>
    </Link>
  );
}

export default function DrugBrowser() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [cnsFilter, setCnsFilter] = useState<string>("");
  const [approvedFilter, setApprovedFilter] = useState<string>("");

  const params: Record<string, string> = { page: String(page) };
  if (search) params.search = search;
  if (cnsFilter) params.cns_viable = cnsFilter;
  if (approvedFilter) params.is_approved = approvedFilter;

  const { data, isLoading } = useQuery({
    queryKey: ["drugs", params],
    queryFn: () => api.getDrugs(params),
  });

  const totalPages = data ? Math.ceil(data.count / 20) : 0;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Drug Browser</h1>
        <p className="text-sm text-muted-foreground">Search and explore drug compounds</p>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search by name, DrugBank ID, ChEMBL ID..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="pl-9 bg-secondary border-border"
          />
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => { setCnsFilter(cnsFilter === "true" ? "" : "true"); setPage(1); }}
            className={`flex items-center gap-1.5 rounded-lg border px-3 py-2 text-xs font-medium transition-all ${
              cnsFilter === "true" ? "border-success/40 bg-success/10 text-success" : "border-border text-muted-foreground hover:border-border/80"
            }`}
          >
            <Brain className="h-3.5 w-3.5" /> CNS Viable
          </button>
          <button
            onClick={() => { setApprovedFilter(approvedFilter === "true" ? "" : "true"); setPage(1); }}
            className={`flex items-center gap-1.5 rounded-lg border px-3 py-2 text-xs font-medium transition-all ${
              approvedFilter === "true" ? "border-primary/40 bg-primary/10 text-primary" : "border-border text-muted-foreground hover:border-border/80"
            }`}
          >
            <Filter className="h-3.5 w-3.5" /> Approved Only
          </button>
        </div>
      </div>

      {/* Results */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-20 text-sm text-muted-foreground">Loading drugs...</div>
        ) : data?.results?.length ? (
          <>
            <div className="border-b border-border px-5 py-2.5">
              <p className="text-xs text-muted-foreground">{data.count} results</p>
            </div>
            {data.results.map((drug) => (
              <DrugRow key={drug.id} drug={drug} />
            ))}
          </>
        ) : (
          <div className="flex items-center justify-center py-20 text-sm text-muted-foreground">
            {search ? "No drugs match your search" : "No drugs found. Is the backend running?"}
          </div>
        )}
      </motion.div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3">
          <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="rounded-lg border border-border p-2 text-muted-foreground disabled:opacity-30 hover:bg-secondary">
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page === totalPages} className="rounded-lg border border-border p-2 text-muted-foreground disabled:opacity-30 hover:bg-secondary">
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}
