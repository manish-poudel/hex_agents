from collections.abc import Awaitable, Callable
from operator import add
from typing import Annotated, Any
from uuid import uuid4

from typing_extensions import TypedDict

from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send

from hex_agents.builders.prompt_builder import PromptBuilder
from hex_agents.loaders.prompt_loader import PromptLoader
from hex_agents.registry.action_registry import ActionRegistry
from hex_agents.registry.model_registry import ModelRegistry
from hex_agents.registry.tool_registry import ToolRegistry
from hex_agents.utils.output_parser import extract_text


class MultipleFilesNetState(TypedDict, total=False):
    file_ids: list[str]

    # Current file being processed by this branch.
    file_id: str

    # Results from all file analysis agents.
    outputs: Annotated[list[Any], add]

    # Final result from synthesizer.
    last_message: Any
    output: Any
    token_usage: dict


class MultipleFilesNet:

    def __init__(
        self,
        *,
        node: dict,
        tools: list,
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

        self.tools = tools
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
        state: MultipleFilesNetState,
    ):
        return await self.graph.ainvoke(state)

    def build(self):

        graph = StateGraph(MultipleFilesNetState)

        graph.add_node(
            "process_file",
            self._process_file,
        )

        graph.add_node(
            "synthesizer",
            self._synthesizer,
        )

        graph.add_conditional_edges(
            START,
            self._fan_out,
            ["process_file"],
        )

        graph.add_edge(
            "process_file",
            "synthesizer",
        )

        graph.add_edge(
            "synthesizer",
            END,
        )

        return graph.compile()

    def _fan_out(
        self,
        state: MultipleFilesNetState,
    ):
        return [
            Send(
                "process_file",
                {
                    "file_id": file_id,
                },
            )
            for file_id in state["file_ids"]
        ]

    async def _process_file(
        self,
        state: MultipleFilesNetState,
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

        await self._before(state)

        response = await self.agent.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            f"{self.user_prompt}\n\n"
                            "Analyze the following file:\n\n"
                            f"{file_content}"
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
                "output": output,
                "token_usage": token_usage,
            }
        )

        return {
            "outputs": [
                {
                    "file_id": file_id,
                    "output": output,
                }
            ],
        }

    async def _synthesizer(
        self,
        state: MultipleFilesNetState,
    ):

        await self._before(state)

        synthesis_prompt = (
            f"{self.user_prompt}\n\n"
            "You are now synthesizing the results of multiple "
            "file analyses.\n\n"
            "Here are the results from the individual file "
            "analysis agents:\n\n"
            f"{state['outputs']}\n\n"
            "Synthesize these results into one coherent final "
            "answer."
        )

        response = await self.agent.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content=synthesis_prompt,
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