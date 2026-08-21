from langgraph.types import interrupt

class InterruptNode:

    def __init__(self, data):
        self.data = data

    def _debug(self, message: str) -> None:
        print(f"[InterruptNode:{self.data['id']}] {message}")

    def __call__(self, state):

        self._debug(f"entered with state output={state.get('output', '')!r}")

        # interrupts = list(state.get("interrupts", []))

        # interrupts.append({
        #     "id": self.data["id"],
        #     "type": "approval",
        #     "status": "waiting",
        # })

        # Pause
        self._debug("calling interrupt() to pause graph")
        interrupt({
            "id": self.data["id"],
            "title": self.data["title"],
            "message": self.data["message"],
        })

        # # We only reach here after resume
        # self._debug(f"resumed with response={response!r}")
        # for item in interrupts:
        #     if item["id"] == self.data["id"]:
        #         item["status"] = response["status"]

        # return {
        #     "interrupts": interrupts
        # }

        self._debug("returning state after resume")

        return state