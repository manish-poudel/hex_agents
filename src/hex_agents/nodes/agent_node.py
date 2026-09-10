from langchain.agents import create_agent

from hex_agents.graph.state import WorkflowState
from hex_agents.nodes.llm_node import LLMNode
from hex_agents.utils.output_parser import extract_text


class AgentNode(LLMNode):

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
        before_execution=None,
        after_execution=None,
    ):
        super().__init__(
            id=id,
            model=model,
            model_name=model_name,
            before_execution=before_execution,
            after_execution=after_execution,
        )

        self.inputs = inputs
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

        self.agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
        )

    def _get_invoker(self):
        return self.agent

    async def __call__(
        self,
        state: dict,
    ) -> dict:
     
        await self._before(state)

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

        response = await self._invoke(input_data)

        ai_message = response["messages"][-1]

        output = extract_text(ai_message)

        usage = self._build_usage(ai_message)

        new_state: WorkflowState = {
            **state,
            "output": output,
            **self._usage_state(usage),
        }

        await self._after(new_state)

        return {
            "output": output,
            **self._usage_state(usage),
        }