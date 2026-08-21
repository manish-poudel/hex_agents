from hex_agents.tools.base import Tool


class BaseTool:

    def __init__(self, filtered_tools: list[str] | None = None):
        self.filtered_tools = filtered_tools
        self.tools: list[Tool] = []

    def load_tools(self, available_tools: dict[str, Tool]) -> None:
        """
        Load all tools or only the requested tools.
        """

        if self.filtered_tools is None:
            self.tools = list(available_tools.values())
            return

        self.tools = [
            available_tools[key]
            for key in self.filtered_tools
            if key in available_tools
        ]

    def definitions(self) -> list[dict[str, str]]:
        return [
            tool.definition()
            for tool in self.tools
        ]