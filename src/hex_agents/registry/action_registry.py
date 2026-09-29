
class ActionRegistry:

    def __init__(self, actions: dict):
        self.actions = actions

    def create(self, action: dict):

        
        kind  = action["kind"]
        factory = self.actions.get(kind)
 

        if factory is None:
            raise ValueError(
                f"Unknown action: {action['kind']}"
            )

        return factory(action)
