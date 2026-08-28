from collections.abc import Awaitable, Callable
from uuid import uuid4

from langchain.agents import create_agent

from hex_agents.graph.state import WorkflowState
from hex_agents.utils.output_parser import extract_text


class AgentNode:

    def __init__(
        self,
        *,
        id: str,
        model,
        model_name: str,
        system_prompt: str,
        user_prompt: str,
        tools: list,
        inputs: list[str],
        before_execution: Callable[
            [str, WorkflowState],
            Awaitable[None],
        ] | None = None,
        after_execution: Callable[
            [str, WorkflowState],
            Awaitable[None],
        ] | None = None,
    ):
        self.id = id
        self.inputs = inputs
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.model_name = model_name

        self.before_execution = before_execution
        self.after_execution = after_execution

        self.agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
        )

    async def __call__(
        self,
        state: WorkflowState,
    ) -> WorkflowState:


        if self.before_execution:
            await self.before_execution(
                self.id,
                state,
            )


        input_data = {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        self.user_prompt
                        + (
                            f" Output from previous node: {state['output']}"
                            if state.get("output")
                            else ""
                        )
                    ),
                }
            ]
        }


        response = await self.agent.ainvoke(input_data)

        ai_message = response["messages"][-1]

        output = extract_text(ai_message)


        usage = ai_message.usage_metadata or {}

        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        last_usage = {
            "id": str(uuid4()),
            "node_id": self.id,
            "model_name": self.model_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        }


        new_state: WorkflowState = {
            **state,
            "output": output,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "last_usage": last_usage,
        }

        if self.after_execution:
            await self.after_execution(
                self.id,
                new_state,
            )

        return {
            "output": output,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "last_usage": last_usage,
        }