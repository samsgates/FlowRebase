from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import api_router
from .config import get_settings
from .db import init_db
from .middleware import RequestContextMiddleware
from .telemetry import configure_telemetry


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_telemetry()
    await init_db()
    yield


settings = get_settings()
app = FastAPI(
    title="FlowRebase Control Plane",
    description="Vendor-neutral automation modernization, UAM, ProofRun and digital-twin APIs.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": "FlowRebase",
        "tagline": "Understand every automation. Recompile it anywhere. Prove it before cutover.",
        "docs": "/docs",
    }
