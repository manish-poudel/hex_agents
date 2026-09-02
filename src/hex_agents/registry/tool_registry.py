from typing import Type

from hex_agents.tools.base_tools import BaseTool


class ToolRegistry:

    def __init__(
        self,
        tool_providers: dict[str, Type[BaseTool]],
        filters: dict[str, list[str]] | None = None,
    ):
        self.tool_providers = tool_providers
        self.filters = filters or {}
        self._instances: dict[str, BaseTool] = {}

    def get_provider(self, provider: str) -> BaseTool:

        if provider not in self._instances:

            tool_class = self.tool_providers.get(provider)

            if tool_class is None:
                raise ValueError(
                    f"Unknown tool provider: {provider}"
                )

            filtered_tools = self.filters.get(provider)

            self._instances[provider] = tool_class(
                filtered_tools=filtered_tools
            )

        return self._instances[provider]
    

    def get_tools(self, provider: str) -> list:
        return self.get_provider(provider).tools
    

    def get_tool(
        self,
        provider: str,
        key: str,
    ):
        tools = self.get_tools(provider)

        for tool in tools:
            if tool.key == key:
                return tool

        raise ValueError(
            f"Unknown tool '{key}' for provider '{provider}'"
        )
        
    def get_all_tools(self) -> list:
        tools = []

        for provider in self.tool_providers:
            tools.extend(self.get_tools(provider))

        return tools