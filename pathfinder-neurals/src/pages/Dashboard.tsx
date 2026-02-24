import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Pill, Target, Route, Brain, FlaskConical, Database, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import { Link } from "react-router-dom";

function StatCard({ icon: Icon, label, value, color }: { icon: React.ElementType; label: string; value: string | number; color: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-5"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="stat-value mt-1" style={{ color: `hsl(var(--${color}))` }}>{value}</p>
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-lg" style={{ backgroundColor: `hsl(var(--${color}) / 0.1)` }}>
          <Icon className="h-5 w-5" style={{ color: `hsl(var(--${color}))` }} />
        </div>
      </div>
    </motion.div>
  );
}

function QuickAction({ to, icon: Icon, title, desc }: { to: string; icon: React.ElementType; title: string; desc: string }) {
  return (
    <Link to={to} className="glass-card flex items-center gap-4 p-4 transition-all hover:border-primary/40 hover:glow-cyan">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
        <Icon className="h-5 w-5 text-primary" />
      </div>
      <div>
        <p className="text-sm font-semibold text-foreground">{title}</p>
        <p className="text-xs text-muted-foreground">{desc}</p>
      </div>
    </Link>
  );
}

export default function Dashboard() {
  const { data: systemInfo, isLoading } = useQuery({
    queryKey: ["system"],
    queryFn: api.getSystemInfo,
    retry: 1,
  });

  const stats = systemInfo?.statistics;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">NeuroAI Platform</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Multimodal AI for computational drug discovery in neurodegenerative diseases
        </p>
      </div>

      <DisclaimerBanner />

      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Pill} label="Total Drugs" value={isLoading ? "—" : stats?.drug_count ?? "—"} color="primary" />
        <StatCard icon={Target} label="Targets" value={isLoading ? "—" : stats?.target_count ?? "—"} color="info" />
        <StatCard icon={Route} label="Pathways" value={isLoading ? "—" : stats?.pathway_count ?? "—"} color="chart-purple" />
        <StatCard icon={Brain} label="CNS-Viable Drugs" value={isLoading ? "—" : stats?.cns_viable_drugs ?? "—"} color="success" />
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="mb-3 text-lg font-semibold text-foreground">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <QuickAction to="/drugs" icon={Pill} title="Browse Drugs" desc="Explore 150+ drugs in the database" />
          <QuickAction to="/targets" icon={Target} title="Explore Targets" desc="500+ biological targets with disease relevance" />
          <QuickAction to="/pathways" icon={Route} title="View Pathways" desc="45+ disease-relevant biological pathways" />
          <QuickAction to="/predictions" icon={FlaskConical} title="Run Predictions" desc="Binding affinity, toxicity & drug response" />
          <QuickAction to="/simulation" icon={Database} title="Simulate" desc="Disease progression with drug interventions" />
        </div>
      </div>

      {/* ML Models */}
      {systemInfo?.ml_models && (
        <div>
          <h2 className="mb-3 text-lg font-semibold text-foreground">ML Models</h2>
          <div className="glass-card divide-y divide-border">
            {Object.entries(systemInfo.ml_models).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between px-5 py-3">
                <span className="text-sm text-muted-foreground capitalize">{key.replace(/_/g, " ")}</span>
                <span className="font-mono text-xs text-primary">{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Connection status */}
      {!isLoading && !systemInfo && (
        <div className="glass-card flex items-center gap-3 border-destructive/30 bg-destructive/5 p-4">
          <AlertTriangle className="h-5 w-5 text-destructive" />
          <div>
            <p className="text-sm font-medium text-destructive">Backend Unavailable</p>
            <p className="text-xs text-muted-foreground">
              Ensure the Django server is running at http://localhost:8000
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
