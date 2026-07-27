from pathlib import Path

from workflows.workflow_loader import load_workflow
from compiler.workflow_compiler import WorkflowCompiler

BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)

workflow = load_workflow(
    BASE_DIR / "workflows" / "resume_email.json"
)

compiler = WorkflowCompiler(workflow)
workflow_graph = compiler.compile()
workflow_graph.print_graph()
app = workflow_graph.compile()

result = app.invoke(
    {
        "messages": [],
        "outputs": {},
        "used_tools": {}
    }
)

from pprint import pprint
pprint(result)