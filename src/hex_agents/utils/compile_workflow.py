from typing import Any


def compile_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    """
    Compiles a React Flow workflow into an executable workflow definition.
    """

    workflow_json = workflow["workflow_json"]

    compiled = {
        "id": workflow.get("name", "").lower().replace(" ", "_"),
        "description": workflow.get("description", ""),
        "version": 1,
        "nodes": [],
        "edges": [],
    }

    # ------------------------
    # Compile nodes
    # ------------------------
    for node in workflow_json["nodes"]:
        data = node["data"]

        compiled_node = {
            "id": data["id"],
            "type": data["type"],
        }

        # copy everything except UI metadata
        for key, value in data.items():
            if key in {"id", "type", "name", "description"}:
                continue

            compiled_node[key] = value

        compiled["nodes"].append(compiled_node)

    # ------------------------
    # Compile edges
    # ------------------------
    for edge in workflow_json["edges"]:
        compiled["edges"].append(
            {
                "from": edge["source"],
                "to": edge["target"],
            }
        )

    return compiled