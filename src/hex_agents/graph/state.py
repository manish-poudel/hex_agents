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

    input_tokens: Annotated[int, add_tokens]
    output_tokens: Annotated[int, add_tokens]
    total_tokens: Annotated[int, add_tokens]