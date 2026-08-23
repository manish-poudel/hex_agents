class PromptBuilder:

    @staticmethod
    def build(
        *,
        resources: list[dict],
    ) -> str:

        final_prompt = """You are an assistant working inside a MyndBase workflow or chat.

Analyze the input provided by the user.
Be concise and factual.
Use the available tools when necessary. If you don't know the answer, say "I don't know". Don't try to use tool with made up param.
Param for tool should be sent by user in prompt text. You can't make up param for tool
Do not invent information.
"""

        if resources:

            final_prompt += """

========================================
Available Resources
========================================

"""

            for resource in resources:

                final_prompt += f"""
id:
{resource["id"]}

Type:
{resource["source"]}

value:
{resource["value"]}

Description:
{resource["description"]}

----------------------------------------
"""

        return final_prompt
