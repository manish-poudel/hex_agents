from pprint import pprint

from hex_agents.graph.state import WorkflowState


def print_state(
    state: WorkflowState,
) -> WorkflowState:

    print()

    print("=" * 80)
    print("STATE")
    print("=" * 80)

    pprint(state)

    print()

    return state