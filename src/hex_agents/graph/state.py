from typing import Any, Literal
from typing_extensions import Annotated, TypedDict


def ignore_updates(current, updates):
    """Keep first non-empty value, ignore subsequent updates."""
    if current in (None, ""):
        return updates

    return current


def merge_dicts(current, updates):
    """Merge dictionary updates into the existing dictionary."""
    if not updates:
        return current or {}

    if not isinstance(updates, dict):
        return current or {}

    result = current.copy() if current else {}
    result.update(updates)

    return result


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

    output: str