from operator import add
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


# ============================================================
# MAIN WORKFLOW STATE
# ============================================================

class WorkflowState(TypedDict):
    file_ids: list[str]

    # Results from all parallel file workers are collected here.
    outputs: Annotated[list, add]


# ============================================================
# FILE WORKER STATE
# ============================================================

class FileState(TypedDict):
    # This state belongs to ONE fan-out branch.
    file_id: str

    # Also belongs only to this branch.
    file_content: str

    # This is the value that gets returned/shared with the
    # parent WorkflowState.
    outputs: Annotated[list, add]


# ============================================================
# FAKE DATABASE
# ============================================================

FILES = {
    "file_1": "This is the content of file one.",
    "file_2": "This is the content of file two.",
    "file_3": "This is the content of file three.",
}


# ============================================================
# GET FILE
# ============================================================

def get_file(state: FileState):

    file_id = state["file_id"]

    print(f"GET FILE: {file_id}")

    content = FILES.get(file_id)

    if content is None:
        raise ValueError(
            f"File not found: {file_id}"
        )

    return {
        "file_content": content,
    }


# ============================================================
# AGENT
# ============================================================

def agent(state: FileState):

    file_id = state["file_id"]
    content = state["file_content"]

    print(f"AGENT: analyzing {file_id}")

    result = {
        "file_id": file_id,
        "analysis": f"Analysis of {content}",
    }

    return {
        "outputs": [result],
    }


# ============================================================
# FILE WORKER SUBGRAPH
# ============================================================

file_worker_builder = StateGraph(FileState)

file_worker_builder.add_node(
    "get_file",
    get_file,
)

file_worker_builder.add_node(
    "agent",
    agent,
)

file_worker_builder.add_edge(
    START,
    "get_file",
)

file_worker_builder.add_edge(
    "get_file",
    "agent",
)

file_worker_builder.add_edge(
    "agent",
    END,
)

file_worker = file_worker_builder.compile()


# ============================================================
# FAN OUT
# ============================================================

def fan_out(state: WorkflowState):

    return [
        Send(
            "file_worker",
            {
                "file_id": file_id,
            },
        )
        for file_id in state["file_ids"]
    ]


# ============================================================
# REDUCER
# ============================================================

def reducer(state: WorkflowState):

    print("\nREDUCER")

    for output in state["outputs"]:
        print(output)

    return {
        "outputs": state["outputs"],
    }


# ============================================================
# MAIN WORKFLOW
# ============================================================

workflow_builder = StateGraph(
    WorkflowState
)

workflow_builder.add_node(
    "file_worker",
    file_worker,
)

workflow_builder.add_node(
    "reducer",
    reducer,
)


# START → fan out
workflow_builder.add_conditional_edges(
    START,
    fan_out,
)


# Every file worker eventually goes to reducer.
workflow_builder.add_edge(
    "file_worker",
    "reducer",
)


workflow_builder.add_edge(
    "reducer",
    END,
)


graph = workflow_builder.compile()


# ============================================================
# RUN
# ============================================================

result = graph.invoke(
    {
        "file_ids": [
            "file_1",
            "file_2",
            "file_3",
        ],
        "outputs": [],
    }
)


print("\nFINAL RESULT")

for output in result["outputs"]:
    print(output)