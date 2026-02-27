"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, Layers } from "lucide-react";
import { type ThemeGroup } from "@/types/api";
import { MemoryCard } from "@/components/memory/memory-card";
import { Badge } from "@/components/ui/badge";

interface ThemedMemoryLibraryProps {
  workspaceId: string;
  groups: ThemeGroup[];
}

interface ThemeSectionProps {
  workspaceId: string;
  group: ThemeGroup;
}

function ThemeSection({ workspaceId, group }: ThemeSectionProps) {
  const [open, setOpen] = useState(true);

  return (
    <div className="rounded-lg border border-border bg-surface overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-2 px-4 py-3 text-left hover:bg-white/5 transition-colors"
      >
        {open ? (
          <ChevronDown className="h-4 w-4 text-muted shrink-0" />
        ) : (
          <ChevronRight className="h-4 w-4 text-muted shrink-0" />
        )}
        <Layers className="h-4 w-4 text-indigo-400 shrink-0" />
        <span className="flex-1 text-sm font-medium text-foreground">
          {group.theme_title}
        </span>
        <Badge variant="muted" className="text-xs">
          {group.memories.length}
        </Badge>
      </button>

      {open && (
        <div className="border-t border-border px-4 py-4">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {group.memories.map((memory) => (
              <MemoryCard
                key={memory.id}
                workspaceId={workspaceId}
                memory={memory}
                deduped={group.memories.length > 1}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function ThemedMemoryLibrary({ workspaceId, groups }: ThemedMemoryLibraryProps) {
  if (groups.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-col gap-3">
      {groups.map((group) => (
        <ThemeSection key={group.theme_id} workspaceId={workspaceId} group={group} />
      ))}
    </div>
  );
}
