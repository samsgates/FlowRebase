from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class NodeKind(StrEnum):
    START = "start"
    END = "end"
    TASK = "task"
    DECISION = "decision"
    LOOP = "loop"
    PARALLEL = "parallel"
    WAIT = "wait"
    TIMER = "timer"
    EVENT = "event"
    API_CALL = "api_call"
    UI_ACTION = "ui_action"
    ROBOT_ACTION = "robot_action"
    SCRIPT = "script"
    DATABASE = "database_action"
    QUEUE = "queue_action"
    DOCUMENT = "document_action"
    AGENT = "agent_action"
    HUMAN = "human_task"
    APPROVAL = "approval"
    POLICY = "policy_check"
    SUBPROCESS = "subprocess"
    COMPENSATION = "compensation"
    ROLLBACK = "rollback"
    EXCEPTION = "exception"
    NOTIFICATION = "notification"


class Determinism(StrEnum):
    DETERMINISTIC = "deterministic"
    PROBABILISTIC = "probabilistic"
    HUMAN_ACCOUNTABLE = "human_accountable"


class Evidence(BaseModel):
    id: str
    source_type: str
    source_ref: str
    excerpt: str | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)


class UAMEdge(BaseModel):
    source: str
    target: str
    label: str | None = None
    condition: str | None = None


class UAMNode(BaseModel):
    id: str
    kind: NodeKind
    name: str
    description: str | None = None
    determinism: Determinism = Determinism.DETERMINISTIC
    config: dict[str, Any] = Field(default_factory=dict)
    application: str | None = None
    policy_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    criticality: Literal["low", "medium", "high", "mission_critical"] = "medium"
    estimated_cost: float = 0


class UAMIntent(BaseModel):
    objective: str
    business_outcomes: dict[str, Any] = Field(default_factory=dict)
    owner: str | None = None
    criticality: Literal["low", "medium", "high", "mission_critical"] = "medium"


class UAMPolicy(BaseModel):
    id: str
    name: str
    effect: Literal["allow", "deny", "require_approval"]
    action: str
    when: dict[str, Any] = Field(default_factory=dict)
    reason: str | None = None


class UAMProcess(BaseModel):
    schema_version: str = "1.0"
    id: str
    name: str
    version: str = "1.0.0"
    source: dict[str, Any] = Field(default_factory=dict)
    intent: UAMIntent
    nodes: list[UAMNode]
    edges: list[UAMEdge]
    variables: dict[str, Any] = Field(default_factory=dict)
    applications: list[str] = Field(default_factory=list)
    credentials: list[dict[str, Any]] = Field(default_factory=list)
    policies: list[UAMPolicy] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    telemetry: dict[str, Any] = Field(default_factory=dict)
    economics: dict[str, Any] = Field(default_factory=dict)
    extensions: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_graph(self):
        ids = {node.id for node in self.nodes}
        if len(ids) != len(self.nodes):
            raise ValueError("UAM node IDs must be unique")
        for edge in self.edges:
            if edge.source not in ids or edge.target not in ids:
                raise ValueError(f"edge references unknown node: {edge.source}->{edge.target}")
        return self

    def node(self, node_id: str) -> UAMNode:
        for node in self.nodes:
            if node.id == node_id:
                return node
        raise KeyError(node_id)

    def outgoing(self, node_id: str) -> list[UAMEdge]:
        return [edge for edge in self.edges if edge.source == node_id]
