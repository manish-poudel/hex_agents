from collections.abc import Awaitable, Callable
from typing import Any
from uuid import uuid4

from langchain.agents import create_agent

from hex_agents.core.state import LLMState


class LLMNode:

    def __init__(
        self,
        *,
        id: str,
        model,
        model_name: str,
        tools: list | None = None,
        system_prompt: str | None = None,
        before_execution: Callable[
            [str, LLMState],
            Awaitable[None],
        ] | None = None,
        after_execution: Callable[
            [str, LLMState],
            Awaitable[None],
        ] | None = None,
    ):
        self.id = id
        self.model = model
        self.model_name = model_name
        self.tools = tools or []
        self.system_prompt = system_prompt

        self.before_execution = before_execution
        self.after_execution = after_execution

        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=self.system_prompt,
        )

    async def _invoke(
        self,
        input_data: Any,
    ):
        return await self.agent.ainvoke(input_data)

    async def _before(
        self,
        state: dict,
    ):
        if self.before_execution:
            await self.before_execution(
                self.id,
                state,
            )

    async def _after(
        self,
        state: dict,
    ):
        if self.after_execution:
            await self.after_execution(
                self.id,
                state,
            )

    def _build_usage(
        self,
        response: Any,
    ) -> dict:
        usage = getattr(
            response,
            "usage_metadata",
            None,
        ) or {}

        return {
            "id": str(uuid4()),
            "node_id": self.id,
            "model_name": self.model_name,
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

    def _usage_state(
        self,
        usage: dict,
    ) -> dict:
        return {
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "total_tokens": usage["total_tokens"],
            "last_usage": usage,
        }