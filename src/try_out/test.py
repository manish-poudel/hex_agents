from typing import Any
from uuid import uuid4


class WorkflowCompilerV2:

    # ======================================================
    # PUBLIC
    # ======================================================

    def compile(
        self,
        workflow_json: dict[str, Any],
    ) -> dict[str, Any]:

        return self._compile(
            workflow_json=workflow_json,
        )

    def compile_trigger(
        self,
        workflow_json: dict[str, Any],
        event_source_id: str | None = None,
    ) -> dict[str, Any]:

        return self._compile(
            workflow_json=workflow_json,
            event_source_id=event_source_id,
        )

    # ======================================================
    # MAIN COMPILER
    # ======================================================

    def _compile(
        self,
        workflow_json: dict[str, Any],
        event_source_id: str | None = None,
    ) -> dict[str, Any]:

        metadata = workflow_json.get("__metadata__") or {}

        compiled = {
            "id": workflow_json.get(
                "id",
                "",
            ).lower().replace(" ", "_"),

            "description": workflow_json.get(
                "description",
                "",
            ),

            "version": workflow_json.get(
                "version",
                1,
            ),

            "nodes": [],
            "edges": [],

            "services": metadata.get(
                "services",
            ) or [],

            "models": metadata.get(
                "models",
            ) or [],

            "has_skills": bool(
                metadata.get("has_skills")
            ),
        }

        nodes = workflow_json.get("nodes", [])
        edges = workflow_json.get("edges", [])

        nodes_by_id = {
            node["id"]: node
            for node in nodes
        }

        node_id_map: dict[str, str] = {}

        # ==================================================
        # NODES
        # ==================================================

        for node in nodes:

            node_id = node["id"]
            node_type = node.get("type")
            node_data = node.get("data") or {}

            # --------------------------------------------------
            # STORAGE TRIGGER
            # --------------------------------------------------

            if (
                node_type == "storage_trigger"
                and node_data.get("is_executable") is False
            ):

                if event_source_id is None:
                    raise ValueError(
                        "Storage trigger requires event_source_id"
                    )

                injected_id = str(uuid4())

                node_id_map[node_id] = injected_id

                compiled["nodes"].append(
                    {
                        "id": injected_id,
                        "type": "action",
                        "kind": "access_storage_node",
                        "file_id": event_source_id,
                    }
                )

                continue

            # --------------------------------------------------
            # NON EXECUTABLE
            # --------------------------------------------------

            if node_data.get(
                "is_executable",
                True,
            ) is False:

                continue

            # --------------------------------------------------
            # MULTIPLE FILES
            # --------------------------------------------------

            if node_type == "multiple_select_files":

                compiled_node = self._compile_multiple_files(
                    node=node,
                    nodes_by_id=nodes_by_id,
                    edges=edges,
                )

                node_id_map[node_id] = node_id

                compiled["nodes"].append(
                    compiled_node
                )

                continue

            # --------------------------------------------------
            # NORMAL NODE
            # --------------------------------------------------

            node_id_map[node_id] = node_id

            compiled["nodes"].append(
                {
                    "id": node_id,
                    **node_data,
                }
            )

        # ==================================================
        # EDGES
        # ==================================================

        for edge in edges:

            source = edge.get("source")
            target = edge.get("target")

            source_id = node_id_map.get(source)
            target_id = node_id_map.get(target)

            if source_id is None or target_id is None:
                continue

            # The edge FROM multiple_select_files is consumed
            # by the subgraph compiler.
            #
            # It will be replaced by:
            #
            # fan_out_multiple_files -> first OUTER node
            #
            # depending on the graph structure.
            if (
                nodes_by_id.get(source, {}).get("type")
                == "multiple_select_files"
            ):
                continue

            compiled["edges"].append(
                {
                    "from": source_id,
                    "to": target_id,
                }
            )

        # ==================================================
        # MULTIPLE FILE OUTER EDGES
        # ==================================================

        for node in nodes:

            if node.get("type") != "multiple_select_files":
                continue

            self._compile_multiple_file_outer_edges(
                node=node,
                nodes_by_id=nodes_by_id,
                edges=edges,
                compiled=compiled,
            )

        return compiled

    # ======================================================
    # MULTIPLE FILES
    # ======================================================

    def _compile_multiple_files(
        self,
        node: dict[str, Any],
        nodes_by_id: dict[str, dict[str, Any]],
        edges: list[dict[str, Any]],
    ) -> dict[str, Any]:

        node_data = node.get("data") or {}
        node_id = node["id"]

        file_ids = node_data.get("file_ids") or []

        if not file_ids:
            raise ValueError(
                "multiple_select_files requires file_ids"
            )

        # --------------------------------------------------
        # Find direct downstream nodes
        # --------------------------------------------------

        outgoing = [
            edge
            for edge in edges
            if edge.get("source") == node_id
        ]

        if not outgoing:
            raise ValueError(
                f"multiple_select_files '{node_id}' "
                "must have a downstream node"
            )

        # --------------------------------------------------
        # For now, the first downstream branch is the
        # per-file workflow.
        #
        # The important part:
        # We preserve the exact frontend ordering.
        # --------------------------------------------------

        worker_start_id = outgoing[0]["target"]

        worker_nodes = [
            {
                "id": f"{node_id}-select-file",
                "type": "action",
                "kind": "access_storage_node",
            }
        ]

        worker_edges = [
            {
                "from": "START",
                "to": f"{node_id}-select-file",
            }
        ]

        current_id = worker_start_id
        previous_id = f"{node_id}-select-file"

        visited: set[str] = set()

        while current_id not in visited:

            visited.add(current_id)

            current_node = nodes_by_id.get(current_id)

            if current_node is None:
                break

            current_data = current_node.get("data") or {}

            # ----------------------------------------------
            # Stop at a reducer.
            #
            # Reducer remains in the parent workflow.
            # ----------------------------------------------

            if self._is_reducer(current_node):

                break

            # ----------------------------------------------
            # Non executable UI node
            # ----------------------------------------------

            if current_data.get(
                "is_executable",
                True,
            ) is False:

                break

            # ----------------------------------------------
            # Add node to worker
            # ----------------------------------------------

            worker_nodes.append(
                {
                    "id": current_id,
                    **current_data,
                }
            )

            # ----------------------------------------------
            # Preserve frontend order
            # ----------------------------------------------

            worker_edges.append(
                {
                    "from": previous_id,
                    "to": current_id,
                }
            )

            previous_id = current_id

            # ----------------------------------------------
            # Find next node
            # ----------------------------------------------

            next_edges = [
                edge
                for edge in edges
                if edge.get("source") == current_id
            ]

            if not next_edges:
                break

            current_id = next_edges[0]["target"]

        # --------------------------------------------------
        # Worker ends after its last per-file node.
        # --------------------------------------------------

        worker_edges.append(
            {
                "from": previous_id,
                "to": "END",
            }
        )

        return {
            "id": node_id,
            "type": "fan_out_multiple_files",
            "file_ids": file_ids,
            "workflow": {
                "id": f"{node_id}_worker",
                "description": "Process one file",
                "version": 1,
                "nodes": worker_nodes,
                "edges": worker_edges,
            },
        }

    # ======================================================
    # OUTER EDGES
    # ======================================================

    def _compile_multiple_file_outer_edges(
        self,
        node: dict[str, Any],
        nodes_by_id: dict[str, dict[str, Any]],
        edges: list[dict[str, Any]],
        compiled: dict[str, Any],
    ):

        node_id = node["id"]

        outgoing = [
            edge
            for edge in edges
            if edge.get("source") == node_id
        ]

        if not outgoing:
            return

        # --------------------------------------------------
        # Walk the frontend graph.
        #
        # The worker nodes stay inside the subgraph.
        # Once we reach a reducer, it becomes the first
        # node in the parent workflow.
        # --------------------------------------------------

        for edge in outgoing:

            current_id = edge["target"]

            visited: set[str] = set()

            while current_id not in visited:

                visited.add(current_id)

                current_node = nodes_by_id.get(current_id)

                if current_node is None:
                    break

                # ------------------------------------------
                # Reducer is parent-level.
                # ------------------------------------------

                if self._is_reducer(current_node):

                    compiled["edges"].append(
                        {
                            "from": node_id,
                            "to": current_id,
                        }
                    )

                    return

                # ------------------------------------------
                # This node belongs to the worker.
                # Continue following its frontend edge.
                # ------------------------------------------

                next_edges = [
                    e
                    for e in edges
                    if e.get("source") == current_id
                ]

                if not next_edges:
                    break

                current_id = next_edges[0]["target"]

    # ======================================================
    # REDUCER DETECTION
    # ======================================================

    def _is_reducer(
        self,
        node: dict[str, Any],
    ) -> bool:

        node_data = node.get("data") or {}

        # Explicit frontend designation.
        #
        # Recommended frontend data:
        #
        # "role": "reducer"
        #
        return (
            node_data.get("role") == "reducer"
            or node.get("type") == "reducer"
        )


