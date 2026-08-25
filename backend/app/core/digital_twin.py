from __future__ import annotations

import random
from statistics import mean

from .uam import UAMProcess


class DigitalTwinSimulator:
    def simulate(
        self,
        process: UAMProcess,
        runs: int = 1000,
        failure_overrides: dict[str, float] | None = None,
        latency_multipliers: dict[str, float] | None = None,
        seed: int = 42,
    ) -> dict:
        rng = random.Random(seed)
        failure_overrides = failure_overrides or {}
        latency_multipliers = latency_multipliers or {}
        run_latencies: list[float] = []
        failures = 0
        costs: list[float] = []
        node_stats = {n.id: {"failures": 0, "runs": 0} for n in process.nodes}

        for _ in range(runs):
            total_latency = 0.0
            total_cost = 0.0
            failed = False
            for node in process.nodes:
                node_stats[node.id]["runs"] += 1
                base_failure = float(node.config.get("sim_failure_rate", 0.005))
                failure_rate = failure_overrides.get(node.id, base_failure)
                base_latency = float(node.config.get("sim_latency_ms", 100))
                latency = base_latency * latency_multipliers.get(node.id, 1.0)
                total_latency += latency
                total_cost += float(node.estimated_cost or node.config.get("sim_cost", 0))
                if rng.random() < failure_rate:
                    node_stats[node.id]["failures"] += 1
                    failed = True
                    break
            failures += int(failed)
            run_latencies.append(total_latency)
            costs.append(total_cost)

        risky = sorted(
            (
                {
                    "node_id": node_id,
                    "failure_rate": stat["failures"] / max(1, stat["runs"]),
                }
                for node_id, stat in node_stats.items()
            ),
            key=lambda x: x["failure_rate"],
            reverse=True,
        )[:5]
        return {
            "runs": runs,
            "predicted_success_rate": round(1 - failures / max(1, runs), 5),
            "predicted_failure_rate": round(failures / max(1, runs), 5),
            "average_latency_ms": round(mean(run_latencies), 2),
            "average_cost": round(mean(costs), 6),
            "highest_risk_nodes": risky,
            "simulation_seed": seed,
        }
