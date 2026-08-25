from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth import get_principal
from ...db import get_db
from ...services.repository import Repository

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/summary")
async def summary(db: AsyncSession = Depends(get_db), _=Depends(get_principal)):
    return await Repository(db).portfolio_summary()
