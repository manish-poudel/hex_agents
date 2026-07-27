import json


def load_workflow(path: str) -> dict:

    with open(path, "r") as file:
        return json.load(file)