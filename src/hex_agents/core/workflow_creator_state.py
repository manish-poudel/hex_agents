from typing import Any

from hex_agents.core.state import LLMState


class WorkflowCreatorState(LLMState, total=False):
    user_request: str
    knowledge: str
    context: dict[str, Any]
    workflow: Any