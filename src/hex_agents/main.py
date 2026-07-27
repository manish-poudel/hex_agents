import asyncio
from pathlib import Path
from pprint import pprint

from hex_agents.compiler.workflow_compiler import WorkflowCompiler
from hex_agents.model.auth_context import AuthContext
from hex_agents.workflows.workflow_loader import load_workflow


async def main():
    BASE_DIR = Path(__file__).resolve().parent

    workflow = load_workflow(
        BASE_DIR / "workflows" / "resume_email.json"
    )

    compiler = WorkflowCompiler(workflow)
    workflow_graph = compiler.compile()
    workflow_graph.print_graph()

    app = workflow_graph.compile()

    result = await app.ainvoke(
        {
            "messages": [],
            "outputs": {},
            "used_tools": {},
        },
        context=AuthContext(
            accessor_id="ad-1",
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4YWIzZGNiZS0xNWRiLTRjYTMtYTNiOS0zMzIxNDkxNjJmMTEiLCJleHAiOjE3ODUxNjc4NTksInR5cGUiOiJhY2Nlc3MifQ.bnZkqaSqUGWWhxwtUeAZpcSFGfbIVrVQdejCkSlpPf4",
        ),
    )

    pprint(result)


if __name__ == "__main__":
    asyncio.run(main())