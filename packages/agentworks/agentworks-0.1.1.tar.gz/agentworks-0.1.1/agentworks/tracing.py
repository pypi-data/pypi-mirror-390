"""Tracing context managers and utilities."""

import time
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from typing import Any

from agentworks.config import get_config
from agentworks.cost import calculate_cost
from agentworks.otlp import send_span_to_ingest
from agentworks.pii import redact_pii
from agentworks.utils import generate_span_id, generate_trace_id

# Context variables for trace propagation
_trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)
_span_id_var: ContextVar[str | None] = ContextVar("span_id", default=None)
_parent_span_id_var: ContextVar[str | None] = ContextVar("parent_span_id", default=None)


def get_current_trace_id() -> str:
    """Get current trace ID, creating one if needed."""
    trace_id = _trace_id_var.get()
    if trace_id is None:
        trace_id = generate_trace_id()
        _trace_id_var.set(trace_id)
    return trace_id


def get_current_span_id() -> str | None:
    """Get current span ID."""
    return _span_id_var.get()


@contextmanager
def trace_agent(
    agent_id: str,
    workflow_id: str | None = None,
    **attrs: str,
) -> Generator[str, None, None]:
    """
    Trace an agent execution.

    Args:
        agent_id: Unique identifier for the agent
        workflow_id: Optional workflow identifier
        **attrs: Additional attributes to attach to the span

    Yields:
        span_id: The generated span ID

    Example:
        with trace_agent("support-bot", workflow_id="ticket-123") as span_id:
            # Your agent logic here
            pass
    """
    config = get_config()

    # Generate IDs
    trace_id = get_current_trace_id()
    span_id = generate_span_id()
    parent_span_id = _span_id_var.get()

    # Set current span
    token_span = _span_id_var.set(span_id)
    token_parent = _parent_span_id_var.set(parent_span_id)

    start_time = time.time()
    error_type = ""
    error_msg = ""
    status = "ok"

    try:
        yield span_id
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        status = "error"
        raise
    finally:
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        # Build attributes
        span_attrs: dict[str, str] = {
            "aw.agent_id": agent_id,
            "aw.kind": "agent",
        }

        if workflow_id:
            span_attrs["aw.workflow_id"] = workflow_id

        # Convert all attr values to strings for validation
        for key, value in attrs.items():
            span_attrs[key] = str(value)

        # Send span
        send_span_to_ingest(
            org_id=config.org_id,
            project_id=config.project_id,
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_span_id or "",
            ts=datetime.utcfromtimestamp(start_time),
            kind="agent",
            name=agent_id,
            status=status,
            latency_ms=latency_ms,
            attrs=span_attrs,
            error_type=error_type,
            error_msg=error_msg,
        )

        # Reset context
        _span_id_var.reset(token_span)
        _parent_span_id_var.reset(token_parent)


@contextmanager
def trace_tool(
    name: str,
    **attrs: str,
) -> Generator[str, None, None]:
    """
    Trace a tool execution.

    Args:
        name: Tool name
        **attrs: Additional attributes

    Yields:
        span_id: The generated span ID

    Example:
        with trace_tool("fetch_user_data") as span_id:
            user = fetch_user_data(user_id)
    """
    config = get_config()

    trace_id = get_current_trace_id()
    span_id = generate_span_id()
    parent_span_id = _span_id_var.get()

    token_span = _span_id_var.set(span_id)
    token_parent = _parent_span_id_var.set(parent_span_id)

    start_time = time.time()
    error_type = ""
    error_msg = ""
    status = "ok"

    try:
        yield span_id
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        status = "error"
        raise
    finally:
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        span_attrs: dict[str, str] = {
            "aw.tool": name,
            "aw.kind": "tool",
        }
        # Convert all attr values to strings for validation
        for key, value in attrs.items():
            span_attrs[key] = str(value)

        send_span_to_ingest(
            org_id=config.org_id,
            project_id=config.project_id,
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_span_id or "",
            ts=datetime.utcfromtimestamp(start_time),
            kind="tool",
            name=name,
            status=status,
            latency_ms=latency_ms,
            attrs=span_attrs,
            error_type=error_type,
            error_msg=error_msg,
        )

        _span_id_var.reset(token_span)
        _parent_span_id_var.reset(token_parent)


