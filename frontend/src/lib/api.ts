import type {
  DriftReportOut,
  EvolveResult,
  HealthResponse,
  ImportResult,
  IntegrityResponse,
  MemoryDetail,
  MemoryList,
  MemoryOut,
  RunDetail,
  RunList,
  ThemeGroupList,
  Workspace,
  WorkspaceList,
} from "@/types/api";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error");
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// Health
export const getHealth = () =>
  request<HealthResponse>("/api/health");

// Workspaces
export const listWorkspaces = () =>
  request<WorkspaceList>("/api/workspaces");

export const createWorkspace = (name: string) =>
  request<Workspace>("/api/workspaces", {
    method: "POST",
    body: JSON.stringify({ name }),
  });

// Ingest
export const importTrace = (workspaceId: string, file: File) => {
  const form = new FormData();
  form.append("file", file);
  return request<ImportResult>(`/api/workspaces/${workspaceId}/import`, {
    method: "POST",
    headers: {}, // let browser set multipart boundary
    body: form,
  });
};

// Integrity
export const checkIntegrity = (workspaceId: string) =>
  request<IntegrityResponse>(`/api/workspaces/${workspaceId}/integrity`);

// Runs
export const listRuns = (workspaceId: string) =>
  request<RunList>(`/api/workspaces/${workspaceId}/runs`);

export const getRun = (workspaceId: string, runId: string) =>
  request<RunDetail>(`/api/workspaces/${workspaceId}/runs/${runId}`);

// Memory
export const listMemories = (
  workspaceId: string,
  params?: { q?: string; status?: string; memory_type?: string }
) => {
  const qs = new URLSearchParams();
  if (params?.q) qs.set("q", params.q);
  if (params?.status) qs.set("status", params.status);
  if (params?.memory_type) qs.set("memory_type", params.memory_type);
  const query = qs.toString() ? `?${qs.toString()}` : "";
  return request<MemoryList>(`/api/workspaces/${workspaceId}/memory${query}`);
};

export const getMemory = (workspaceId: string, memoryId: string) =>
  request<MemoryDetail>(`/api/workspaces/${workspaceId}/memory/${memoryId}`);

export const deprecateMemory = (workspaceId: string, memoryId: string) =>
  request<MemoryOut>(`/api/workspaces/${workspaceId}/memory/${memoryId}/deprecate`, {
    method: "PATCH",
  });

export const forgetMemory = (workspaceId: string, memoryId: string) =>
  request<{ deleted: boolean }>(`/api/workspaces/${workspaceId}/memory/${memoryId}`, {
    method: "DELETE",
  });

// Policy
export const evolveWorkspace = (workspaceId: string) =>
  request<EvolveResult>(`/api/workspaces/${workspaceId}/policy/evolve`, {
    method: "POST",
  });

// Themes (hierarchical retrieval)
export const listMemoryThemes = (workspaceId: string) =>
  request<ThemeGroupList>(`/api/workspaces/${workspaceId}/memory/themes`);

// Drift
export const getDrift = (workspaceId: string) =>
  request<DriftReportOut>(`/api/workspaces/${workspaceId}/drift`);
