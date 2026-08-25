from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth import get_principal, require_roles
from ...config import get_settings
from ...core.archaeology import ProcessArchaeology
from ...core.compilers import COMPILERS
from ...core.diff import diff_uam
from ...core.digital_twin import DigitalTwinSimulator
from ...core.policy import PolicyEngine
from ...core.uam import UAMProcess
from ...db import get_db
from ...schemas import ArchaeologyRequest, CompileRequest, PolicyEvaluationRequest, SimulationRequest, UAMDiffRequest
from ...services.repository import Repository

router = APIRouter(prefix="/processes", tags=["processes"])


@router.get("/{process_id}")
async def get_process(process_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_principal)):
    repo = Repository(db)
    process = await repo.get_process(process_id)
    if not process:
        raise HTTPException(404, "process not found")
    recommendation = await repo.latest_recommendation(process_id)
    return {
        "id": process.id,
        "automation_id": process.automation_id,
        "name": process.name,
        "version": process.version,
        "uam": process.uam,
        "recommendation": {
            "disposition": recommendation.disposition,
            "confidence": recommendation.confidence,
            "rationale": recommendation.rationale,
            "economics": recommendation.economics,
        } if recommendation else None,
    }


@router.post("/{process_id}/compile")
async def compile_process(
    process_id: str,
    request: CompileRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("admin", "architect", "developer")),
):
    process = await Repository(db).get_process(process_id)
    if not process:
        raise HTTPException(404, "process not found")
    compiler = COMPILERS[request.target]
    artifact = compiler.compile(UAMProcess.model_validate(process.uam))
    return {
        "target": artifact.target,
        "filename": artifact.filename,
        "media_type": artifact.media_type,
        "content": artifact.content,
        "warnings": artifact.warnings,
    }


@router.post("/{process_id}/simulate")
async def simulate(
    process_id: str,
    request: SimulationRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_principal),
):
    process = await Repository(db).get_process(process_id)
    if not process:
        raise HTTPException(404, "process not found")
    return DigitalTwinSimulator().simulate(
        UAMProcess.model_validate(process.uam),
        runs=request.runs,
        failure_overrides=request.failure_overrides,
        latency_multipliers=request.latency_multipliers,
    )


@router.post("/{process_id}/policy/evaluate")
async def policy_evaluate(
    process_id: str,
    request: PolicyEvaluationRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_principal),
):
    process = await Repository(db).get_process(process_id)
    if not process:
        raise HTTPException(404, "process not found")
    engine = PolicyEngine(get_settings().opa_url)
    return await engine.evaluate(UAMProcess.model_validate(process.uam), request.action, request.context)


@router.post("/{process_id}/archaeology")
async def archaeology(
    process_id: str,
    request: ArchaeologyRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("admin", "architect", "developer", "auditor")),
):
    process = await Repository(db).get_process(process_id)
    if not process:
        raise HTTPException(404, "process not found")
    return ProcessArchaeology().analyze(
        UAMProcess.model_validate(process.uam),
        [d.model_dump() for d in request.documents],
    )


@router.post("/{process_id}/diff")
async def uam_diff(
    process_id: str,
    request: UAMDiffRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_principal),
):
    process = await Repository(db).get_process(process_id)
    if not process:
        raise HTTPException(404, "process not found")
    return diff_uam(UAMProcess.model_validate(process.uam), request.other)


@router.get("/{process_id}/graph")
async def process_graph(process_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_principal)):
    process = await Repository(db).get_process(process_id)
    if not process:
        raise HTTPException(404, "process not found")
    uam = UAMProcess.model_validate(process.uam)
    nodes = [
        {"id": n.id, "type": "activity", "label": n.name, "kind": n.kind.value, "application": n.application}
        for n in uam.nodes
    ]
    app_nodes = [{"id": f"app:{a}", "type": "application", "label": a} for a in uam.applications]
    app_edges = [
        {"source": n.id, "target": f"app:{n.application}", "type": "uses"}
        for n in uam.nodes if n.application
    ]
    return {
        "nodes": nodes + app_nodes,
        "edges": [e.model_dump(mode="json") for e in uam.edges] + app_edges,
    }
