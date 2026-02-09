import { HelpCircle } from 'lucide-react'

export function Header() {
    return (
        <header className="h-14 border-b border-border bg-card flex items-center justify-between px-6">
            <div>
                {/* Breadcrumb or page title can go here */}
            </div>

            <div className="flex items-center gap-4">
                <button className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
                    <HelpCircle className="w-4 h-4" />
                    <span>Documentation</span>
                </button>
            </div>
        </header>
    )
}
