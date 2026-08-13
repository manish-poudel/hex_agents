from langgraph.graph import START, END

from hex_agents.agents.interrupt_node import InterruptNode
from hex_agents.graph.workflow_graph import WorkflowGraph
from hex_agents.agents.action_node import ActionNode
from hex_agents.registry.v2.action_registry import ActionRegistry
from hex_agents.factories.agent_factory import AgentFactory


class WorkflowGraphFactory:

    def __init__(
        self,
        workflow: dict,
        action_registry: ActionRegistry,
    ):
        self.workflow = workflow
        self.action_registry = action_registry

    def build(self):

        graph = WorkflowGraph()

        #
        # Build inputs map
        #

        inputs = {}

        for edge in self.workflow["edges"]:

            if edge["to"] not in inputs:

                inputs[edge["to"]] = []

            inputs[edge["to"]].append(
                edge["from"]
            )

        #
        # Create Nodes
        #

        for node in self.workflow["nodes"]:

            if node["type"] == "action":

                graph.add_node(

                    node["id"],

                    self.action_registry.create(node)

                )

            elif node["type"] == "agent":

                graph.add_node(

                    node["id"],

                    AgentFactory.create(

                        agent=node,

                        inputs=inputs.get(
                            node["id"],
                            []
                        )

                    )

                )

            elif node["type"] == "interrupt":
                graph.add_node(node["id"], InterruptNode(
                    data = node
                ))

        # Fallback: if workflow has nodes but no edges, run first node only.
        if self.workflow["nodes"] and not self.workflow["edges"]:
            first_node_id = self.workflow["nodes"][0]["id"]
            graph.add_edge(START, first_node_id)
            graph.add_edge(first_node_id, END)
            return graph

        #
        # Create workflow edges
        #

        for edge in self.workflow["edges"]:

            graph.add_edge(

                edge["from"],

                edge["to"]

            )

        #
        # Connect START
        #

        targets = set()

        for edge in self.workflow["edges"]:

            targets.add(edge["to"])

        for node in self.workflow["nodes"]:

            if node["id"] not in targets:

                graph.add_edge(
                    START,
                    node["id"]
                )

        #
        # Connect END
        #

        sources = set()

        for edge in self.workflow["edges"]:

            sources.add(edge["from"])

        for node in self.workflow["nodes"]:

            if node["id"] not in sources:

                graph.add_edge(
                    node["id"],
                    END
                )

        return graph