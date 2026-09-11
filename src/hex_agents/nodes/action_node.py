from langchain.messages import HumanMessage

from hex_agents.graph.state import WorkflowState


class ActionNode:

    def __init__(
        self,
        action,
    ):
        self.action = action
        self.id = getattr(action, "__name__", action.__class__.__name__)

    def _debug(self, message: str) -> None:
        
        pass

    def _preview(self, value: str, limit: int = 240) -> str:
        if len(value) <= limit:
            return value
        return value[:limit] + "..."

    def __call__(
        self,
        state: dict,
    ) -> dict:

        input_output = state.get("output", "")
        print(
            f"starting with input output={self._preview(input_output)!r}"
        )

        next_state = self.action(state)

        output = next_state.get("output", "")
        print(
            f"completed with output={self._preview(output)!r}"
        )
        print("output")

        return {
            "messages": [HumanMessage(content=output)],
            "output": output,
        }