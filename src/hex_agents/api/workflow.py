from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
import traceback

from hex_agents.compiler.workflow_compiler import WorkflowCompiler

router = APIRouter()


@router.post("/execute")
async def execute_workflow(body: dict = Body(...)):
    try:
        print(body);
        compiler = WorkflowCompiler(body)

        workflow_graph = compiler.compile()

        app = workflow_graph.compile()

        result = app.invoke(
            {
                "messages": [],
                "outputs": {},
                "used_tools": {},
            }
        )

        return result

    except Exception:
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "error": traceback.format_exc()
            },
        )