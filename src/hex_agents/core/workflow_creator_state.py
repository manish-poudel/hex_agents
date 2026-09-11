from typing import Annotated, Any

from hex_agents.core.state import LLMState

def ignore_updates(current, updates):
    """Keep first non-empty value, ignore subsequent updates."""
    if current in (None, ""):
        return updates

    return current


class WorkflowCreatorState(LLMState, total=False):
    user_request: Annotated[str, ignore_updates]
