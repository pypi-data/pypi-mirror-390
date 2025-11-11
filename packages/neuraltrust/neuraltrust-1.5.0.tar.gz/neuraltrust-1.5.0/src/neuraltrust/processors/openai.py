from __future__ import annotations

import asyncio
import json
import logging
from contextlib import suppress
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agents.tracing import Span as AgentSpan
from agents.tracing import Trace as AgentTrace
from agents.tracing import add_trace_processor, set_trace_processors
from agents.tracing.processors import TracingProcessor
from agents.tracing.span_data import (
    AgentSpanData,
    CustomSpanData,
    FunctionSpanData,
    GenerationSpanData,
    GuardrailSpanData,
    HandoffSpanData,
    ResponseSpanData,
    SpanData,
)

from ..client import TelemetryClient
from ..config import TelemetryConfig
from ..models import Resource, Span, Trace, TraceEnvelope

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SDK_RESOURCE = Resource(
    sdk_name="neuraltrust",
    sdk_version="1.5.0",
    language="python",
    library_name="openai-agents",
)


def _safe_json(value: Any) -> str:
    try:
        return json.dumps(value, default=str)
    except TypeError:
        return str(value)


def _span_kind_from_data(span_data: SpanData) -> str:
    if isinstance(span_data, (GenerationSpanData, ResponseSpanData)):
        return "llm"
    if isinstance(span_data, (FunctionSpanData, GuardrailSpanData)):
        return "tool"
    if isinstance(span_data, (AgentSpanData, HandoffSpanData, CustomSpanData)):
        return "workflow"
    return "internal"


def _parse_usage(usage_data: Any) -> Dict[str, Optional[int]]:
    """Parse usage data into standardized dictionary."""
    parsed: Dict[str, Optional[int]] = {
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
    }
    if usage_data is None:
        return parsed

    usage_dict = {}
    if hasattr(usage_data, "model_dump"):
        try:
            usage_dict = usage_data.model_dump()
        except Exception:
            if isinstance(usage_data, dict):
                usage_dict = usage_data
            else:
                return parsed
    elif isinstance(usage_data, dict):
        usage_dict = usage_data
    else:
        return parsed

    parsed["input_tokens"] = usage_dict.get("input_tokens", usage_dict.get("prompt_tokens"))
    parsed["output_tokens"] = usage_dict.get("output_tokens", usage_dict.get("completion_tokens"))
    parsed["total_tokens"] = usage_dict.get("total_tokens")

    for key in parsed:
        if parsed[key] is not None:
            try:
                parsed[key] = int(parsed[key])  # type: ignore[arg-type]
            except (ValueError, TypeError):
                parsed[key] = None

    return parsed


def _map_span_name(span: AgentSpan) -> str:
    """Determine the name for a given OpenAI Agent span."""
    span_data = getattr(span, "span_data", None)
    if not span_data:
        return getattr(span, "name", "Unknown Span")
    
    if name := getattr(span_data, "name", None):
        return name
    if isinstance(span_data, GenerationSpanData):
        return "LLM Generation"
    if isinstance(span_data, ResponseSpanData):
        return "LLM Response"
    if isinstance(span_data, HandoffSpanData):
        from_agent = getattr(span_data, "from_agent", None)
        to_agent = getattr(span_data, "to_agent", None)
        if from_agent and to_agent:
            return f"Handoff: {from_agent} -> {to_agent}"
        return "Handoff"
    if isinstance(span_data, AgentSpanData):
        return getattr(span_data, "name", "Agent")
    if isinstance(span_data, FunctionSpanData):
        return getattr(span_data, "name", "Function")
    if isinstance(span_data, GuardrailSpanData):
        return "Guardrail"
    if isinstance(span_data, CustomSpanData):
        return getattr(span_data, "name", "Custom Span")
    if hasattr(span_data, "type"):
        span_type = getattr(span_data, "type", "")
        return span_type.capitalize() if span_type else "Span"
    return getattr(span, "name", "Unknown Span")


