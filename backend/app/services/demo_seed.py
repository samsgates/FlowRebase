from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models
from ..core.advisor import ModernizationAdvisor
from ..core.demo import demo_uam
from .repository import Repository
from .scoring import score_process



async def seed_demo(db: AsyncSession) -> dict:
    repo = Repository(db)
    existing = (await db.execute(select(models.Automation).where(models.Automation.name == "Vendor Invoice Processing"))).scalar_one_or_none()
    if existing:
        process = await repo.get_process_by_automation(existing.id)
        return {"created": False, "automation_id": existing.id, "process_id": process.id if process else None}
    ws = await repo.default_workspace()
    uam = demo_uam()
    health, risk = score_process(uam, {"failure_rate": 0.12})
    automation = await repo.create_automation(
        workspace_id=ws.id,
        name=uam.name,
        source_type="uipath",
        content="<!-- demo source represented by pre-built UAM -->",
        metadata={"failure_rate": 0.12, "annual_cost": 180000, "executions_year": 18000},
        health_score=health,
        risk_score=risk,
    )
    process = await repo.create_process(workspace_id=ws.id, automation_id=automation.id, uam=uam)
    advice = ModernizationAdvisor().recommend(uam, automation.source_metadata)
    await repo.create_recommendation(process_id=process.id, advice=advice)
    return {"created": True, "automation_id": automation.id, "process_id": process.id}
