"use client";

import { useState } from "react";
import Link from "next/link";
import {
  User,
  Bot,
  Wrench,
  Database,
  MessageSquare,
  ChevronDown,
  ChevronRight,
  Copy,
  CheckCheck,
  Brain,
} from "lucide-react";
import { type TimelineStep } from "@/types/api";
import { cn, parseContent } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

const EVENT_ICONS: Record<string, React.ElementType> = {
  user_message: User,
  user_feedback: User,
  agent_message: Bot,
  agent_action: Bot,
  tool_call: Wrench,
  tool_result: Database,
  memory_retrieval: Brain,
  run_start: MessageSquare,
  run_end: MessageSquare,
};

const EVENT_COLORS: Record<string, string> = {
  user_message: "text-accent border-accent",
  user_feedback: "text-accent border-accent",
  agent_message: "text-success border-success",
  agent_action: "text-success border-success",
  tool_call: "text-warning border-warning",
  tool_result: "text-warning border-warning",
  memory_retrieval: "text-accent border-accent",
  run_start: "text-muted border-muted",
  run_end: "text-muted border-muted",
};

interface TimelineProps {
  steps: TimelineStep[];
  workspaceId: string;
}

export function Timeline({ steps, workspaceId }: TimelineProps) {
  return (
    <div className="space-y-1">
      {steps.map((step) => (
        <TimelineItem
          key={step.id}
          step={step}
          workspaceId={workspaceId}
        />
      ))}
    </div>
  );
}

function TimelineItem({
  step,
  workspaceId,
}: {
  step: TimelineStep;
  workspaceId: string;
}) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const Icon = EVENT_ICONS[step.event_type] ?? MessageSquare;
  const colorClass = EVENT_COLORS[step.event_type] ?? "text-muted border-muted";
  const parsed = parseContent(step.content);
  const isMemoryRetrieval = step.event_type === "memory_retrieval";

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(parsed, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="relative flex gap-3">
      {/* Line */}
      <div className="flex flex-col items-center">
        <div
          className={cn(
            "flex h-7 w-7 shrink-0 items-center justify-center rounded-full border bg-bg",
            colorClass
          )}
        >
          <Icon className="h-3.5 w-3.5" />
        </div>
        <div className="flex-1 w-px bg-border mt-1" />
      </div>

      {/* Content */}
      <div className="mb-3 flex-1 min-w-0">
        <div
          className="flex cursor-pointer items-center gap-2 pb-1"
          onClick={() => setExpanded((e) => !e)}
        >
          <span className="text-xs font-medium text-muted-foreground">
            {step.sequence}
          </span>
          <Badge variant="outline" className="font-mono text-[10px]">
            {step.event_type}
          </Badge>
          <span className="text-xs text-muted">{step.actor}</span>
          {isMemoryRetrieval && (
            <Badge variant="default" className="gap-1 text-[10px]">
              <Brain className="h-2.5 w-2.5" />
              memory
            </Badge>
          )}
          <div className="ml-auto">
            {expanded ? (
              <ChevronDown className="h-3.5 w-3.5 text-muted" />
            ) : (
              <ChevronRight className="h-3.5 w-3.5 text-muted" />
            )}
          </div>
        </div>

        {expanded && (
          <div className="mt-1 rounded-md border border-border bg-surface">
            <div className="flex items-center justify-between border-b border-border px-3 py-1.5">
              <span className="text-xs text-muted-foreground font-mono">
                payload
              </span>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 text-xs text-muted hover:text-foreground transition-colors"
              >
                {copied ? (
                  <CheckCheck className="h-3 w-3 text-success" />
                ) : (
                  <Copy className="h-3 w-3" />
                )}
              </button>
            </div>
            <pre className="overflow-auto p-3 text-xs text-foreground-subtle font-mono max-h-64">
              {JSON.stringify(parsed, null, 2)}
            </pre>

            {/* Memory links */}
            {isMemoryRetrieval && typeof parsed === "object" && parsed !== null && (
              <MemoryLinks payload={parsed as Record<string, unknown>} workspaceId={workspaceId} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function MemoryLinks({
  payload,
  workspaceId,
}: {
  payload: Record<string, unknown>;
  workspaceId: string;
}) {
  const candidates = (
    (payload.candidates ?? payload.memories_retrieved ?? []) as unknown[]
  ).filter(Boolean);

  if (!candidates.length) return null;

  return (
    <div className="border-t border-border px-3 py-2">
      <p className="mb-1 text-xs font-medium text-muted-foreground">
        Retrieved memories
      </p>
      <div className="space-y-1">
        {candidates.map((c, i) => {
          const mem = typeof c === "string" ? { memory_id: c } : (c as Record<string, unknown>);
          const id = mem.memory_id as string;
          const title = mem.title as string | undefined;
          return (
            <Link
              key={i}
              href={`/workspaces/${workspaceId}/memory/${id}`}
              className="flex items-center gap-2 text-xs text-accent hover:underline"
            >
              <Brain className="h-3 w-3 shrink-0" />
              {title ?? id}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
