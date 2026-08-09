from typing import Any
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages

from typing import Literal


def ignore_updates(current, updates):
    """Keep initial value, ignore all updates"""
    return current


def add_interrupts(current, updates):
    """Append new interrupts to the list"""
    if not updates:
        return current
    if not isinstance(updates, list):
        updates = [updates]
    return current + updates if current else updates


def merge_dicts(current, updates):
    """Merge dictionaries"""
    if not updates:
        return current
    if not isinstance(updates, dict):
        return current
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
        "cancelled"
    ]
    response: Any | None

class WorkflowState(TypedDict):
    workflow_id: Annotated[str, ignore_updates]
    workflow_run_id: Annotated[str, ignore_updates]
    messages: Annotated[list, add_messages]

    outputs: Annotated[dict[str, Any], merge_dicts]

    used_tools: Annotated[dict[str, Any], merge_dicts]

    interrupts: Annotated[list[InterruptState], add_interrupts]

    final_output: str