import asyncio

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.auth import BearerAuth
from langchain_openai import ChatOpenAI


async def run_test():
    # transport = StreamableHttpTransport(
    #     url="http://localhost:8000/mcp",
    #     auth=BearerAuth("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4YWIzZGNiZS0xNWRiLTRjYTMtYTNiOS0zMzIxNDkxNjJmMTEiLCJleHAiOjE3ODUxNDc2MjcsInR5cGUiOiJhY2Nlc3MifQ.jg7jkqUuMfVZaYpK0Xtoo8diY1_0sv_ZNdeD4g9WP4Q"),
    # )

    # async with Client(transport) as client:
    #     tools = await client.list_tools()
    #     result = await client.call_tool(
    #         "fetch_file",
    #         arguments={"file_id": "605bbfa7-2d83-48c2-97a4-50c6205f9982"},
    #     )
    
    model = ChatOpenAI(
                model="gpt-5.6-luna",
                api_key = "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"
            )
    print(model.invoke(messages = [
    (
        "system",
        "You are a helpful translator. Translate the user sentence to French.",
    ),
    ("human", "I love programming."),
    ]
))




asyncio.run(run_test())