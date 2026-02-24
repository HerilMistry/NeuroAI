import { AlertTriangle } from "lucide-react";

export function DisclaimerBanner({ compact = false }: { compact?: boolean }) {
  if (compact) {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-warning/30 bg-warning/5 px-3 py-2 text-xs text-warning">
        <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
        <span>Exploratory AI only — not clinically validated</span>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-warning/30 bg-warning/5 p-4">
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-warning" />
        <div className="space-y-1">
          <p className="text-sm font-medium text-warning">Research Tool — Not for Clinical Use</p>
          <ul className="space-y-0.5 text-xs text-muted-foreground">
            <li>• This is exploratory AI, NOT clinical prediction</li>
            <li>• Results should be reviewed by domain experts</li>
            <li>• No diagnostic or treatment recommendations are made</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