def _extract_span_attributes(span: AgentSpan, trace_metadata: Dict[str, str]) -> Dict[str, str]:
    attributes: Dict[str, str] = {}
    span_data = getattr(span, "span_data", None)

    if isinstance(span_data, GenerationSpanData):
        if span_data.model:
            attributes["model"] = span_data.model
        if span_data.input is not None:
            attributes["input"] = _safe_json(span_data.input)
        if span_data.output is not None:
            attributes["output"] = _safe_json(span_data.output)
        if span_data.usage:
            usage = span_data.usage if isinstance(span_data.usage, dict) else getattr(span_data.usage, "model_dump", lambda: {})()
            if isinstance(usage, dict):
                for key, value in usage.items():
                    attributes[f"usage_{key}"] = str(value)
        if span_data.model_config and isinstance(span_data.model_config, dict):
            for key, value in span_data.model_config.items():
                attributes[f"model_config_{key}"] = str(value)
    elif isinstance(span_data, ResponseSpanData):
        response = span_data.response
        input_data = getattr(span_data, "input", None)
        
        if input_data is not None:
            attributes["input"] = _safe_json(input_data)
        
        if response:
            if hasattr(response, "model") and response.model:
                attributes["model"] = response.model
            if hasattr(response, "output") and response.output is not None:
                # Extract text from output messages
                output_texts = []
                if isinstance(response.output, list):
                    for item in response.output:
                        if hasattr(item, "content"):
                            content = item.content
                            if isinstance(content, list):
                                for c in content:
                                    if hasattr(c, "text"):
                                        output_texts.append(c.text)
                            elif hasattr(content, "text"):
                                output_texts.append(content.text)
                            else:
                                output_texts.append(str(content))
                if output_texts:
                    attributes["output"] = " ".join(output_texts)
                else:
                    attributes["output"] = _safe_json(response.output)
            
            usage = _parse_usage(getattr(response, "usage", None))
            for key, value in usage.items():
                if value is not None:
                    attributes[f"usage_{key}"] = str(value)
            
            if hasattr(response, "temperature") and response.temperature is not None:
                attributes["temperature"] = str(response.temperature)
            
            if hasattr(response, "instructions") and response.instructions:
                attributes["instructions"] = str(response.instructions)
    elif isinstance(span_data, FunctionSpanData):
        attributes["function_name"] = span_data.name
        if span_data.input is not None:
            attributes["input"] = _safe_json(span_data.input)
        if span_data.output is not None:
            attributes["output"] = _safe_json(span_data.output)
    elif isinstance(span_data, GuardrailSpanData):
        attributes["guardrail_triggered"] = str(span_data.triggered)
    elif isinstance(span_data, AgentSpanData):
        if span_data.name:
            attributes["agent_name"] = span_data.name
        if span_data.tools:
            attributes["agent_tools"] = _safe_json(span_data.tools)
        if span_data.handoffs:
            attributes["agent_handoffs"] = _safe_json(span_data.handoffs)
        if span_data.output_type:
            attributes["agent_output_type"] = span_data.output_type
    elif isinstance(span_data, HandoffSpanData):
        if span_data.from_agent:
            attributes["handoff_from"] = span_data.from_agent
        if span_data.to_agent:
            attributes["handoff_to"] = span_data.to_agent
    elif isinstance(span_data, CustomSpanData):
        for key, value in (span_data.data or {}).items():
            attributes[f"custom_{key}"] = _safe_json(value)

    for key, value in trace_metadata.items():
        attributes.setdefault(f"trace_{key}", value)

    return {k: v for k, v in attributes.items() if v}


