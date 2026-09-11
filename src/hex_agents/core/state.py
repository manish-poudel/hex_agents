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
    model_name: str
    input_tokens: int
    output_tokens: int
    total_tokens: int


class LLMState(TypedDict, total=False):
    # Conversation / LLM message history

    # Most recent message
    last_message: Annotated[Any | None, replace_value]

    # Cumulative token usage
    input_tokens: Annotated[int, add_tokens]
    output_tokens: Annotated[int, add_tokens]
    total_tokens: Annotated[int, add_tokens]

    # Latest LLM invocation
    last_usage: Annotated[TokenUsage | None, replace_value]
    output: Annotated[str | None, replace_value]