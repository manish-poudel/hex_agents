from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from langgraph.types import Command

from hex_agents.factories.workflow_graph_factory import WorkflowGraphFactory
from hex_agents.model.auth_context import AuthContext


@dataclass
class WorkflowRunner:
    """Compile and execute workflows with auth context in one place."""

    default_state: dict[str, Any] | None = None

    def _build_initial_state(self, initial_state: dict[str, Any] | None, workflow_id: str) -> dict[str, Any]:
        # workflow_id must be provided in initial_state
        if not workflow_id:
            raise ValueError("workflow_id must be provided")

        state = {
            "workflow_run_id": str(uuid.uuid4()),
            "interrupt": None,
            "workflow_id": workflow_id,
            "messages": [],
            "outputs": {},
            "used_tools": {},
            "interrupts": [],
        }

        if self.default_state:
            state.update(self.default_state)

        if initial_state:
            state.update(initial_state)

        return state

    async def ainvoke(
        self,
        *,
        user_id: str,
        token: str,
        workflow: dict[str, Any] | None = None,
        workflow_graph=None,
        app=None,
        checkpointer=None,
        initial_state: dict[str, Any] | None = None,
        command: Command | None = None,
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a workflow using LangGraph's async invoke.

        Provide one of: workflow, workflow_graph, or app.
        For resuming interrupted workflows, provide command parameter.
        For normal execution, provide initial_state or leave empty.
        """
        compiled_app = app

        if compiled_app is None:
            if workflow_graph is not None:
                compiled_app = workflow_graph.compile(checkpointer=checkpointer)
            elif workflow is not None:
                workflow_graph = WorkflowGraphFactory(workflow).build()
                compiled_app = workflow_graph.compile(checkpointer=checkpointer)
            else:
                raise ValueError("Provide one of workflow, workflow_graph, or app.")

        context = AuthContext(accessor_id=user_id, access_token=token)

        # Resume interrupted workflow with command
        if command is not None:
            if config is None:
                return await compiled_app.ainvoke(command, context=context)
            return await compiled_app.ainvoke(command, config=config, context=context)

        # Normal workflow execution
        state = self._build_initial_state(initial_state, workflow_id=workflow["id"])

        if config is None:
            return await compiled_app.ainvoke(state, context=context)

        return await compiled_app.ainvoke(state, config=config, context=context)


async def ainvoke_workflow(
    *,
    user_id: str,
    token: str,
    workflow: dict[str, Any] | None = None,
    workflow_graph=None,
    app=None,
    checkpointer=None,
    initial_state: dict[str, Any] | None = None,
    command: Command | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convenience function wrapper for WorkflowRunner."""
    runner = WorkflowRunner()
    return await runner.ainvoke(
        user_id=user_id,
        token=token,
        workflow=workflow,
        workflow_graph=workflow_graph,
        app=app,
        checkpointer=checkpointer,
        initial_state=initial_state,
        command=command,
        config=config,
    )


