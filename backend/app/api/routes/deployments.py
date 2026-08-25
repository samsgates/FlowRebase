from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ... import models
from ...auth import require_roles
from ...db import get_db
from ...services.repository import Repository

router = APIRouter(prefix="/deployments", tags=["deployments"])


class DeploymentRequest(BaseModel):
    process_id: str
    target: str
    stage: str = "shadow"
    traffic_percent: float = Field(default=0, ge=0, le=100)
    proofrun_id: str


@router.post("")
async def create_deployment(
    request: DeploymentRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("admin", "architect")),
):
    repo = Repository(db)
    proof = await repo.get_proofrun(request.proofrun_id)
    if not proof or proof.process_id != request.process_id:
        raise HTTPException(409, "matching ProofRun is required")
    if proof.status != "passed" or proof.critical_failure:
        raise HTTPException(409, "deployment blocked: ProofRun has not passed")
    record = await repo.create_deployment(
        process_id=request.process_id,
        target=request.target,
        stage=request.stage,
        traffic_percent=request.traffic_percent,
        status="approved",
        metadata={"proofrun_id": proof.id},
    )
    return {"id": record.id, "status": record.status, "stage": record.stage, "traffic_percent": record.traffic_percent}


@router.get("")
async def list_deployments(db: AsyncSession = Depends(get_db), _=Depends(require_roles("admin", "architect", "developer", "auditor"))):
    items = list((await db.execute(select(models.Deployment).order_by(models.Deployment.created_at.desc()))).scalars().all())
    return [
        {
            "id": x.id,
            "process_id": x.process_id,
            "target": x.target,
            "stage": x.stage,
            "traffic_percent": x.traffic_percent,
            "status": x.status,
        }
        for x in items
    ]
