from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ... import models
from ...auth import require_roles
from ...db import get_db

router = APIRouter(prefix="/governance", tags=["governance"])


@router.get("/audit")
async def audit_events(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("admin", "auditor")),
):
    limit = min(max(limit, 1), 1000)
    rows = list((await db.execute(select(models.AuditEvent).order_by(models.AuditEvent.created_at.desc()).limit(limit))).scalars().all())
    return [
        {
            "id": row.id,
            "actor": row.actor,
            "action": row.action,
            "resource": row.resource,
            "request_id": row.request_id,
            "status_code": row.status_code,
            "created_at": row.created_at,
        }
        for row in rows
    ]
