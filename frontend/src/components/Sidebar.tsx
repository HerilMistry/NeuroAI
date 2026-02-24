import { NavLink } from 'react-router-dom'
import {
    Home,
    Pill,
    GitBranch,
    Activity,
    AlertTriangle,
    Info,
    Brain
} from 'lucide-react'

const navItems = [
    { to: '/', icon: Home, label: 'Dashboard' },
    { to: '/drugs', icon: Pill, label: 'Drug Explorer' },
    { to: '/pathways', icon: GitBranch, label: 'Pathways' },
    { to: '/simulation', icon: Activity, label: 'Simulation' },
]

export function Sidebar() {
    return (
        <aside className="w-72 bg-gradient-to-b from-card via-card to-card/95 border-r border-border flex flex-col shadow-lg">
            {/* Logo/Brand */}
            <div className="p-6 border-b border-border/50 bg-gradient-to-r from-primary/10 to-accent/10">
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 rounded-lg bg-primary/20">
                        <Brain className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                        <h1 className="text-lg font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                            NeuroDegenRx
                        </h1>
                        <p className="text-xs text-muted-foreground mt-0.5">
                            Drug Discovery AI
                        </p>
                    </div>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-2">
                {navItems.map(({ to, icon: Icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${isActive
                                ? 'bg-gradient-to-r from-primary/25 to-primary/10 text-primary border border-primary/30 shadow-sm'
                                : 'text-muted-foreground hover:text-foreground hover:bg-muted/40'
                            }`
                        }
                    >
                        <Icon className="w-5 h-5" />
                        <span>{label}</span>
                    </NavLink>
                ))}
            </nav>

            {/* Caution Alert */}
            <div className="p-4 border-t border-border/50">
                <div className="bg-gradient-to-br from-destructive/10 to-destructive/5 border-2 border-destructive/30 rounded-lg p-4 space-y-2">
                    <div className="flex items-start gap-3">
                        <AlertTriangle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="text-xs font-bold text-destructive">Research Only</p>
                            <p className="text-xs text-muted-foreground mt-1.5">
                                Not for clinical use or medical decisions.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer Info */}
            <div className="p-4 border-t border-border/50">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <div className="flex items-center gap-2">
                        <Info className="w-4 h-4" />
                        <span>v1.0.0</span>
                    </div>
                    <span className="px-2 py-1 rounded-full bg-success/10 text-success text-xs font-medium">
                        Live
                    </span>
                </div>
            </div>
        </aside>
    )
}
