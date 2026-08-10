from hex_agents.graph.state import WorkflowState
from pypdf import PdfReader

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.auth import BearerAuth


def get_file(
    id: str,
    path: str,
):

    def action(
        state: WorkflowState,
    ) -> WorkflowState:

        reader = PdfReader(path)

        content = ""

        for page in reader.pages:
            content += page.extract_text() or ""


        #s#tate["outputs"][id] = content
        state["output"] = content

        return state


    return action

async def get_file_mcp(url, id, file_id, access_token):

    async def action(state):

        transport = StreamableHttpTransport(
            url=url,
            auth=BearerAuth(access_token),
        )

        print("accessign file mcp")

        async with Client(transport) as client:
            result = await client.call_tool(
                "fetch_file",
                arguments={"file_id": file_id},
            )

        print("ok file get")
        print(result);
        return state;

        state["outputs"][id] = result.data["data"]

        return state

    return action