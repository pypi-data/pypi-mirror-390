# AgentWorks Python SDK

Instrument and observe your multi-agent AI systems with a single line of code.

## Installation

```bash
pip install agentworks
```

## Quick Start

```python
from agentworks import trace_agent, trace_tool, llm_call, configure

# Configure SDK
configure(
    ingest_endpoint="http://localhost:8080",
    org_id="my-org",
    project_id="my-project",
)

# Trace your agent
with trace_agent("support-bot", workflow_id="ticket-123"):
    
    # Trace tool calls
    with trace_tool("fetch_user_data"):
        user = fetch_user_data(user_id)
    
    # Trace LLM calls with automatic cost tracking
    result = llm_call(
        model="gpt-4",
        provider="openai",
        prompt=f"Summarize: {user.history}",
        completion=response_text,
        prompt_tokens=150,
        completion_tokens=50,
    )
```

## Features

- **Zero-overhead instrumentation**: <5ms latency per span
- **Automatic cost tracking**: Built-in pricing for OpenAI, Anthropic, Google
- **PII detection & redaction**: Protect sensitive data automatically
- **W3C trace propagation**: Compatible with OpenTelemetry
- **Framework agnostic**: Works with any Python agent framework

## API Reference

### Configuration

```python
configure(
    ingest_endpoint="http://localhost:8080",  # AgentWorks API endpoint
    api_key="aw_...",                         # API key (optional for dev)
    org_id="my-org",                          # Organization ID
    project_id="my-project",                  # Project ID
    redact_pii=True,                          # Enable PII redaction
    debug=False,                              # Enable debug logging
)
```

### Tracing

#### `trace_agent(agent_id, workflow_id=None, **attrs)`

Trace an agent execution.

```python
with trace_agent("support-bot", workflow_id="ticket-123") as span_id:
    # Agent logic here
    pass
```

#### `trace_tool(name, **attrs)`

Trace a tool execution.

```python
with trace_tool("stripe_refund", amount="50.00") as span_id:
    # Tool logic here
    pass
```

#### `trace_decision(policy="default", **attrs)`

Trace a decision point.

```python
with trace_decision(policy="routing-v1", task="classification") as span_id:
    model = select_model(task)
```

#### `llm_call(model, provider, prompt, completion, prompt_tokens, completion_tokens, **attrs)`

Trace an LLM call with automatic cost calculation and PII detection.

```python
result = llm_call(
    model="gpt-4",
    provider="openai",
    prompt="Classify: ...",
    completion="Category: Support",
    prompt_tokens=100,
    completion_tokens=10,
    temperature=0.7,
)
# Returns: {"trace_id": "...", "span_id": "...", "cost_usd": 0.0045, "pii_detected": []}
```

### Utilities

#### `get_current_trace_id()`

Get the current trace ID.

```python
trace_id = get_current_trace_id()
```

#### `get_current_span_id()`

Get the current span ID.

```python
span_id = get_current_span_id()
```

## Supported Models

The SDK includes built-in pricing for:

- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-4o, GPT-3.5 Turbo
- **Anthropic**: Claude 3 Opus, Sonnet, Haiku, Claude 3.5 Sonnet
- **Google**: Gemini Pro, Gemini 1.5 Pro/Flash

## PII Detection

Automatically detects and redacts:

- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers
- API keys

Configure PII patterns:

```python
configure(
    redact_pii=True,
    pii_patterns="email,phone,ssn,credit_card,api_key",
)
```

## Examples

See `examples/agents-python/` for complete examples:

- `support_flow.py` - Customer support agent with error handling and PII
- `research_flow.py` - Research agent with multiple tools
- `extractor_flow.py` - Data extraction agent

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run linter
poetry run ruff check agentworks

# Type check
poetry run mypy agentworks
```

## License

MIT

