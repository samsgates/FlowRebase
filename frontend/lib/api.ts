import type { Automation, AutomationDetail, PortfolioSummary, ProcessDetail } from "./types";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function get<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API}/api/v1${path}`, { cache: "no-store" });
    if (!response.ok) return fallback;
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export const api = {
  portfolio: () => get<PortfolioSummary>("/portfolio/summary", {
    automations: 0,
    processes: 0,
    proofruns: 0,
    high_risk: 0,
    average_health: 0,
    estimated_annual_savings: 0,
    dispositions: {},
  }),
  automations: () => get<Automation[]>("/automations", []),
  automation: (id: string) => get<AutomationDetail | null>(`/automations/${id}`, null),
  process: (id: string) => get<ProcessDetail | null>(`/processes/${id}`, null),
};
