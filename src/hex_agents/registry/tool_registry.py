
from hex_agents.tools.access_file import create_access_file_tool




class ToolRegistry:
    

    def __init__(self, tools: dict):
        self.tools = tools

    def create(self, name: str):

        factory = self.tools.get(name)

        if factory is None:
            raise ValueError(
                f"Unknown tool: {name}"
            )
        print(f"Creating tool: {name} using factory: {factory}")

        return factory


