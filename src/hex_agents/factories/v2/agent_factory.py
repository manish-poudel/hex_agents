from hex_agents.agents.agent_node import AgentNode
from hex_agents.registry.model_registry import ModelRegistry
from hex_agents.registry.tool_registry import ToolRegistry
from hex_agents.loaders.prompt_loader import PromptLoader
from hex_agents.loaders.resource_loaders import ResourceLoader
from hex_agents.builders.prompt_builder import PromptBuilder



class AgentFactory:

    @staticmethod
    def create(
        *,
        agent: dict,
        inputs: list[str],
        tools: list = None,
    ):

        #
        # Model
        #
        model = ModelRegistry.create(
            agent["model"]
        )

        #
        # Prompt
        #
        prompt = PromptLoader.load(
            agent["prompt"]
        )

        system_prompt = PromptBuilder.build(

    prompt=prompt,

    resources=agent["resources"]

)
    
        return AgentNode(

            id=agent["id"],

            model=model,

            prompt=system_prompt,

            tools=tools,

            inputs=inputs

        )