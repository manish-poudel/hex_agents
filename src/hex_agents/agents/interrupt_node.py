from langgraph.types import interrupt

class InterruptNode:

    def __init__(self, data):
        self.data = data

    def __call__(self, state):

        interrupts = list(state.get("interrupts", []))

        interrupts.append({
            "id": self.data["id"],
            "type": "approval",
            "status": "waiting",
        })

        # Pause
        response = interrupt({
            "id": self.data["id"],
            "title": self.data["title"],
            "message": self.data["message"],
        })

        # We only reach here after resume
        for item in interrupts:
            if item["id"] == self.data["id"]:
                item["status"] = response["status"]

        # return {
        #     "interrupts": interrupts
        # }

        return state;