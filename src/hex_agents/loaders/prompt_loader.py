from pathlib import Path


class PromptLoader:

    @staticmethod
    def load(
        prompt: dict,
    ) -> str:

        #
        # Prompt written directly in JSON
        #

        if prompt["source"] == "text":

            return prompt["value"]

        #
        # Prompt stored in a file
        #

        if prompt["source"] == "file":

            path = Path(
                prompt["value"]
            )

            return path.read_text(
                encoding="utf-8"
            )

        raise Exception(

            f"Unknown prompt source: {prompt['source']}"

        )