from langchain.agents import create_agent

from hex_agents.graph.state import WorkflowState
from hex_agents.utils.output_parser import extract_text


class AgentNode:

    def __init__(
        self,
        *,
        id: str,
        model,
        prompt: str,
        tools: list,
        inputs: list[str],
    ):

        self.id = id
        self.inputs = inputs

        self.agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=prompt,
        )

    def _debug(self, message: str) -> None:
        print(f"[AgentNode:{self.id}] {message}")

    async def __call__(
        self,
        state: WorkflowState,
    ) -> WorkflowState:

        self._debug(
            f"starting with input output={state.get('output', '')!r}"
        )

        input_data = {
                "messages": [
                    {
                        "role": "user",
                        "content": state["output"]
                    }
                ]
        }

        #
        # Run agent
        #
        self._debug("calling underlying agent")
        response = await self.agent.ainvoke(
            input_data
        )

        output = extract_text(response["messages"][-1])
        self._debug(f"produced output={output!r}")
        state["output"] = output

        self._debug("state output updated")

        return state