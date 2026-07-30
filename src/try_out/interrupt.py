from typing import TypedDict

# Graph classes
from langgraph.graph import StateGraph, START, END

# interrupt() pauses the graph
# Command() resumes the graph
from langgraph.types import interrupt, Command

# Simple in-memory checkpoint storage
from langgraph.checkpoint.memory import InMemorySaver


# ---------------------------------------------------
# State
# ---------------------------------------------------
# Everything inside this class is automatically
# saved whenever the graph reaches an interrupt().
#
# Think of it like the memory of your workflow.
# ---------------------------------------------------
class State(TypedDict):
    filename: str
    approved: str
    result: str


# ---------------------------------------------------
# Node 1
# ---------------------------------------------------
# This node asks the human for approval.
#
# interrupt() pauses execution.
#
# The graph will stop here until someone calls
# graph.invoke(Command(resume=...), ...)
# ---------------------------------------------------
def approval_node(state: State):

    print("Approval node started")

    approval = interrupt(
        {
            "title": "Delete File",
            "message": f"Do you want to delete '{state['filename']}'?"
        }
    )

    # Everything BELOW interrupt()
    # executes ONLY after resume()

    print("Workflow resumed")

    return {
        "approved": approval
    }


# ---------------------------------------------------
# Node 2
# ---------------------------------------------------
# Executes only after approval_node finishes.
# ---------------------------------------------------
def delete_node(state: State):

    if state["approved"].lower() != "yes":

        return {
            "result": "Deletion cancelled."
        }

    # Imagine deleting a real file here.

    print(f"Deleting {state['filename']}")

    return {
        "result": f"{state['filename']} deleted successfully."
    }


# ---------------------------------------------------
# Build graph
# ---------------------------------------------------
builder = StateGraph(State)

builder.add_node("approval", approval_node)
builder.add_node("delete", delete_node)

builder.add_edge(START, "approval")
builder.add_edge("approval", "delete")
builder.add_edge("delete", END)


# ---------------------------------------------------
# Checkpointer
# ---------------------------------------------------
# Required for interrupt().
#
# Without a checkpointer,
# LangGraph cannot remember where it stopped.
# ---------------------------------------------------
graph = builder.compile(
    checkpointer=InMemorySaver()
)


# ---------------------------------------------------
# Thread ID
# ---------------------------------------------------
# Every workflow execution has its own ID.
#
# Later we MUST use the SAME thread_id
# to continue this workflow.
# ---------------------------------------------------
config = {
    "configurable": {
        "thread_id": "workflow-001"
    }
}


# ---------------------------------------------------
# # FIRST RUN
# # ---------------------------------------------------
# print("\n----- FIRST INVOKE -----\n")

result = graph.invoke(
    {
        "filename": "secret.txt"
    },
    config=config
)

print("\n----- RESUME -----\n")

result = graph.invoke(
    Command(
        resume="yes"
    ),
    config=config
)

print(result)

print(result)