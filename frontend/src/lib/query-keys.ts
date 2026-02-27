export const queryKeys = {
  health: ["health"] as const,

  workspaces: {
    all: ["workspaces"] as const,
  },

  runs: {
    list: (workspaceId: string) => ["runs", workspaceId] as const,
    detail: (workspaceId: string, runId: string) =>
      ["runs", workspaceId, runId] as const,
  },

  memory: {
    list: (workspaceId: string, params?: object) =>
      ["memory", workspaceId, params] as const,
    detail: (workspaceId: string, memoryId: string) =>
      ["memory", workspaceId, memoryId] as const,
  },

  integrity: {
    workspace: (workspaceId: string) => ["integrity", workspaceId] as const,
  },

  drift: {
    workspace: (workspaceId: string) => ["drift", workspaceId] as const,
  },

  themes: {
    workspace: (workspaceId: string) => ["themes", workspaceId] as const,
  },
};
