class PromptBuilder:

    @staticmethod
    def build(
        *,
        prompt: str,
        resources: list[dict],
    ) -> str:

        final_prompt = prompt

        if resources:

            final_prompt += """

========================================
Available Resources
========================================

"""

            for resource in resources:

                final_prompt += f"""
Resource ID:
{resource["id"]}

Type:
{resource["source"]}

Path:
{resource["value"]}

Description:
{resource["description"]}

----------------------------------------
"""

        return final_prompt