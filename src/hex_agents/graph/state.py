from typing import Any, Literal
from typing_extensions import Annotated, TypedDict


def ignore_updates(current, updates):
    """Keep first non-empty value, ignore subsequent updates."""
    if current in (None, ""):
        return updates

    return current


def add_tokens(current, updates):
    """Accumulate token usage across workflow nodes."""
    return (current or 0) + (updates or 0)


def replace_value(current, updates):
    """Always replace the current value with the latest value."""
    return updates


class TokenUsage(TypedDict):
    id: str
    node_id: str
    model_name: str
    input_tokens: int
    output_tokens: int
    total_tokens: int


class InterruptState(TypedDict):
    id: str
    type: Literal["approval", "input", "confirmation"]
    status: Literal[
        "waiting",
        "approved",
        "rejected",
        "cancelled",
    ]
    response: Any | None


class WorkflowState(TypedDict):
    workflow_id: Annotated[str, ignore_updates]
    workflow_run_id: Annotated[str, ignore_updates]

    output: str | None

    # Cumulative workflow usage
    input_tokens: Annotated[int, add_tokens]
    output_tokens: Annotated[int, add_tokens]
    total_tokens: Annotated[int, add_tokens]

    # Latest LLM invocation only
    last_usage: Annotated[TokenUsage | None, replace_value]