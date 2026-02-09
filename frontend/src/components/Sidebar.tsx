import { NavLink } from 'react-router-dom'
import {
    Home,
    Pill,
    GitBranch,
    Activity,
    AlertTriangle,
    Info
} from 'lucide-react'

const navItems = [
    { to: '/', icon: Home, label: 'Dashboard' },
    { to: '/drugs', icon: Pill, label: 'Drug Explorer' },
    { to: '/pathways', icon: GitBranch, label: 'Pathways' },
    { to: '/simulation', icon: Activity, label: 'Simulation' },
]

export function Sidebar() {
    return (
        <aside className="w-64 bg-card border-r border-border flex flex-col">
            {/* Logo/Brand */}
            <div className="p-4 border-b border-border">
                <h1 className="text-xl font-bold text-primary">NeuroDegenRx</h1>
                <p className="text-xs text-muted-foreground mt-1">
                    Drug Discovery Platform
                </p>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-1">
                {navItems.map(({ to, icon: Icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive
                                ? 'bg-primary/10 text-primary'
                                : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                            }`
                        }
                    >
                        <Icon className="w-4 h-4" />
                        {label}
                    </NavLink>
                ))}
            </nav>

            {/* Warning Footer */}
            <div className="p-4 border-t border-border">
                <div className="bg-warning/10 border border-warning/30 rounded-md p-3">
                    <div className="flex items-start gap-2">
                        <AlertTriangle className="w-4 h-4 text-warning flex-shrink-0 mt-0.5" />
                        <div className="text-xs">
                            <p className="font-medium text-warning">Research Use Only</p>
                            <p className="text-muted-foreground mt-1">
                                Not for clinical decisions or medical advice.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Info */}
            <div className="p-4 border-t border-border">
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Info className="w-3 h-3" />
                    <span>v1.0.0</span>
                </div>
            </div>
        </aside>
    )
}
