
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
    
    
    
