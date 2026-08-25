import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def uid() -> str:
    return str(uuid.uuid4())


def now() -> datetime:
    return datetime.now(timezone.utc)


class Workspace(Base):
    __tablename__ = "workspaces"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(200), default="Default Workspace")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Automation(Base):
    __tablename__ = "automations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    workspace_id: Mapped[str] = mapped_column(String(36), ForeignKey("workspaces.id"), index=True)
    name: Mapped[str] = mapped_column(String(240), index=True)
    source_type: Mapped[str] = mapped_column(String(50), index=True)
    source_content: Mapped[str] = mapped_column(Text)
    source_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    health_score: Mapped[float] = mapped_column(Float, default=0)
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(50), default="discovered")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class Process(Base):
    __tablename__ = "processes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    workspace_id: Mapped[str] = mapped_column(String(36), ForeignKey("workspaces.id"), index=True)
    automation_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("automations.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(240), index=True)
    uam: Mapped[dict] = mapped_column(JSON)
    version: Mapped[str] = mapped_column(String(40), default="1.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class Recommendation(Base):
    __tablename__ = "recommendations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    process_id: Mapped[str] = mapped_column(String(36), ForeignKey("processes.id"), index=True)
    disposition: Mapped[str] = mapped_column(String(50), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    rationale: Mapped[list] = mapped_column(JSON, default=list)
    evidence: Mapped[list] = mapped_column(JSON, default=list)
    alternatives: Mapped[list] = mapped_column(JSON, default=list)
    economics: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class ProofRun(Base):
    __tablename__ = "proofruns"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    process_id: Mapped[str] = mapped_column(String(36), ForeignKey("processes.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    score: Mapped[float] = mapped_column(Float, default=0)
    critical_failure: Mapped[bool] = mapped_column(default=False)
    report: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Deployment(Base):
    __tablename__ = "deployments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    process_id: Mapped[str] = mapped_column(String(36), ForeignKey("processes.id"), index=True)
    target: Mapped[str] = mapped_column(String(80))
    stage: Mapped[str] = mapped_column(String(40), default="dev")
    traffic_percent: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(50), default="planned")
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    actor: Mapped[str] = mapped_column(String(240), default="unknown", index=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    resource: Mapped[str] = mapped_column(String(500), index=True)
    request_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    status_code: Mapped[int] = mapped_column(default=0)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
