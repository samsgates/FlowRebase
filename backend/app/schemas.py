from typing import Any, Literal

from pydantic import BaseModel, Field

from .core.uam import UAMProcess


class AutomationImportRequest(BaseModel):
    name: str
    source_type: Literal["uipath", "bpmn", "python"]
    content: str
    workspace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AutomationResponse(BaseModel):
    id: str
    name: str
    source_type: str
    health_score: float
    risk_score: float
    status: str
    process_id: str | None = None


class ProcessResponse(BaseModel):
    id: str
    automation_id: str | None
    name: str
    version: str
    uam: UAMProcess


class CompileRequest(BaseModel):
    target: Literal["python", "bpmn", "power_automate"]


class CompileResponse(BaseModel):
    target: str
    filename: str
    media_type: str
    content: str
    warnings: list[str] = Field(default_factory=list)


class ProofCase(BaseModel):
    name: str
    input: dict[str, Any]
    expected: dict[str, Any]
    critical_paths: list[str] = Field(default_factory=list)


class ProofRunRequest(BaseModel):
    cases: list[ProofCase]


class SimulationRequest(BaseModel):
    runs: int = Field(default=1000, ge=1, le=100_000)
    failure_overrides: dict[str, float] = Field(default_factory=dict)
    latency_multipliers: dict[str, float] = Field(default_factory=dict)


class PolicyEvaluationRequest(BaseModel):
    action: str
    context: dict[str, Any] = Field(default_factory=dict)


class EvidenceDocument(BaseModel):
    name: str
    content: str
    source_type: str = "document"


class ArchaeologyRequest(BaseModel):
    documents: list[EvidenceDocument] = Field(default_factory=list)


class UAMDiffRequest(BaseModel):
    other: UAMProcess
