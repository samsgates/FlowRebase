export type NodeKind =
  | "start" | "end" | "task" | "decision" | "loop" | "parallel" | "wait" | "timer"
  | "event" | "api_call" | "ui_action" | "robot_action" | "script" | "database_action"
  | "queue_action" | "document_action" | "agent_action" | "human_task" | "approval"
  | "policy_check" | "subprocess" | "compensation" | "rollback" | "exception" | "notification";

export type Determinism = "deterministic" | "probabilistic" | "human_accountable";
export type Criticality = "low" | "medium" | "high" | "mission_critical";

export interface Evidence {
  id: string;
  source_type: string;
  source_ref: string;
  excerpt?: string | null;
  confidence: number;
}

export interface UAMEdge {
  source: string;
  target: string;
  label?: string | null;
  condition?: string | null;
}

export interface UAMNode {
  id: string;
  kind: NodeKind;
  name: string;
  description?: string | null;
  determinism: Determinism;
  config: Record<string, unknown>;
  application?: string | null;
  policy_refs: string[];
  evidence_refs: string[];
  criticality: Criticality;
  estimated_cost: number;
}

export interface UAMIntent {
  objective: string;
  business_outcomes: Record<string, unknown>;
  owner?: string | null;
  criticality: Criticality;
}

export interface UAMPolicy {
  id: string;
  name: string;
  effect: "allow" | "deny" | "require_approval";
  action: string;
  when: Record<string, unknown>;
  reason?: string | null;
}

export interface UAMProcess {
  schema_version: string;
  id: string;
  name: string;
  version: string;
  source: Record<string, unknown>;
  intent: UAMIntent;
  nodes: UAMNode[];
  edges: UAMEdge[];
  variables: Record<string, unknown>;
  applications: string[];
  credentials: Array<Record<string, unknown>>;
  policies: UAMPolicy[];
  evidence: Evidence[];
  telemetry: Record<string, unknown>;
  economics: Record<string, unknown>;
  extensions: Record<string, unknown>;
}
