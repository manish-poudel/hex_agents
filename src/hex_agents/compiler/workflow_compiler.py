from langgraph.graph import START, END

from hex_agents.agents.interrupt_node import InterruptNode
from hex_agents.graph.workflow_graph import WorkflowGraph
from hex_agents.agents.action_node import ActionNode
from hex_agents.actions.file_retrieval_action import get_file
from hex_agents.agents.agent_node import AgentNode
from hex_agents.registry.model_registry import ModelRegistry
from hex_agents.registry.action_registry import ActionRegistry
from hex_agents.factories.agent_factory import AgentFactory


class WorkflowCompiler:

    def __init__(
        self,
        workflow: dict,
    ):
        self.workflow = workflow

    def compile(self):

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

                    ActionRegistry.create(node)

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
                    data = node["data"]
                ))

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