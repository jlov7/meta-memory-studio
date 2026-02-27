// TypeScript interfaces matching all backend response schemas

export interface HealthResponse {
  status: string;
  version: string;
}

export interface Workspace {
  id: string;
  name: string;
  run_count: number;
  memory_count: number;
}

export interface WorkspaceList {
  workspaces: Workspace[];
}

export interface ImportResult {
  success: boolean;
  raw_file_id: string | null;
  event_count: number;
  run_count: number;
  memory_count: number;
  pii_level: string;
  hash_valid: boolean;
  errors: string[];
}

export interface IntegrityResult {
  raw_file_id: string;
  filename: string;
  valid: boolean;
  event_count: number;
}

export interface IntegrityResponse {
  workspace_id: string;
  results: IntegrityResult[];
  all_valid: boolean;
}

export interface RunSummary {
  id: string;
  external_id: string;
  outcome: string;
  score: number | null;
  started_at: string | null;
  ended_at: string | null;
  episode_count: number;
  step_count: number;
}

export interface RunList {
  runs: RunSummary[];
  total: number;
}

export interface TimelineStep {
  id: string;
  sequence: number;
  event_type: string;
  timestamp: string | null;
  actor: string;
  content: string; // JSON string
  raw_event_id: string | null;
}

export interface RunDetail extends RunSummary {
  timeline: TimelineStep[];
  hash_valid: boolean;
}

export interface MemoryOut {
  id: string;
  title: string;
  content: string;
  memory_type: string;
  status: string;
  current_weight: number;
  created_at: string;
  updated_at: string;
}

export interface MemoryList {
  memories: MemoryOut[];
  total: number;
}

export interface WeightUpdateOut {
  id: string;
  old_weight: number;
  new_weight: number;
  delta: number;
  reason: string;
  updated_at: string;
}

export interface ContributionOut {
  id: string;
  memory_item_id: string;
  baseline_run_id: string;
  guided_run_id: string;
  baseline_score: number;
  guided_score: number;
  delta: number;
  measured_at: string;
}

export interface MemoryDetail {
  memory: MemoryOut;
  weight_history: WeightUpdateOut[];
  contributions: ContributionOut[];
  retrieval_count: number;
}

export interface EvolveResult {
  contributions_created: number;
  weight_updates: number;
}

export interface ToolAnomalyOut {
  tool_name: string;
  expected_freq: number;
  actual_freq: number;
  anomaly_score: number;
  runs_affected: string[];
}

export interface DriftReportOut {
  workspace_id: string;
  total_runs: number;
  anomalies: ToolAnomalyOut[];
}

export interface ThemeGroup {
  theme_id: string;
  theme_title: string;
  memories: MemoryOut[];
}

export interface ThemeGroupList {
  groups: ThemeGroup[];
  total_memories: number;
}
