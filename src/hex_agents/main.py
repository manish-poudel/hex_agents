import asyncio
from pathlib import Path
import uuid

from hex_agents.model.auth_context import AuthContext
from hex_agents.workflow_runner import WorkflowExecutor
from hex_agents.workflows.workflow_loader import load_workflow

from langgraph.types import Command


async def main():
    BASE_DIR = Path(__file__).resolve().parent
    workflow = load_workflow(
        BASE_DIR / "workflows" / "resume_email_2.json"
    )
    context = AuthContext(
        accessor_id="ad-1",
        access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkYWM1NjQ0Ny1kY2ZlLTQ0YTctOTNhOC0yMjI0Y2I0ZDZjN2UiLCJleHAiOjE3ODYzMzA0MjMsInR5cGUiOiJhY2Nlc3MifQ.jaUfbtmWeanANSlF3UK3R0UcEaoWGc8fTb_tk9qLg1c",
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
        workflow_run_id="7fc983b930b2473eb2c1bd5b859ea0cf",
    )

    try:
        #run = await workflow_executor.arun()
        run = await workflow_executor.aresume(
            command=Command(resume= {
                "status": "resumed",
            })
        )
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