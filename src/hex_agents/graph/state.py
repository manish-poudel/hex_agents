from typing import Any
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages

from typing import Literal

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
    messages: Annotated[list, add_messages]

    outputs: dict[str, Any]

    used_tools: dict[str, Any]

    interrupts: list[InterruptState]

    final_output: str