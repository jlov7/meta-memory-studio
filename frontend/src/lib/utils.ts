import { clsx, type ClassValue } from "clsx";
import { formatDistanceToNow, format, parseISO } from "date-fns";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "—";
  try {
    return format(parseISO(dateStr), "MMM d, yyyy HH:mm");
  } catch {
    return "—";
  }
}

export function formatDateRelative(dateStr: string | null | undefined): string {
  if (!dateStr) return "—";
  try {
    return formatDistanceToNow(parseISO(dateStr), { addSuffix: true });
  } catch {
    return "—";
  }
}

export function formatDelta(delta: number): string {
  const sign = delta > 0 ? "+" : "";
  return `${sign}${delta.toFixed(3)}`;
}

export function formatWeight(weight: number): string {
  return weight.toFixed(3);
}

export function formatDuration(
  startStr: string | null,
  endStr: string | null
): string {
  if (!startStr || !endStr) return "—";
  try {
    const start = parseISO(startStr);
    const end = parseISO(endStr);
    const ms = end.getTime() - start.getTime();
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
  } catch {
    return "—";
  }
}

export function parseContent(content: string): unknown {
  try {
    return JSON.parse(content);
  } catch {
    return content;
  }
}

export function outcomeColor(outcome: string): string {
  switch (outcome.toLowerCase()) {
    case "success":
      return "text-success";
    case "fail":
    case "failure":
    case "error":
      return "text-danger";
    default:
      return "text-muted-foreground";
  }
}
