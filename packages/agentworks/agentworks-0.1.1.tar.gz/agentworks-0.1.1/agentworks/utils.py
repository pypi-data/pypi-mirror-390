"""Utility functions."""

import secrets
import time
from datetime import datetime


def generate_trace_id() -> str:
    """
    Generate W3C-compatible trace ID (32 hex chars).

    Returns:
        32-character hexadecimal string
    """
    return secrets.token_hex(16)


def generate_span_id() -> str:
    """
    Generate W3C-compatible span ID (16 hex chars).

    Returns:
        16-character hexadecimal string
    """
    return secrets.token_hex(8)


def current_timestamp_ms() -> int:
    """
    Get current timestamp in milliseconds.

    Returns:
        Current time in milliseconds since epoch
    """
    return int(time.time() * 1000)


def timestamp_to_datetime(ts_ms: int) -> datetime:
    """
    Convert millisecond timestamp to datetime.

    Args:
        ts_ms: Timestamp in milliseconds

    Returns:
        datetime object in UTC
    """
    return datetime.utcfromtimestamp(ts_ms / 1000)


def format_traceparent(trace_id: str, span_id: str, sampled: bool = True) -> str:
    """
    Format W3C traceparent header.

    Format: version-trace_id-span_id-flags
    Example: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01

    Args:
        trace_id: 32-character hex trace ID
        span_id: 16-character hex span ID
        sampled: Whether the trace is sampled

    Returns:
        W3C traceparent header value
    """
    flags = "01" if sampled else "00"
    return f"00-{trace_id}-{span_id}-{flags}"


def parse_traceparent(traceparent: str) -> tuple[str, str, bool]:
    """
    Parse W3C traceparent header.

    Args:
        traceparent: W3C traceparent header value

    Returns:
        Tuple of (trace_id, span_id, sampled)
    """
    parts = traceparent.split("-")
    if len(parts) != 4:
        raise ValueError(f"Invalid traceparent format: {traceparent}")

    version, trace_id, span_id, flags = parts

    if version != "00":
        raise ValueError(f"Unsupported traceparent version: {version}")

    sampled = flags.endswith("1")

    return trace_id, span_id, sampled