@contextmanager
def trace_decision(
    policy: str = "default",
    **attrs: str,
) -> Generator[str, None, None]:
    """
    Trace a decision point.

    Args:
        policy: Policy name
        **attrs: Additional attributes

    Yields:
        span_id: The generated span ID
    """
    config = get_config()

    trace_id = get_current_trace_id()
    span_id = generate_span_id()
    parent_span_id = _span_id_var.get()

    token_span = _span_id_var.set(span_id)
    token_parent = _parent_span_id_var.set(parent_span_id)

    start_time = time.time()

    try:
        yield span_id
    finally:
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        span_attrs: dict[str, str] = {
            "aw.policy": policy,
            "aw.kind": "decision",
        }
        # Convert all attr values to strings for validation
        for key, value in attrs.items():
            span_attrs[key] = str(value)

        send_span_to_ingest(
            org_id=config.org_id,
            project_id=config.project_id,
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_span_id or "",
            ts=datetime.utcfromtimestamp(start_time),
            kind="decision",
            name=f"decision:{policy}",
            status="ok",
            latency_ms=latency_ms,
            attrs=span_attrs,
        )

        _span_id_var.reset(token_span)
        _parent_span_id_var.reset(token_parent)


def llm_call(
    model: str,
    provider: str,
    prompt: str,
    completion: str = "",
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    **attrs: Any,
) -> dict[str, Any]:
    """
    Trace an LLM call.

    This is a simplified wrapper. In practice, you'd instrument
    the actual LLM client (OpenAI, Anthropic, etc.)

    Args:
        model: Model name
        provider: Provider (openai, anthropic, google)
        prompt: Input prompt
        completion: Output completion
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens
        **attrs: Additional attributes

    Returns:
        Dict with span metadata
    """
    config = get_config()

    trace_id = get_current_trace_id()
    span_id = generate_span_id()
    parent_span_id = _span_id_var.get()

    start_time = time.time()

    # PII detection and redaction
    redacted_prompt = prompt
    redacted_completion = completion
    pii_types = []

    if config.redact_pii:
        redacted_prompt, pii_types_prompt = redact_pii(prompt)
        redacted_completion, pii_types_completion = redact_pii(completion)
        pii_types = list(set(pii_types_prompt + pii_types_completion))

    # Calculate cost
    cost_usd = calculate_cost(model, prompt_tokens, completion_tokens)

    end_time = time.time()
    latency_ms = int((end_time - start_time) * 1000)

    # Build attributes
    span_attrs: dict[str, str] = {
        "aw.model": model,
        "aw.provider": provider,
        "aw.kind": "llm",
        "aw.prompt_tokens": str(prompt_tokens),
        "aw.completion_tokens": str(completion_tokens),
        "aw.total_tokens": str(prompt_tokens + completion_tokens),
        "aw.cost_usd": str(cost_usd),
    }

    if pii_types:
        span_attrs["aw.pii_types"] = ",".join(pii_types)

    for key, value in attrs.items():
        span_attrs[f"aw.{key}"] = str(value)

    send_span_to_ingest(
        org_id=config.org_id,
        project_id=config.project_id,
        trace_id=trace_id,
        span_id=span_id,
        parent_id=parent_span_id or "",
        ts=datetime.utcfromtimestamp(start_time),
        kind="llm",
        name=f"{provider}:{model}",
        status="ok",
        latency_ms=latency_ms,
        attrs=span_attrs,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        cost_usd=cost_usd,
        pii_flag=1 if pii_types else 0,
    )

    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "cost_usd": float(cost_usd),
        "pii_detected": pii_types,
    }


def send_span(
    kind: str,
    name: str,
    latency_ms: int,
    status: str = "ok",
    **attrs: str,
) -> None:
    """
    Send a custom span.

    Args:
        kind: Span kind (agent, tool, llm, decision, custom)
        name: Span name
        latency_ms: Latency in milliseconds
        status: Span status (ok, error, timeout)
        **attrs: Additional attributes
    """
    config = get_config()

    trace_id = get_current_trace_id()
    span_id = generate_span_id()
    parent_span_id = _span_id_var.get()

    span_attrs: dict[str, str] = {"aw.kind": kind}
    # Convert all attr values to strings for validation
    for key, value in attrs.items():
        span_attrs[key] = str(value)

    send_span_to_ingest(
        org_id=config.org_id,
        project_id=config.project_id,
        trace_id=trace_id,
        span_id=span_id,
        parent_id=parent_span_id or "",
        ts=datetime.utcnow(),
        kind=kind,
        name=name,
        status=status,
        latency_ms=latency_ms,
        attrs=span_attrs,
    )

