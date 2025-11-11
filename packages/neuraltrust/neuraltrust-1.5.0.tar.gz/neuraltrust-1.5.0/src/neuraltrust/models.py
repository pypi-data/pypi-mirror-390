from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class Event(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    timestamp: float
    attributes: Dict[str, str] = Field(default_factory=dict)


class Span(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    span_id: str = Field(..., serialization_alias="id")
    parent_id: Optional[str] = None
    name: str
    kind: str = "internal"
    status: str = "ok"
    started_at: float
    ended_at: float
    attributes: Dict[str, str] = Field(default_factory=dict)
    events: List[Event] = Field(default_factory=list)


class Resource(BaseModel):
    model_config = ConfigDict(extra="ignore")

    sdk_name: str
    sdk_version: str
    language: str = "python"
    runtime: Optional[str] = None
    library_name: Optional[str] = None
    library_version: Optional[str] = None


class Trace(BaseModel):
    model_config = ConfigDict(extra="ignore")

    trace_id: str
    workflow_name: str
    group_id: Optional[str] = None
    started_at: float
    ended_at: Optional[float] = None
    attributes: Dict[str, str] = Field(default_factory=dict)
    spans: List[Span] = Field(default_factory=list)


class TraceEnvelope(BaseModel):
    model_config = ConfigDict(extra="ignore")

    resource: Resource
    traces: List[Trace]
