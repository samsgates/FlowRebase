from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth import require_roles
from ...db import get_db
from ...services.demo_seed import seed_demo

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/seed")
async def seed(db: AsyncSession = Depends(get_db), _=Depends(require_roles("admin", "developer"))):
    return await seed_demo(db)
