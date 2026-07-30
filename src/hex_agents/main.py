import asyncio
from pathlib import Path
from pprint import pprint

from langgraph.types import Command
from psycopg import AsyncConnection
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from hex_agents.compiler.workflow_compiler import WorkflowCompiler
from hex_agents.model.auth_context import AuthContext
from hex_agents.workflows.workflow_loader import load_workflow


async def main():
    BASE_DIR = Path(__file__).resolve().parent

    # Create async PostgreSQL connection
    conn = await AsyncConnection.connect(
        "postgresql://hexlipi:admin@localhost:5432/dhaulagiri",
        autocommit=True,
    )

    # Create async checkpointer
    checkpointer = AsyncPostgresSaver(conn)

    # Create LangGraph checkpoint tables (run once)
    await checkpointer.setup()

    workflow = load_workflow(
        BASE_DIR / "workflows" / "sample.json"
    )

    compiler = WorkflowCompiler(workflow)

    workflow_graph = compiler.compile()

    app = workflow_graph.compile(
        checkpointer=checkpointer
    )

    config = {
        "configurable": {
            "thread_id": workflow["id"]
        }
    }

    result = await app.ainvoke(
        {
            "messages": [],
            "outputs": {},
            "used_tools": {},
            "interrupts": [],
        },
        config=config,
        context=AuthContext(
            accessor_id="ad-1",
            access_token="YOUR_ACCESS_TOKEN",
        ),
    )


#     result = await app.ainvoke(
#     Command(
#         resume={
#             "id": "interrput_1",
#             "status": "approved",
#         }
#     ),
#     config=config,
# )

    state = await app.aget_state(config)

    print(state.values["final_output"])

    # pprint(result)

    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())