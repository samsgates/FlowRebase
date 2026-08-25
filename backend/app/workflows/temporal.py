from __future__ import annotations

from datetime import timedelta

from temporalio import workflow


@workflow.defn
class ModernizationWorkflow:
    """Durable orchestration contract for production-scale modernization jobs.

    Activities are deliberately referenced by string so operators can split parsers, AI workers,
    compilers and ProofRun workers into separately scaled worker pools.
    """

    @workflow.run
    async def run(self, automation_id: str, target: str) -> dict:
        analyzed = await workflow.execute_activity(
            "analyze_automation",
            automation_id,
            start_to_close_timeout=timedelta(minutes=20),
            retry_policy=None,
        )
        compiled = await workflow.execute_activity(
            "compile_process",
            {"process_id": analyzed["process_id"], "target": target},
            start_to_close_timeout=timedelta(minutes=30),
        )
        proof = await workflow.execute_activity(
            "proofrun_process",
            {"process_id": analyzed["process_id"], "artifact": compiled},
            start_to_close_timeout=timedelta(hours=2),
        )
        return {"analysis": analyzed, "compile": compiled, "proofrun": proof}
