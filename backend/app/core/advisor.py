from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .uam import Determinism, NodeKind, UAMProcess


class Disposition(StrEnum):
    KEEP = "KEEP"
    UPGRADE = "UPGRADE"
    REFACTOR = "REFACTOR"
    API_FY = "API-FY"
    WORKFLOW = "WORKFLOW"
    MIGRATE = "MIGRATE"
    AGENTIFY = "AGENTIFY"
    HYBRIDIZE = "HYBRIDIZE"
    MERGE = "MERGE"
    RETIRE = "RETIRE"


@dataclass
class Advice:
    disposition: Disposition
    confidence: float
    rationale: list[str]
    evidence: list[dict]
    alternatives: list[dict]
    economics: dict


class ModernizationAdvisor:
    """Deterministic baseline advisor.

    The production product can augment this result with an LLM, but the baseline always remains
    explainable and available in air-gapped installations.
    """

    def recommend(self, process: UAMProcess, automation_metrics: dict | None = None) -> Advice:
        metrics = automation_metrics or {}
        nodes = process.nodes
        ui_nodes = [n for n in nodes if n.kind == NodeKind.UI_ACTION]
        api_nodes = [n for n in nodes if n.kind == NodeKind.API_CALL]
        human_nodes = [n for n in nodes if n.determinism == Determinism.HUMAN_ACCOUNTABLE]
        agent_nodes = [n for n in nodes if n.kind == NodeKind.AGENT or n.determinism == Determinism.PROBABILISTIC]
        legacy_apps = [a for a in process.applications if a.lower() in {"sap", "microsoft excel", "citrix"}]
        failure_rate = float(metrics.get("failure_rate", 0.05))
        annual_cost = float(metrics.get("annual_cost", process.economics.get("annual_cost", 50_000)))
        last_run_days = int(metrics.get("last_run_days", 0))
        executions_year = int(metrics.get("executions_year", 1000))

        rationale: list[str] = []
        evidence: list[dict] = []
        alternatives: list[dict] = []

        if last_run_days > 365 and executions_year == 0:
            disposition = Disposition.RETIRE
            confidence = 0.94
            rationale.append("No observed execution in the last year and no forecast execution volume.")
        elif ui_nodes and len(ui_nodes) >= max(2, len(nodes) // 3):
            if api_nodes:
                disposition = Disposition.HYBRIDIZE
                confidence = 0.88
                rationale.append("The process mixes fragile UI automation with API-capable steps.")
            else:
                disposition = Disposition.API_FY
                confidence = 0.84
                rationale.append("A large portion of the process is UI automation and is a strong API replacement candidate.")
        elif agent_nodes and human_nodes:
            disposition = Disposition.HYBRIDIZE
            confidence = 0.91
            rationale.append("The process already combines probabilistic reasoning with accountable human decisions.")
        elif agent_nodes:
            disposition = Disposition.AGENTIFY
            confidence = 0.82
            rationale.append("The process contains reasoning-oriented or probabilistic tasks suitable for governed agents.")
        elif failure_rate > 0.15 or legacy_apps:
            disposition = Disposition.REFACTOR
            confidence = 0.86
            rationale.append("Runtime fragility or legacy application coupling makes direct migration risky.")
        elif len(human_nodes) > 2:
            disposition = Disposition.WORKFLOW
            confidence = 0.83
            rationale.append("Human task density indicates a workflow/case-management architecture may be a better fit than RPA.")
        else:
            disposition = Disposition.KEEP
            confidence = 0.78
            rationale.append("No strong signal currently justifies disruptive migration. Improve observability and reassess periodically.")

        if ui_nodes:
            evidence.append({"type": "structure", "fact": f"{len(ui_nodes)} UI interaction nodes detected"})
        if human_nodes:
            evidence.append({"type": "structure", "fact": f"{len(human_nodes)} human-accountable nodes detected"})
        if process.applications:
            evidence.append({"type": "dependency", "fact": f"Applications: {', '.join(process.applications)}"})
        evidence.append({"type": "runtime", "fact": f"Observed/assumed failure rate: {failure_rate:.1%}"})

        alternatives.extend(
            [
                {"architecture": "retain_and_harden", "risk": "low", "relative_cost": 1.0},
                {"architecture": "api_workflow", "risk": "medium", "relative_cost": 0.72},
                {"architecture": "hybrid_agentic", "risk": "medium-high", "relative_cost": 0.78},
            ]
        )

        savings_factor = {
            Disposition.KEEP: 0.05,
            Disposition.UPGRADE: 0.12,
            Disposition.REFACTOR: 0.22,
            Disposition.API_FY: 0.35,
            Disposition.WORKFLOW: 0.25,
            Disposition.MIGRATE: 0.18,
            Disposition.AGENTIFY: 0.20,
            Disposition.HYBRIDIZE: 0.28,
            Disposition.MERGE: 0.40,
            Disposition.RETIRE: 0.95,
        }[disposition]
        economics = {
            "current_annual_cost": round(annual_cost, 2),
            "estimated_annual_savings": round(annual_cost * savings_factor, 2),
            "estimated_target_annual_cost": round(annual_cost * (1 - savings_factor), 2),
            "method": "deterministic-baseline-v1",
        }

        return Advice(disposition, confidence, rationale, evidence, alternatives, economics)
