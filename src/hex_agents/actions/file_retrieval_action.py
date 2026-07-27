from hex_agents.graph.state import WorkflowState
from pypdf import PdfReader


def get_file(
    id: str,
    path: str,
):

    def action(
        state: WorkflowState,
    ) -> WorkflowState:

        reader = PdfReader(path)

        content = ""

        for page in reader.pages:
            content += page.extract_text() or ""


        state["outputs"][id] = content

        return state


    return action