from abc import ABC, abstractmethod


class BaseTool(ABC):

    @abstractmethod
    def execute(self):
        """
        Execute the tool.

        Returns:
            Any
        """
        pass