from hex_agents.graph.state import WorkflowState


class ActionNode:

    def __init__(
        self,
        action,
    ):
        self.action = action
        self.id = getattr(action, "__name__", action.__class__.__name__)

    def _debug(self, message: str) -> None:
        print(f"[ActionNode:{self.id}] {message}")

    def _preview(self, value: str, limit: int = 240) -> str:
        if len(value) <= limit:
            return value
        return value[:limit] + "..."

    def __call__(
        self,
        state: WorkflowState,
    ) -> WorkflowState:

        input_output = state.get("output", "")
        self._debug(
            f"starting with input output={self._preview(input_output)!r}"
        )

        next_state = self.action(state)

        output = next_state.get("output", "")
        self._debug(
            f"completed with output={self._preview(output)!r}"
        )

        return next_state