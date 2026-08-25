from fastapi import APIRouter

from .routes import automations, demo, deployments, governance, health, portfolio, processes, proofruns

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(demo.router)
api_router.include_router(portfolio.router)
api_router.include_router(automations.router)
api_router.include_router(processes.router)
api_router.include_router(proofruns.router)
api_router.include_router(deployments.router)
api_router.include_router(governance.router)
