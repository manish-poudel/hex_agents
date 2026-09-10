


from build.lib.hex_agents.core.workflow_creator_state import WorkflowCreatorState
from build.lib.hex_agents.nodes.llm_node import LLMNode


class PlannerNode(LLMNode):

    def __init__(
        self,
        *,
        id: str,
        model,
        model_name: str,
        system_prompt: str,
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

        self.system_prompt = system_prompt

    async def __call__(
        self,
        state: WorkflowCreatorState,
    ) -> WorkflowCreatorState:

        await self._before(state)

        input_data = {
            "messages": [
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {
                    "role": "user",
                    "content": state["user_request"],
                },
            ]
        }

        response = await self._invoke(input_data)

        usage = self._build_usage(response)

        new_state: WorkflowCreatorState = {
            **state,
            "workflow": response.content,
            **self._usage_state(usage),
        }

        await self._after(new_state)

        return new_state