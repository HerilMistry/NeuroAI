import { HelpCircle, Zap } from 'lucide-react'

export function Header() {
    return (
        <header className="h-16 border-b border-border bg-gradient-to-r from-card via-card to-card/80 flex items-center justify-between px-8 shadow-sm">
            <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-primary/10">
                    <Zap className="w-4 h-4 text-primary" />
                    <span className="text-xs font-semibold text-primary">ML Powered</span>
                </div>
            </div>

            <div className="flex items-center gap-6">
                <a 
                    href="#docs" 
                    className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors duration-200 hover:gap-3"
                >
                    <HelpCircle className="w-4 h-4" />
                    <span>Help</span>
                </a>
            </div>
        </header>
    )
}
