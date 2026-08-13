from hex_agents.actions.storage_action import get_storage_node
from hex_agents.agents.action_node import ActionNode
from hex_agents.actions.file_retrieval_action import get_file
from hex_agents.agents.async_action_node import AsyncActionNode


class ActionRegistry:

    @staticmethod
    def create(action: dict):

        if action["kind"] == "read_file":

            return ActionNode(

                get_file(
                    id=action["id"],
                    path=action["path"]

                )

            )
            
        if action["kind"] == "read_file":

            return ActionNode(
                get_file(
                    id=action["id"],
                    path=action["path"]

                )

            )
            
        if action["kind"] == "access_storage_node":
            print("creating access_storage_node action")
            return AsyncActionNode(
                get_storage_node(
                    node_id=action["node_id"]
                )
            )

        raise Exception(
            f"Unknown action: {action['kind']}"
        )