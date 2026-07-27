from hex_agents.graph.state import WorkflowState


class ActionNode:

    def __init__(
        self,
        action,
    ):
        self.action = action

    def __call__(
        self,
        state: WorkflowState,
    ) -> WorkflowState:

        return self.action(state)