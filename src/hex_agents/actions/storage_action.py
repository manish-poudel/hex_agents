from typing import Any

from anyio import sleep

from hex_agents.agents.async_action_node import AsyncActionNode




def access_storage_node(action):
    return AsyncActionNode(
        get_storage_node(
            node_id=action["file_id"]
        )
    )
    

def get_storage_node(node_id: str):

    async def action() -> Any:
        await sleep(1)  # Simulate some async operation
        return f"Data from storage node {node_id}"
       
    return action


