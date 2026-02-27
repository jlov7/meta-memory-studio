import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface StatusPillProps {
  outcome: string;
  className?: string;
}

export function StatusPill({ outcome, className }: StatusPillProps) {
  const lower = outcome.toLowerCase();
  const variant =
    lower === "success"
      ? "success"
      : lower === "fail" || lower === "failure" || lower === "error"
        ? "danger"
        : "muted";

  return (
    <Badge variant={variant} className={cn("capitalize", className)}>
      {outcome}
    </Badge>
  );
}
