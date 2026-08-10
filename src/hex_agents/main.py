import asyncio
from pathlib import Path
import uuid

from langgraph.types import Command
from psycopg import AsyncConnection
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from hex_agents.factories.workflow_graph_factory import WorkflowGraphFactory
from hex_agents.model.auth_context import AuthContext
from hex_agents.workflow_runner import WorkflowExecutor
from hex_agents.workflows.workflow_loader import load_workflow



async def main():
    BASE_DIR = Path(__file__).resolve().parent

    conn = await AsyncConnection.connect(
        "postgresql://hexlipi:admin@localhost:5432/dhaulagiri",
        autocommit=True,
    )
    checkpointer = AsyncPostgresSaver(conn)
    await checkpointer.setup()

    workflow = load_workflow(
        BASE_DIR / "workflows" / "sample.json"
    )

    workflow_run_id = uuid.uuid4().hex
    workflow_run_id ="bba888139bee46129edd7b23056c2aea"
    workflow_graph = WorkflowGraphFactory(workflow).build()

    config = None;
    if workflow_graph.has_node_class("InterruptNode"):
        print("Workflow has interrupt nodes. Use resume instead of run.")
        config = {
            "configurable": {
                "thread_id": workflow_run_id
            }
        }
    
    compiled_app = workflow_graph.compile(checkpointer=checkpointer)
    context = AuthContext(accessor_id="ad-1", access_token="token")
    # result = await compiled_app.ainvoke(
    #     {
    #         "workflow_id": workflow["id"],
    #         "workflow_run_id": workflow_run_id,
    #         "output":"",       
    #     },
    #     config=config,
    #     context=context
    # )

    result = await compiled_app.ainvoke(Command(
        resume={
            "id": "interrput_1",
            "status": "approved"
        })
        , config=config, context=context)
    print(result);
    print("***************************************************************")
    # final_state = await compiled_app.aget_state(config)
    # print(final_state)
    if result.get("__interrupt__"):
        status = "waiting"
        print("Workflow paused for interrupt. Waiting for user input...")
    else:
        final_state = await compiled_app.aget_state(config)
        print(f"final state: {final_state}")
        if not final_state.next:
            print("Workflow completed successfully.")
            await checkpointer.adelete_thread(
                workflow_run_id
            )
            final_state = await compiled_app.aget_state(config)
            print(f"final state: {final_state}")

    # result = await compiled_app.ainvoke(Command(
    #     resume={
    #         "id": "interrput_1",
    #         "status": "approved"
    #     })
    #     , config=config, context=context)
    # print(result);

    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())