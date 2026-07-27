from hex_agents.tools.access_file import create_access_file_storage, create_access_file_tool


class ToolRegistry:

    @staticmethod
    def create(tool_json):

        name = tool_json["name"]

        if name == "access_file":

            return create_access_file_tool()
            

        if name == "access_file_storage":
            return  create_access_file_storage()

        raise Exception(
            f"Unknown tool: {name}"
        )