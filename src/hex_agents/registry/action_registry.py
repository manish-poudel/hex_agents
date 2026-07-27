from hex_agents.agents.action_node import ActionNode
from hex_agents.actions.file_retrieval_action import get_file


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

        raise Exception(
            f"Unknown action: {action['kind']}"
        )