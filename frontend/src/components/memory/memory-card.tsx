"use client";

import Link from "next/link";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Trash2, Archive, Brain, Copy } from "lucide-react";
import { type MemoryOut } from "@/types/api";
import { deprecateMemory, forgetMemory } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip";
import { formatWeight, formatDateRelative } from "@/lib/utils";

interface MemoryCardProps {
  workspaceId: string;
  memory: MemoryOut;
  deduped?: boolean;
}

export function MemoryCard({ workspaceId, memory, deduped = false }: MemoryCardProps) {
  const qc = useQueryClient();
  const invalidate = () =>
    qc.invalidateQueries({ queryKey: queryKeys.memory.list(workspaceId) });

  const { mutate: deprecate } = useMutation({
    mutationFn: () => deprecateMemory(workspaceId, memory.id),
    onSuccess: invalidate,
  });

  const { mutate: forget } = useMutation({
    mutationFn: () => forgetMemory(workspaceId, memory.id),
    onSuccess: invalidate,
  });

  const weightColor =
    memory.current_weight > 1.5
      ? "text-success"
      : memory.current_weight < 0.5
        ? "text-danger"
        : "text-foreground";

  return (
    <div data-testid="memory-card" className="group relative rounded-lg border border-border bg-surface p-4 hover:border-accent/50 transition-colors">
      {/* Header */}
      <div className="mb-2 flex items-start justify-between gap-2">
        <Link
          href={`/workspaces/${workspaceId}/memory/${memory.id}`}
          className="text-sm font-medium text-foreground hover:text-accent line-clamp-2 leading-snug"
        >
          {memory.title}
        </Link>
        <div className="flex shrink-0 gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={() => deprecate()}
              >
                <Archive className="h-3 w-3" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Deprecate</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 hover:text-danger"
                onClick={() => {
                  if (confirm(`Permanently forget "${memory.title}"?`)) forget();
                }}
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Forget (permanent)</TooltipContent>
          </Tooltip>
        </div>
      </div>

      {/* Content preview */}
      <p className="mb-3 text-xs text-muted-foreground line-clamp-2">
        {memory.content}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="h-3 w-3 text-muted" />
          <Badge variant="outline" className="text-[10px]">
            {memory.memory_type}
          </Badge>
          {deduped && (
            <Tooltip>
              <TooltipTrigger asChild>
                <span className="inline-flex items-center gap-0.5 rounded-sm bg-indigo-500/15 px-1 py-0.5 text-[10px] font-medium text-indigo-400">
                  <Copy className="h-2.5 w-2.5" />
                  de-dup
                </span>
              </TooltipTrigger>
              <TooltipContent>Grouped by theme to reduce redundancy</TooltipContent>
            </Tooltip>
          )}
          {memory.status !== "active" && (
            <Badge variant="warning" className="text-[10px]">
              {memory.status}
            </Badge>
          )}
        </div>
        <div className="text-right">
          <p className={`font-mono text-xs font-semibold ${weightColor}`}>
            w={formatWeight(memory.current_weight)}
          </p>
          <p className="text-[10px] text-muted-foreground">
            {formatDateRelative(memory.updated_at)}
          </p>
        </div>
      </div>
    </div>
  );
}
