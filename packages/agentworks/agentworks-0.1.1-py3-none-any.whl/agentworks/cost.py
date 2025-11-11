"""Cost calculation for LLM calls."""

from decimal import Decimal

# Pricing map: model -> (input_price_per_1k, output_price_per_1k)
PRICING_MAP: dict[str, tuple[Decimal, Decimal]] = {
    # OpenAI
    "gpt-4": (Decimal("0.03"), Decimal("0.06")),
    "gpt-4-turbo": (Decimal("0.01"), Decimal("0.03")),
    "gpt-4o": (Decimal("0.005"), Decimal("0.015")),
    "gpt-4o-mini": (Decimal("0.00015"), Decimal("0.0006")),
    "gpt-3.5-turbo": (Decimal("0.0005"), Decimal("0.0015")),

    # Anthropic
    "claude-3-opus": (Decimal("0.015"), Decimal("0.075")),
    "claude-3-sonnet": (Decimal("0.003"), Decimal("0.015")),
    "claude-3-haiku": (Decimal("0.00025"), Decimal("0.00125")),
    "claude-3-5-sonnet": (Decimal("0.003"), Decimal("0.015")),

    # Google
    "gemini-pro": (Decimal("0.00025"), Decimal("0.0005")),
    "gemini-pro-vision": (Decimal("0.00025"), Decimal("0.0005")),
    "gemini-1.5-pro": (Decimal("0.00125"), Decimal("0.005")),
    "gemini-1.5-flash": (Decimal("0.000075"), Decimal("0.0003")),
}


def calculate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> Decimal:
    """
    Calculate cost for an LLM call.

    Args:
        model: Model name
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens

    Returns:
        Cost in USD (Decimal for precision)
    """
    # Normalize model name (remove version suffixes, etc.)
    normalized_model = normalize_model_name(model)

    if normalized_model not in PRICING_MAP:
        # Unknown model, return 0
        return Decimal("0")

    input_price, output_price = PRICING_MAP[normalized_model]

    # Calculate cost (prices are per 1k tokens)
    input_cost = (Decimal(str(prompt_tokens)) / 1000) * input_price
    output_cost = (Decimal(str(completion_tokens)) / 1000) * output_price

    return input_cost + output_cost


def normalize_model_name(model: str) -> str:
    """
    Normalize model name for pricing lookup.

    Args:
        model: Raw model name

    Returns:
        Normalized model name
    """
    # Remove common prefixes and suffixes
    model = model.lower().strip()

    # Remove date suffixes (e.g., gpt-4-turbo-2024-04-09 -> gpt-4-turbo)
    # Only remove if there are 3 consecutive numeric parts at the end (date pattern)
    # or if the last part is a 4+ digit number (likely a year or timestamp)
    parts = model.split("-")

    # Check for date pattern: YYYY-MM-DD (3 consecutive numeric parts at end)
    if len(parts) >= 3 and all(p.isdigit() for p in parts[-3:]):
        # Remove date suffix (last 3 parts)
        model = "-".join(parts[:-3])

    # Map aliases
    aliases = {
        "gpt-4-1106-preview": "gpt-4-turbo",
        "gpt-4-0125-preview": "gpt-4-turbo",
        "gpt-4-turbo-preview": "gpt-4-turbo",
        "gpt-35-turbo": "gpt-3.5-turbo",
    }

    return aliases.get(model, model)


def get_model_pricing(model: str) -> tuple[Decimal, Decimal]:
    """
    Get pricing for a model.

    Args:
        model: Model name

    Returns:
        Tuple of (input_price_per_1k, output_price_per_1k)
    """
    normalized_model = normalize_model_name(model)
    return PRICING_MAP.get(normalized_model, (Decimal("0"), Decimal("0")))

