from hex_agents.actions.storage_action import get_storage_node
from hex_agents.agents.async_action_node import AsyncActionNode


class ActionRegistry:

    def __init__(self, actions: dict):
        self.actions = actions

    def create(self, action: dict):

        factory = self.actions.get(action["kind"])

        if factory is None:
            raise ValueError(
                f"Unknown action: {action['kind']}"
            )

        return factory(action)
    
    
    
def create_storage_action(action):
    return AsyncActionNode(
        get_storage_node(
            node_id=action["node_id"]
        )
    )
    