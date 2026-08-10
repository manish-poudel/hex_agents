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

        #
        # First node in workflow
        #
        if len(self.inputs) == 0:

            input_data = {
                "messages": state["messages"]
            }

        #
        # Build context from previous node outputs
        #
        else:

            context = ""

            for node_id in self.inputs:

                output = state["outputs"].get(node_id)

                context += f"""
Node: {node_id}

{output}

----------------------------------------
"""

            input_data = {
                "messages": [
                    {
                        "role": "user",
                        "content": context
                    }
                ]
            }

        #
        # Run agent
        #
        response = await self.agent.ainvoke(
            input_data
        )

        used_resources = []

        for message in response["messages"]:

            if hasattr(message, "tool_calls"):

                for tool in message.tool_calls:

                    if tool["name"] == "access_file":

                        used_resources.append(
                            tool["args"]["filename"]
                        )
                    if tool["name"] == "access_file_storage":
                   
                        print("tool was used", tool["args"])
                        used_resources.append(
                                                tool["args"]["value"]
                                            )

        #
        # Final response from LLM
        #
        output = extract_text(response["messages"][-1])

        #
        # Save into workflow state
        #
        #state["outputs"][self.id] = output
        state["output"] = output
        #state["used_tools"][self.id] = used_resources
        # state["messages"] = output

        return state