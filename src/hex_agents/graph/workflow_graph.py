from langgraph.graph import StateGraph

from hex_agents.graph.state import WorkflowState


class WorkflowGraph:

    def __init__(self):

        self.builder = StateGraph(WorkflowState)
        self._node_class_names: set[str] = set()

    def add_node(
        self,
        name: str,
        node,
    ):

        self._node_class_names.add(node.__class__.__name__)

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

    def has_node_class(self, class_name: str) -> bool:
        """Return True if any graph node is an instance of class_name."""

        if class_name in self._node_class_names:
            return True

        def _matches(obj) -> bool:
            if obj is None:
                return False

            if obj.__class__.__name__ == class_name:
                return True

            # LangGraph may wrap callables; unwrap bound method owners when present.
            call = getattr(obj, "func", None) or getattr(obj, "afunc", None)
            if call is not None:
                owner = getattr(call, "__self__", None)
                if owner is not None and owner.__class__.__name__ == class_name:
                    return True

            return False

        for node_spec in self.builder.nodes.values():
            if _matches(node_spec):
                return True

            for attr in ("runnable", "node", "action", "bound"):
                if _matches(getattr(node_spec, attr, None)):
                    return True

        return False


    def print_graph(self):

        app = self.compile()

