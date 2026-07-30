from langgraph.graph import StateGraph

from hex_agents.graph.state import WorkflowState


class WorkflowGraph:

    def __init__(self):

        self.builder = StateGraph(WorkflowState)

    def add_node(
        self,
        name: str,
        node,
    ):

        self.builder.add_node(
            name,
            node,
        )

    def add_edge(
        self,
        source: str,
        target: str,
    ):

        self.builder.add_edge(
            source,
            target,
        )

    def compile(self, checkpointer=None):

        return self.builder.compile(checkpointer=checkpointer)


    def print_graph(self):

        app = self.compile()

        print("\n" + "=" * 80)
        print("WORKFLOW GRAPH")
        print("=" * 80)
        print(app.get_graph().draw_mermaid())
        print("=" * 80 + "\n")