def datetime_to_timestamp(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.timestamp()
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(normalized).timestamp()
        except ValueError:
            logger.debug("Unable to parse datetime string: %s", value)
            return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    logger.debug("Unsupported datetime value: %s (%s)", value, type(value))
    return 0.0


def span_kind(agent_span: AgentSpan) -> str:
    span_data = getattr(agent_span, "span_data", None)
    if span_data:
        return _span_kind_from_data(span_data)
    mapping = {
        "agent": "agent",
        "generation": "llm",
        "function": "tool",
        "guardrail": "guardrail",
        "handoff": "handoff",
        "speech": "audio",
        "speech_group": "audio_group",
        "transcription": "audio_transcription",
    }
    return mapping.get(agent_span.span_type, "internal")


def serialize_span(agent_span: AgentSpan, trace_metadata: Dict[str, str]) -> Span:
    raw_events = getattr(agent_span, "events", None) or []
    events = []
    for event in raw_events:
        name = getattr(event, "name", "event")
        timestamp = datetime_to_timestamp(getattr(event, "timestamp", None))
        event_attributes = getattr(event, "attributes", {}) or {}
        events.append(
            {
                "name": name,
                "timestamp": timestamp,
                "attributes": event_attributes,
            }
        )
    
    attributes = _extract_span_attributes(agent_span, trace_metadata=trace_metadata)
    
    span_data = getattr(agent_span, "span_data", None)
    kind = _span_kind_from_data(span_data) if span_data else "internal"
    name = _map_span_name(agent_span)
    
    span_id = getattr(agent_span, "span_id", None) or getattr(agent_span, "id", "span-unknown")
    parent_id = getattr(agent_span, "parent_id", None)
    status = getattr(agent_span, "status", None) or "ok"
    started_at = datetime_to_timestamp(getattr(agent_span, "started_at", None))
    ended_at = datetime_to_timestamp(getattr(agent_span, "ended_at", None))
    
    return Span(
        span_id=span_id,
        parent_id=parent_id,
        name=name,
        kind=kind,
        status=status,
        started_at=started_at,
        ended_at=ended_at,
        attributes=attributes,
        events=events,
    )


def serialize_trace(
    agent_trace: AgentTrace,
    *,
    started_at: datetime | str | None = None,
    ended_at: datetime | str | None = None,
) -> Trace:
    trace_id = getattr(agent_trace, "trace_id", None) or getattr(agent_trace, "id", "trace-unknown")
    workflow_name = getattr(agent_trace, "workflow_name", None) or getattr(agent_trace, "name", "Agent workflow")

    trace_started_at = started_at or getattr(agent_trace, "started_at", None)
    trace_ended_at = ended_at or getattr(agent_trace, "ended_at", None)
    metadata = getattr(agent_trace, "metadata", {}) or {}

    return Trace(
        trace_id=trace_id,
        workflow_name=workflow_name,
        group_id=getattr(agent_trace, "group_id", None),
        started_at=datetime_to_timestamp(trace_started_at),
        ended_at=datetime_to_timestamp(trace_ended_at) if trace_ended_at else None,
        attributes={k: str(v) for k, v in metadata.items()},
        spans=[],
    )


class NeuraltrustTraceProcessor(TracingProcessor):
    def __init__(
        self,
        client: Optional[TelemetryClient] = None,
        config: Optional[TelemetryConfig] = None,
    ) -> None:
        if client is None:
            if config is None:
                config = TelemetryConfig.from_env()
            client = TelemetryClient(config)
        self._client = client
        self._active_traces: dict[str, AgentTrace] = {}
        self._trace_started_at: dict[str, datetime] = {}
        self._trace_spans: dict[str, List[Span]] = {}
        self._span_start_data: dict[str, AgentSpan] = {}

    def on_trace_start(self, trace: AgentTrace) -> None:
        trace_id = getattr(trace, "trace_id", None) or getattr(trace, "id", None)
        if not trace_id:
            logger.debug("Trace received without trace_id; skipping start hook")
            return
        self._active_traces[trace_id] = trace
        self._trace_started_at[trace_id] = datetime.now(timezone.utc)
        self._trace_spans.setdefault(trace_id, [])
        logger.debug("Trace started; trace_id=%s workflow=%s", trace_id, getattr(trace, "name", "unknown"))

    def on_trace_end(self, trace: AgentTrace) -> None:
        trace_id = getattr(trace, "trace_id", None) or getattr(trace, "id", None)
        if not trace_id:
            logger.debug("Trace received without trace_id; skipping end hook")
            return
        started_at = self._trace_started_at.pop(trace_id, None)
        ended_at = datetime.now(timezone.utc)
        self._active_traces.pop(trace_id, None)
        
        # Capture any unfinished spans that were started but not ended
        unfinished_spans = [(sid, sp) for sid, sp in list(self._span_start_data.items()) if getattr(sp, "trace_id", None) == trace_id]
        logger.debug("Checking for unfinished spans; trace_id=%s unfinished_count=%s", trace_id, len(unfinished_spans))
        for span_id, span in unfinished_spans:
            self._span_start_data.pop(span_id, None)
            logger.debug("Capturing unfinished span; span_id=%s trace_id=%s type=%s", 
                        span_id, trace_id, type(getattr(span, "span_data", None)).__name__)
            metadata = self._get_trace_metadata(trace_id)
            try:
                serialized = serialize_span(span, trace_metadata=metadata)
                self._trace_spans.setdefault(trace_id, []).append(serialized)
                logger.debug("Unfinished span serialized; span_id=%s", span_id)
            except Exception as exc:
                logger.exception("Failed to serialize unfinished span; span_id=%s error=%s", span_id, exc)
        
        spans = self._trace_spans.pop(trace_id, [])
        logger.debug(
            "Trace finished; trace_id=%s span_count=%s",
            trace_id,
            len(spans),
        )
        try:
            envelope = self._to_envelope(trace, started_at=started_at, ended_at=ended_at, spans=spans)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Failed to serialize agent trace: %s", exc)
            return
        self._client.emit_envelope(envelope)

    def on_span_start(self, span: AgentSpan) -> None:  # pragma: no cover - no-op hook
        span_data = getattr(span, "span_data", None)
        span_type = type(span_data).__name__ if span_data else "None"
        span_id = getattr(span, "span_id", None)
        trace_id = getattr(span, "trace_id", None)
        
        if span_id and trace_id:
            self._span_start_data[span_id] = span
            logger.debug(
                "Span buffered on start; span_id=%s trace_id=%s type=%s buffer_size=%s",
                span_id,
                trace_id,
                span_type,
                len(self._span_start_data),
            )
        else:
            logger.debug(
                "Span started but not buffered (missing id); span_id=%s trace_id=%s type=%s",
                span_id,
                trace_id,
                span_type,
            )
        return

    def on_span_end(self, span: AgentSpan) -> None:  # pragma: no cover - no-op hook
        trace_id = getattr(span, "trace_id", None)
        span_id = getattr(span, "span_id", None)
        
        if not trace_id:
            logger.debug("Span ended without trace_id; skipping")
            return
        
        # Remove from start data if present
        was_buffered = False
        if span_id:
            was_buffered = self._span_start_data.pop(span_id, None) is not None
        
        span_data = getattr(span, "span_data", None)
        span_type = type(span_data).__name__ if span_data else "None"
        
        metadata = self._get_trace_metadata(trace_id)
        serialized = serialize_span(span, trace_metadata={k: str(v) for k, v in metadata.items()})
        self._trace_spans.setdefault(trace_id, []).append(serialized)
        logger.debug(
            "Span ended; span_id=%s trace_id=%s type=%s was_buffered=%s stored_spans=%s",
            span_id,
            trace_id,
            span_type,
            was_buffered,
            len(self._trace_spans[trace_id]),
        )
        return

    def shutdown(self) -> None:
        self._flush_active_traces()
        # Use synchronous close to avoid asyncio shutdown issues
        try:
            self._client.close_sync()
        except Exception as e:
            logger.warning("Error during telemetry client close: %s", e)

    def force_flush(self) -> None:
        self._flush_active_traces()

    def _flush_active_traces(self) -> None:
        for trace_id, trace in list(self._active_traces.items()):
            started_at = self._trace_started_at.pop(trace_id, None)
            ended_at = datetime.now(timezone.utc)
            spans = self._trace_spans.pop(trace_id, [])
            try:
                envelope = self._to_envelope(trace, started_at=started_at, ended_at=ended_at, spans=spans)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Failed to serialize agent trace during flush: %s", exc)
                continue
            logger.debug("Trace flushed during shutdown; trace_id=%s span_count=%s", trace_id, len(spans))
            self._client.emit_envelope(envelope)
        self._active_traces.clear()

    def _run_async(self, coro: asyncio.Future | asyncio.Task | asyncio.coroutines.coroutine) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            with suppress(asyncio.CancelledError, RuntimeError):
                asyncio.run(coro)
        else:
            loop.create_task(coro)

    def _get_trace_metadata(self, trace_id: str) -> Dict[str, str]:
        trace = self._active_traces.get(trace_id)
        if not trace:
            return {}
        metadata = getattr(trace, "metadata", {}) or {}
        return {k: str(v) for k, v in metadata.items()}

    def _to_envelope(
        self,
        agent_trace: AgentTrace,
        *,
        started_at: datetime | None = None,
        ended_at: datetime | None = None,
        spans: Optional[List[Span]] = None,
    ) -> TraceEnvelope:
        metadata = getattr(agent_trace, "metadata", {}) or {}
        resource = SDK_RESOURCE.copy(
            update={
                "library_version": metadata.get("sdk_version"),
            }
        )

        trace = serialize_trace(agent_trace, started_at=started_at, ended_at=ended_at)
        trace.spans = spans or []
        logger.debug(
            "Trace envelope prepared; trace_id=%s span_count=%s",
            trace.trace_id,
            len(trace.spans),
        )

        return TraceEnvelope(resource=resource, traces=[trace])


def register_openai_tracing(
    *,
    client: Optional[TelemetryClient] = None,
    config: Optional[TelemetryConfig] = None,
    replace_default: bool = True,
) -> NeuraltrustTraceProcessor:
    processor = NeuraltrustTraceProcessor(client=client, config=config)
    if replace_default:
        set_trace_processors([processor])
        logger.info("Registered Neuraltrust trace processor and replaced default exporters")
    else:
        add_trace_processor(processor)
        logger.info("Registered Neuraltrust trace processor for OpenAI Agents")
    return processor

