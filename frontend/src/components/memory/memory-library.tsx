"use client";

import { type MemoryOut } from "@/types/api";
import { MemoryCard } from "@/components/memory/memory-card";

interface MemoryLibraryProps {
  workspaceId: string;
  memories: MemoryOut[];
}

export function MemoryLibrary({ workspaceId, memories }: MemoryLibraryProps) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {memories.map((memory) => (
        <MemoryCard key={memory.id} workspaceId={workspaceId} memory={memory} />
      ))}
    </div>
  );
}