# ==========================================================
# TEST FRONTEND JSON
# ==========================================================

workflow_json = {

    "nodes": [

        {
            "id": "multiple-files-1",
            "type": "multiple_select_files",
            "data": {
                "id": "multiple-files-1",
                "kind": "access_storage_node",
                "name": "Select Files",
                "type": "action",

                "file_ids": [
                    "file-001",
                    "file-002",
                    "file-003",
                ],

                "description": "",
                "is_executable": True,
            },
        },

        {
            "id": "agent-1",
            "type": "agent",
            "data": {
                "id": "agent-1",
                "name": "Analyze File",
                "type": "agent",

                "model": {
                    "name": "gemini-3.5-flash",
                    "provider": "google",
                    "api_key": "",
                },

                "prompt": {
                    "value": "Analyze the contents of the file.",
                    "source": "text",
                },

                "services": [],
                "resources": [],

                "description": "",
                "is_executable": True,
            },
        },

        {
            "id": "reducer-1",
            "type": "agent",
            "data": {
                "id": "reducer-1",
                "name": "Combine Results",
                "type": "agent",

                # IMPORTANT:
                # Frontend explicitly tells compiler
                # this node is a reducer.
                "role": "reducer",

                "model": {
                    "name": "gemini-3.5-flash",
                    "provider": "google",
                    "api_key": "",
                },

                "prompt": {
                    "value": (
                        "Combine the analysis results "
                        "from all files."
                    ),
                    "source": "text",
                },

                "services": [],
                "resources": [],

                "description": "",
                "is_executable": True,
            },
        },
    ],

    "edges": [

        {
            "id": "edge-multiple-agent",
            "source": "multiple-files-1",
            "target": "agent-1",
        },

        {
            "id": "edge-agent-reducer",
            "source": "agent-1",
            "target": "reducer-1",
        },
    ],

    "__metadata__": {
        "models": [
            {
                "provider": "google",
                "model_name": "gemini-3.5-flash",
            }
        ],
        "services": [],
        "triggers": [],
        "schedules": [],
        "has_skills": False,
    },
}


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    from pprint import pprint

    compiler = WorkflowCompilerV2()

    compiled = compiler.compile(
        workflow_json
    )

    pprint(
        compiled,
        sort_dicts=False,
    )