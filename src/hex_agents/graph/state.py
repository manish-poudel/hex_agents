from typing import Any, Literal
from typing_extensions import Annotated, TypedDict

from hex_agents.core.state import LLMState


def ignore_updates(current, updates):
    """Keep first non-empty value, ignore subsequent updates."""
    if current in (None, ""):
        return updates

    return current


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


class WorkflowState(LLMState, total=False):
    workflow_id: Annotated[str, ignore_updates]
    workflow_run_id: Annotated[str, ignore_updates]
