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

    async def __call__(
        self,
        state: WorkflowState,
    ) -> WorkflowState:

  
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
        response = await self.agent.ainvoke(
            input_data
        )

        output = extract_text(response["messages"][-1])
        state["output"] = output

        return state