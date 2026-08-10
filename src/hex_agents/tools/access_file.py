from pathlib import Path

from langchain.tools import ToolRuntime
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader

from hex_agents.actions.file_retrieval_action import get_file_mcp
from hex_agents.model.auth_context import AuthContext
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.auth import BearerAuth
import base64
from io import BytesIO
from pypdf import PdfReader


def create_access_file_tool():

    @tool
    def access_file(filename: str) -> str:
        """
        Read a document file.
        Supports PDF and TXT files.
        """

        file_path = Path(filename)

        if not file_path.exists():
            print("file not found")
            print(file_path)
            return f"File not found: {file_path}"


        extension = file_path.suffix.lower()


        if extension == ".pdf":

            loader = PyPDFLoader(str(file_path))

            documents = loader.load()

            return "\n\n".join(
                doc.page_content
                for doc in documents
            )


        elif extension == ".txt":
            print("yuppy");

            text = file_path.read_text(
                encoding="utf-8"
            )
            print(text)
            return text


        else:
            return f"Unsupported file type: {extension}"


    return access_file

def create_access_file_storage():

    @tool
    async def access_file_storage(
        value: str,
        runtime: ToolRuntime[AuthContext],
    ) -> str:
        """Read a document file from MCP."""
        print("file id", value);
        transport = StreamableHttpTransport(
            url="http://localhost:8000/mcp",
            auth=BearerAuth(runtime.context.access_token),
        )

        async with Client(transport) as client:
            result = await client.call_tool(
                "fetch_file",
                arguments={"file_id": value},
            )
        
        text_bytes = base64.b64decode(result.data["data"]["bytes"])
        text = text_bytes.decode("utf-8")
        return text

    return access_file_storage