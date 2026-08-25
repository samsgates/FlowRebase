from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth import get_principal, require_roles
from ...core.advisor import ModernizationAdvisor
from ...core.parsers import PARSERS
from ...core.uam import UAMProcess
from ...db import get_db
from ...schemas import AutomationImportRequest
from ...services.ai import AIService
from ...services.repository import Repository
from ...services.scoring import score_process

router = APIRouter(prefix="/automations", tags=["automations"])


@router.get("")
async def list_automations(db: AsyncSession = Depends(get_db), _=Depends(get_principal)):
    repo = Repository(db)
    items = await repo.list_automations()
    result = []
    for item in items:
        process = await repo.get_process_by_automation(item.id)
        result.append(
            {
                "id": item.id,
                "name": item.name,
                "source_type": item.source_type,
                "health_score": item.health_score,
                "risk_score": item.risk_score,
                "status": item.status,
                "process_id": process.id if process else None,
                "metadata": item.source_metadata,
            }
        )
    return result


@router.get("/{automation_id}")
async def get_automation(automation_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_principal)):
    repo = Repository(db)
    item = await repo.get_automation(automation_id)
    if not item:
        raise HTTPException(404, "automation not found")
    process = await repo.get_process_by_automation(item.id)
    recommendation = await repo.latest_recommendation(process.id) if process else None
    return {
        "id": item.id,
        "name": item.name,
        "source_type": item.source_type,
        "health_score": item.health_score,
        "risk_score": item.risk_score,
        "status": item.status,
        "metadata": item.source_metadata,
        "process": {"id": process.id, "uam": process.uam} if process else None,
        "recommendation": _rec(recommendation),
    }


@router.post("/import")
async def import_automation(
    request: AutomationImportRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("admin", "architect", "developer")),
):
    parser = PARSERS.get(request.source_type)
    if not parser:
        raise HTTPException(400, f"unsupported source_type: {request.source_type}")
    try:
        uam = parser.parse(name=request.name, content=request.content, metadata=request.metadata)
    except Exception as exc:
        raise HTTPException(422, f"source parse failed: {exc}") from exc
    repo = Repository(db)
    ws = await repo.default_workspace() if not request.workspace_id else None
    workspace_id = request.workspace_id or ws.id
    health, risk = score_process(uam, request.metadata)
    automation = await repo.create_automation(
        workspace_id=workspace_id,
        name=request.name,
        source_type=request.source_type,
        content=request.content,
        metadata=request.metadata,
        health_score=health,
        risk_score=risk,
    )
    process = await repo.create_process(workspace_id=workspace_id, automation_id=automation.id, uam=uam)
    return {
        "automation_id": automation.id,
        "process_id": process.id,
        "health_score": health,
        "risk_score": risk,
        "uam": uam.model_dump(mode="json"),
    }


@router.post("/{automation_id}/recommend")
async def recommend(automation_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_roles("admin", "architect", "developer"))):
    repo = Repository(db)
    automation = await repo.get_automation(automation_id)
    if not automation:
        raise HTTPException(404, "automation not found")
    process = await repo.get_process_by_automation(automation.id)
    if not process:
        raise HTTPException(409, "automation does not have UAM process")
    uam = UAMProcess.model_validate(process.uam)
    advice = ModernizationAdvisor().recommend(uam, automation.source_metadata)
    record = await repo.create_recommendation(process_id=process.id, advice=advice)
    return _rec(record)


@router.get("/{automation_id}/ai-explain")
async def ai_explain(automation_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_principal)):
    repo = Repository(db)
    process = await repo.get_process_by_automation(automation_id)
    if not process:
        raise HTTPException(404, "process not found")
    return await AIService().explain_process(UAMProcess.model_validate(process.uam))


def _rec(record):
    if not record:
        return None
    return {
        "id": record.id,
        "disposition": record.disposition,
        "confidence": record.confidence,
        "rationale": record.rationale,
        "evidence": record.evidence,
        "alternatives": record.alternatives,
        "economics": record.economics,
    }
