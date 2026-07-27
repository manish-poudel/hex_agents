from workflow.tools.file_retrieval_tool import FileRetrievalTool


class ToolFactory:

    @staticmethod
    def create(
        definition: dict,
    ):

        tool_type = definition["type"]

        if tool_type == "file_retrieval":

            return FileRetrievalTool(

                path=definition["config"]["path"]

            )

        raise ValueError(
            f"Unknown tool: {tool_type}"
        )