from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models
from ..core.uam import UAMProcess


class Repository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def default_workspace(self) -> models.Workspace:
        ws = (await self.db.execute(select(models.Workspace).limit(1))).scalar_one_or_none()
        if not ws:
            ws = models.Workspace(name="Default Workspace")
            self.db.add(ws)
            await self.db.commit()
            await self.db.refresh(ws)
        return ws

    async def create_automation(self, *, workspace_id: str, name: str, source_type: str, content: str, metadata: dict, health_score: float, risk_score: float) -> models.Automation:
        item = models.Automation(
            workspace_id=workspace_id,
            name=name,
            source_type=source_type,
            source_content=content,
            source_metadata=metadata,
            health_score=health_score,
            risk_score=risk_score,
            status="analyzed",
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def list_automations(self, workspace_id: str | None = None) -> list[models.Automation]:
        stmt = select(models.Automation).order_by(models.Automation.created_at.desc())
        if workspace_id:
            stmt = stmt.where(models.Automation.workspace_id == workspace_id)
        return list((await self.db.execute(stmt)).scalars().all())

    async def get_automation(self, automation_id: str) -> models.Automation | None:
        return await self.db.get(models.Automation, automation_id)

    async def create_process(self, *, workspace_id: str, automation_id: str | None, uam: UAMProcess) -> models.Process:
        item = models.Process(
            workspace_id=workspace_id,
            automation_id=automation_id,
            name=uam.name,
            version=uam.version,
            uam=uam.model_dump(mode="json"),
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def get_process(self, process_id: str) -> models.Process | None:
        return await self.db.get(models.Process, process_id)

    async def get_process_by_automation(self, automation_id: str) -> models.Process | None:
        stmt = select(models.Process).where(models.Process.automation_id == automation_id).order_by(models.Process.created_at.desc()).limit(1)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def create_recommendation(self, *, process_id: str, advice) -> models.Recommendation:
        item = models.Recommendation(
            process_id=process_id,
            disposition=advice.disposition.value,
            confidence=advice.confidence,
            rationale=advice.rationale,
            evidence=advice.evidence,
            alternatives=advice.alternatives,
            economics=advice.economics,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def latest_recommendation(self, process_id: str) -> models.Recommendation | None:
        stmt = select(models.Recommendation).where(models.Recommendation.process_id == process_id).order_by(models.Recommendation.created_at.desc()).limit(1)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def create_proofrun(self, *, process_id: str, report: dict) -> models.ProofRun:
        item = models.ProofRun(
            process_id=process_id,
            status=report["status"],
            score=report["score"],
            critical_failure=report["critical_failure"],
            report=report,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def get_proofrun(self, proofrun_id: str) -> models.ProofRun | None:
        return await self.db.get(models.ProofRun, proofrun_id)

    async def create_deployment(self, *, process_id: str, target: str, stage: str, traffic_percent: float, status: str, metadata: dict) -> models.Deployment:
        item = models.Deployment(
            process_id=process_id,
            target=target,
            stage=stage,
            traffic_percent=traffic_percent,
            status=status,
            metadata_json=metadata,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def portfolio_summary(self) -> dict:
        total = int((await self.db.execute(select(func.count(models.Automation.id)))).scalar_one())
        processes = int((await self.db.execute(select(func.count(models.Process.id)))).scalar_one())
        proofruns = int((await self.db.execute(select(func.count(models.ProofRun.id)))).scalar_one())
        risky = int((await self.db.execute(select(func.count(models.Automation.id)).where(models.Automation.risk_score >= 70))).scalar_one())
        avg_health = float((await self.db.execute(select(func.avg(models.Automation.health_score)))).scalar_one() or 0)
        recommendations = list((await self.db.execute(select(models.Recommendation))).scalars().all())
        dispositions: dict[str, int] = {}
        savings = 0.0
        for rec in recommendations:
            dispositions[rec.disposition] = dispositions.get(rec.disposition, 0) + 1
            savings += float((rec.economics or {}).get("estimated_annual_savings", 0))
        return {
            "automations": total,
            "processes": processes,
            "proofruns": proofruns,
            "high_risk": risky,
            "average_health": round(avg_health, 1),
            "estimated_annual_savings": round(savings, 2),
            "dispositions": dispositions,
        }
