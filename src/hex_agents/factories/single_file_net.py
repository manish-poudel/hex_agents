from collections.abc import Awaitable, Callable
from typing import Any
from uuid import uuid4

from typing_extensions import TypedDict

from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.graph import START, END, StateGraph

from hex_agents.builders.prompt_builder import PromptBuilder
from hex_agents.loaders.prompt_loader import PromptLoader
from hex_agents.registry.action_registry import ActionRegistry
from hex_agents.registry.model_registry import ModelRegistry
from hex_agents.registry.tool_registry import ToolRegistry
from hex_agents.utils.output_parser import extract_text


class SingleFileNetState(TypedDict, total=False):
    file_id: str
    file_content: str
    last_message: Any
    output: Any
    token_usage: dict


class SingleFileNet:

    def __init__(
        self,
        *,
        node: dict,
        tool_registry: ToolRegistry,
        action_registry: ActionRegistry,
        model_registry: ModelRegistry,
        before_agent_execution: Callable[
            [str, dict[str, Any]],
            Awaitable[None],
        ] | None = None,
        after_agent_execution: Callable[
            [str, dict[str, Any]],
            Awaitable[None],
        ] | None = None,
    ):
        self.node = node

        self.tool_registry = tool_registry
        self.action_registry = action_registry
        self.model_registry = model_registry

        self.before_agent_execution = before_agent_execution
        self.after_agent_execution = after_agent_execution

        self.agent_id = node["id"]

        self.model_provider = node["model"]["provider"]
        self.model_name = node["model"]["name"]

        self.model = self.model_registry.get_model(
            provider=self.model_provider,
            model_name=self.model_name,
        )

        self.tools = self._create_tools()

        self.system_prompt = PromptBuilder.build(
            resources=node.get("resources") or [],
        )

        self.user_prompt = PromptLoader.load(
            node["prompt"],
        )

        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=self.system_prompt,
        )

        self.graph = self.build()

    async def invoke(
        self,
        state: SingleFileNetState,
    ):
        return await self.graph.ainvoke(state)

    def build(self):

        graph = StateGraph(SingleFileNetState)

        graph.add_node(
            "select_file",
            self._select_file,
        )

        graph.add_node(
            "analyze_file",
            self._analyze_file,
        )

        graph.add_edge(
            START,
            "select_file",
        )

        graph.add_edge(
            "select_file",
            "analyze_file",
        )

        graph.add_edge(
            "analyze_file",
            END,
        )

        return graph.compile()

    async def _select_file(
        self,
        state: SingleFileNetState,
    ):

        file_id = state["file_id"]

        action = self.action_registry.create(
            {
                "type": "action",
                "kind": "access_storage_node",
                "file_id": file_id,
            }
        )

        file_content = await action()

        return {
            "file_content": file_content,
        }

    async def _analyze_file(
        self,
        state: SingleFileNetState,
    ):

        await self._before(state)

        response = await self.agent.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            f"{self.user_prompt}\n\n"
                            "Analyze the following file:\n\n"
                            f"{state['file_content']}"
                        )
                    )
                ]
            }
        )

        ai_message = response["messages"][-1]

        output = extract_text(ai_message)

        usage = getattr(
            ai_message,
            "usage_metadata",
            None,
        ) or {}

        token_usage = self._usage_state(usage)

        await self._after(
            {
                **state,
                "last_message": ai_message,
                "output": output,
                "token_usage": token_usage,
            }
        )

        return {
            "last_message": ai_message,
            "output": output,
            "token_usage": token_usage,
        }

    def _create_tools(self):

        tools = []

        resources = self.node.get("resources") or []
        services = self.node.get("services") or []

        for resource in resources:

            if resource["type"] == "skill":

                handler = self.tool_registry.get_tool(
                    "storage",
                    "storage.access.file",
                ).handler()

                tools.append(handler)

        for service in services:

            for tool in self.tool_registry.get_tools(service):
                tools.append(
                    tool.handler()
                )

        return tools

    def _usage_state(
        self,
        usage: dict,
    ) -> dict:

        return {
            "id": str(uuid4()),
            "node_id": self.agent_id,
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "last_usage": usage,
        }

    async def _before(
        self,
        state: dict[str, Any],
    ):

        if self.before_agent_execution:

            await self.before_agent_execution(
                self.agent_id,
                state,
            )

    async def _after(
        self,
        state: dict[str, Any],
    ):

        if self.after_agent_execution:

            await self.after_agent_execution(
                self.agent_id,
                state,
            )