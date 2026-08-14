
from hex_agents.actions.storage_action import access_storage_node, get_storage_node
from hex_agents.agents.async_action_node import AsyncActionNode


class Actions:
    available= {
        "access_storage_node": access_storage_node,
    }
