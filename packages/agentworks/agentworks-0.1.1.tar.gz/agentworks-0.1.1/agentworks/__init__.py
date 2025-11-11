"""AgentWorks SDK for Python."""

from agentworks.config import configure
from agentworks.tracing import (
    get_current_span_id,
    get_current_trace_id,
    llm_call,
    send_span,
    trace_agent,
    trace_decision,
    trace_tool,
)

__version__ = "0.1.0"

__all__ = [
    "trace_agent",
    "trace_tool",
    "trace_decision",
    "llm_call",
    "send_span",
    "get_current_trace_id",
    "get_current_span_id",
    "configure",
]

