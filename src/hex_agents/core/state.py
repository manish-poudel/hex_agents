from typing import Any
from typing_extensions import Annotated, TypedDict


def add_tokens(current, updates):
    """Accumulate token usage."""
    return (current or 0) + (updates or 0)


def replace_value(current, updates):
    """Always replace with the latest value."""
    return updates



class TokenUsage(TypedDict):
    id: str
    node_id: str
    model_provider: str
    model_name: str

    usage_details: dict[str, Any]


class LLMState(TypedDict, total=False):
    last_message: Annotated[Any | None, replace_value]
    token_usage: Annotated[TokenUsage | None, replace_value]
    output: Annotated[str | None, replace_value]