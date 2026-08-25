from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth import get_principal, require_roles
from ...core.proofrun import ProofRunEngine
from ...core.uam import UAMProcess
from ...db import get_db
from ...schemas import ProofRunRequest
from ...services.repository import Repository

router = APIRouter(prefix="/proofruns", tags=["proofrun"])


@router.post("/process/{process_id}")
async def run_proof(
    process_id: str,
    request: ProofRunRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("admin", "architect", "developer", "auditor")),
):
    repo = Repository(db)
    process = await repo.get_process(process_id)
    if not process:
        raise HTTPException(404, "process not found")
    report = ProofRunEngine().run(UAMProcess.model_validate(process.uam), [c.model_dump() for c in request.cases])
    record = await repo.create_proofrun(process_id=process_id, report=report)
    return {"id": record.id, **report}


@router.get("/{proofrun_id}")
async def get_proofrun(proofrun_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_principal)):
    record = await Repository(db).get_proofrun(proofrun_id)
    if not record:
        raise HTTPException(404, "ProofRun not found")
    return {"id": record.id, "process_id": record.process_id, **record.report}
