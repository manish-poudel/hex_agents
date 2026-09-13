from typing import Any, Awaitable, Callable
from uuid import uuid4

from langchain.agents import create_agent
from langchain.messages import HumanMessage

from hex_agents.utils.output_parser import extract_text


class AgentNode:

    def __init__(
        self,
        *,
        id: str,
        model,
        model_provider:str,
        model_name: str,
        system_prompt: str,
        user_prompt: str,
        tools: list,
        inputs: list[str],
        before_execution: Callable[[str, dict[str, Any]], Awaitable[None]] | None = None,
        after_execution: Callable[[str, dict[str, Any]], Awaitable[None]] | None = None,
    ):
        self.id = id
        self.model = model
        self.model_provider = model_provider
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.tools = tools
        self.inputs = inputs

        self.before_execution = before_execution
        self.after_execution = after_execution

        self.agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
        )

    async def _before(self, state: dict[str, Any]):
        if self.before_execution:
            await self.before_execution(self.id, state)

    async def _after(self, state: dict[str, Any]):
        if self.after_execution:
            await self.after_execution(self.id, state)

    async def _invoke(self, input_data: Any):
        return await self.agent.ainvoke(input_data)
    
    def _usage_state(self, usage: dict) -> dict:
        return {
            "id": str(uuid4()),
            "node_id": self.id,
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "last_usage": usage,
        }

    async def __call__(
        self,
        state: dict[str, Any],
    ) -> dict[str, Any]:

        await self._before(state)

        messages = [state.get("last_message")] if state.get("last_message") else []

        input_data = {
            "messages":messages + [HumanMessage(content=self.user_prompt)]
        }

        response = await self._invoke(input_data)

        ai_message = response["messages"][-1]

        output = extract_text(ai_message)

        usage = getattr(ai_message, "usage_metadata", None) or {}
        
        state_update = {
            "last_message": ai_message,
            "output": output,
            "token_usage": self._usage_state(usage),
        }
        
        print(state_update)

        await self._after({
            **state,
            **state_update,
        })

        return state_update