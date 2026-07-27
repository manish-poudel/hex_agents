from typing import TypedDict
from typing_extensions import Annotated
from langgraph.graph.message import add_messages


class WorkflowState(TypedDict):

    messages: Annotated[list, add_messages]

    outputs: dict

    used_tools: dict