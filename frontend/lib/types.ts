import type { UAMProcess } from "@flowrebase/uam";

export type PortfolioSummary = {
  automations: number;
  processes: number;
  proofruns: number;
  high_risk: number;
  average_health: number;
  estimated_annual_savings: number;
  dispositions: Record<string, number>;
};

export type Automation = {
  id: string;
  name: string;
  source_type: string;
  health_score: number;
  risk_score: number;
  status: string;
  process_id?: string | null;
  metadata?: Record<string, unknown>;
};

export type AutomationDetail = Automation & {
  process?: { id: string; uam: UAMProcess } | null;
  recommendation?: Recommendation | null;
};

export type Recommendation = {
  id?: string;
  disposition: string;
  confidence: number;
  rationale: string[];
  evidence?: Array<Record<string, unknown>>;
  alternatives?: Array<Record<string, unknown>>;
  economics?: Record<string, number | string>;
};

export type ProcessDetail = {
  id: string;
  automation_id?: string | null;
  name: string;
  version: string;
  uam: UAMProcess;
  recommendation?: Recommendation | null;
};
