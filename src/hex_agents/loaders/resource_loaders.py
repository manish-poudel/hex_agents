from pathlib import Path


class ResourceLoader:

    @staticmethod
    def load(resources: list) -> str:

        knowledge = []

        for resource in resources:

            #
            # File Resource
            #

            if resource["type"] == "file":

                path = Path(resource["path"])

                knowledge.append(

                    path.read_text(
                        encoding="utf-8"
                    )

                )

        return "\n\n".join(knowledge)