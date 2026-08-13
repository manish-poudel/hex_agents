import asyncio
from pathlib import Path
import uuid

from hex_agents.actions.storage_action import get_storage_node
from hex_agents.model.auth_context import AuthContext

from hex_agents.registry.v2.tool_registry import ToolRegistry
from hex_agents.runners.workflow_runner import WorkflowExecutor
from hex_agents.registry.v2.action_registry import ActionRegistry, create_storage_action
from hex_agents.tools.access_file import create_access_file_storage
from hex_agents.workflows.workflow_loader import load_workflow

from langgraph.types import Command


async def main():
    BASE_DIR = Path(__file__).resolve().parent
    workflow = load_workflow(
        BASE_DIR / "workflows" / "sample_3.json"
    )
    context = AuthContext(
        accessor_id="ad-1",
        access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NmUwODE3Ny1lMTJkLTRkZDgtYWZhYi04ZGUzYzNiYzNhYjIiLCJleHAiOjE3ODY3MDczNTEsInR5cGUiOiJhY2Nlc3MifQ._6-WBxCzbQtWpLB1PRgsiN2VY5ddzM8llQ7tg0x7Hw4",
    )

    worflow_run_id = uuid.uuid4().hex
    workflow_executor = WorkflowExecutor(
        workflow=workflow,
        context=context,
        database_url=(
            "postgresql://hexlipi:admin"
            "@localhost:5432/dhaulagiri"
        ),
        workflow_id=str(workflow["id"]),
        workflow_run_id=worflow_run_id,
        tool_registry=ToolRegistry(
            tools={
                "access_file_storage": create_access_file_storage()
            }
        )
    )

    try:
        run = await workflow_executor.arun()
        # run = await workflow_executor.aresume(
        #     command=Command(resume= {
        #         "status": "resumed",
        #     })
        # )
        print(run)
        print(
            "***************************************************************"
        )
        result = run["result"]
        if result.get("__interrupt__"):
            print(
                "Workflow paused for interrupt. "
                "Waiting for user input..."
            )
            final_state = await workflow_executor.aget_state()
            print("FINAL STATE")
            print(final_state)
        

        else:
            final_state = await workflow_executor.aget_state()

            print("FINAL STATE")
            print(final_state)

            if not final_state.next:

                print(
                    "Workflow completed successfully."
                )

                # Remove checkpoint data.
                await workflow_executor.acleanup()

                print(
                    "Workflow checkpoint cleaned up."
                )

    finally:
        await workflow_executor.aclose()


if __name__ == "__main__":
    asyncio.run(main())