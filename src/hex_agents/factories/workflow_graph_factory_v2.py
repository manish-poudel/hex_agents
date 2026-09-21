from collections.abc import Awaitable, Callable

from langgraph.graph import START, END

from hex_agents.factories.mutiple_file_net import MultipleFilesNet
from hex_agents.builders.prompt_builder import PromptBuilder
from hex_agents.graph.workflow_graph import WorkflowGraph
from hex_agents.loaders.prompt_loader import PromptLoader
from hex_agents.nodes.agent_node import AgentNode
from hex_agents.nodes.async_action_node import AsyncActionNode
from hex_agents.nodes.interrupt_node import InterruptNode
from hex_agents.registry.action_registry import ActionRegistry
from hex_agents.registry.model_registry import ModelRegistry
from hex_agents.registry.tool_registry import ToolRegistry


class WorkflowGraphFactoryV2:

    def __init__(
        self,
        workflow: dict,
        tool_registry: ToolRegistry,
        action_registry: ActionRegistry,
        model_registry: ModelRegistry,
        state_schema,
        before_agent_execution: Callable[
            [str, dict],
            Awaitable[None],
        ] | None = None,
        after_agent_execution: Callable[
            [str, dict],
            Awaitable[None],
        ] | None = None,
    ):
        self.workflow = workflow
        self.tool_registry = tool_registry
        self.action_registry = action_registry
        self.model_registry = model_registry

        self.before_agent_execution = before_agent_execution
        self.after_agent_execution = after_agent_execution
        self.state_schema = state_schema

    def build(self):

        graph = WorkflowGraph(
            state_schema=self.state_schema
        )

        for node in self.workflow["nodes"]:

            #
            # ACTION
            #

            if node["type"] == "action":

                graph.add_node(
                    node["id"],
                    AsyncActionNode(
                        action=self.action_registry.create(node)
                    ),
                )

            #
            # AGENT
            #

            elif node["type"] == "agent":

                file_uploads = node.get("file_uploads") or []
                file_ids = [
                    item["id"]
                    for item in file_uploads
                    if isinstance(item, dict) and item.get("id")
                ] or (node.get("file_ids") or [])

                #
                # Multiple files
                #
                if file_ids:
                    multiple_files_net = MultipleFilesNet(
                        node=node,
                        tool_registry=self.tool_registry,
                        action_registry=self.action_registry,
                        model_registry=self.model_registry,
                        before_agent_execution=self.before_agent_execution,
                        after_agent_execution=self.after_agent_execution,
                    )
                    async def run_multiple_files(
                        state,
                        net=multiple_files_net,
                        file_ids=file_ids,
                    ):
                        result = await net.invoke(
                            {
                                "file_ids": file_ids,
                            }
                        )

                        return {
                            "output": result["output"],
                        }

                    graph.add_node(
                        node["id"],
                        run_multiple_files,
                    )

                #
                # Normal single-input agent
                #

                else:

                    tools = []

                    if node["resources"] is not None:

                        for resource in node["resources"]:

                            if resource["type"] == "skill":

                                handler = self.tool_registry.get_tool(
                                    "storage",
                                    "storage.access.file",
                                ).handler()

                                tools.append(handler)

                    if node["services"] is not None:

                        for service in node["services"]:

                            for tool in self.tool_registry.get_tools(
                                service
                            ):
                                tools.append(
                                    tool.handler()
                                )

                    agent_node = AgentNode(
                        id=node["id"],
                        model=self.model_registry.get_model(
                            provider=node["model"]["provider"],
                            model_name=node["model"]["name"],
                        ),
                        model_provider=node["model"]["provider"],
                        model_name=node["model"]["name"],
                        user_prompt=PromptLoader.load(
                            node["prompt"]
                        ),
                        system_prompt=PromptBuilder.build(
                            resources=node["resources"]
                        ),
                        tools=tools,
                        before_execution=self.before_agent_execution,
                        after_execution=self.after_agent_execution,
                    )

                    graph.add_node(
                        node["id"],
                        agent_node,
                    )

            #
            # INTERRUPT
            #

            elif node["type"] == "interrupt":

                graph.add_node(
                    node["id"],
                    InterruptNode(data=node),
                )

        #
        # Fallback:
        # if workflow has nodes but no edges,
        # run first node only.
        #

        if self.workflow["nodes"] and not self.workflow["edges"]:

            first_node_id = self.workflow["nodes"][0]["id"]

            graph.add_edge(
                START,
                first_node_id,
            )

            graph.add_edge(
                first_node_id,
                END,
            )

            return graph

        #
        # Create workflow edges
        #

        for edge in self.workflow["edges"]:

            graph.add_edge(
                edge["from"],
                edge["to"],
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
                    node["id"],
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
                    END,
                )

        return graph