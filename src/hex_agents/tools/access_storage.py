from pathlib import Path
from urllib import response

from langchain.tools import ToolRuntime
from langchain_core.tools import tool

from hex_agents.actions.storage_action import get_storage_node
from hex_agents.model.auth_context import AuthContext
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.auth import BearerAuth
import base64

def create_storage_tool():
        
    @tool
    async def get_storage_node(
        node_id: str,
        runtime: ToolRuntime[AuthContext],
    ) -> dict:
        """Fetches a storage file from MCP."""
        
        transport = StreamableHttpTransport(
            url="http://localhost:8000/mcp",
            auth=BearerAuth(runtime.context.access_token),
        )

        async with Client(transport) as client:
            result = await client.call_tool(
                "fetch_storage_node",
                arguments={"node_id": node_id},
            )
        
        result.data["bytes"] = base64.b64decode(result.data["bytes"])
        return result.data

    
    return {
        "get_storage_node": get_storage_node,
    }
