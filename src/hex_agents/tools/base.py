from typing import Any


class Tool:

    def __init__(
        self,
        key: str,
        name: str,
        handler: Any,
        input_schema: dict[str, Any] | None = None,
        description: str | None = None,
    ):
        self.key = key
        self.name = name
        self.handler = handler
        self.input_schema = input_schema or {}

        # Use explicitly provided description first.
        # Otherwise use the description from the LangChain tool.
        self.description = (
            description
            or getattr(handler, "description", None)
            or getattr(handler, "__doc__", None)
            or ""
        )

    def definition(self) -> dict[str, str]:
        return {
            "key": self.key,
            "name": self.name,
            "description": self.description,
        }
        
        
    def execute(self, **kwargs: Any) -> Any:
        """
        Execute the actual Python function.
        """
        return self.handler(**kwargs)
