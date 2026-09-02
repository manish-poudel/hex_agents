from langgraph.types import interrupt

class InterruptNode:

    def __init__(self, data):
        self.data = data

    def _debug(self, message: str) -> None:
        pass

    def __call__(self, state):

        self._debug(f"entered with state output={state.get('output', '')!r}")


        # Pause
        self._debug("calling interrupt() to pause graph")
        interrupt({
            "id": self.data["id"],
            "title": self.data["title"],
            "message": self.data["message"],
        })

        self._debug("returning state after resume")

        return {}