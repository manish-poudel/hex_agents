from hex_agents.tools.trash.access_file import create_access_file_tool
from hex_agents.tools.trash.access_storage import create_storage_tool


class ToolRegistry:

    @staticmethod
    def create(tool_json):

        name = tool_json["name"]

        if name == "access_file":
            return create_access_file_tool()

        if name == "access_file_storage":
            return create_access_file_tool()

        if name == "access_storage":
            return create_storage_tool()

        raise Exception(f"Unknown tool: {name}")
