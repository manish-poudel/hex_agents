import base64

from fastmcp import Client
from fastmcp.client.auth import BearerAuth
from fastmcp.client.transports import StreamableHttpTransport


class StorageService:

    def __init__(self, access_token: str):
        self.access_token = access_token

    async def get_file(self, node_id: str) -> dict:

        transport = StreamableHttpTransport(
            url="http://localhost:8000/mcp",
            auth=BearerAuth(self.access_token),
        )

        async with Client(transport) as client:
            result = await client.call_tool(
                "fetch_storage_node",
                arguments={
                    "node_id": node_id,
                },
            )

        result.data["bytes"] = base64.b64decode(
            result.data["bytes"]
        )

        return result.data