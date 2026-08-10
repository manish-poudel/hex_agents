from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from langgraph.types import Command

from hex_agents.factories.workflow_graph_factory import WorkflowGraphFactory
from hex_agents.model.auth_context import AuthContext


@dataclass
class WorkflowExecutor:
    """Workflow executor responsible for compiling and invoking LangGraph."""

    user_id: str
    token: str
    workflow: dict[str, Any]
    workflow_id: str
    workflow_run_id: str
    thread_id: str | None = None
    checkpointer: Any | None = None
    default_state: dict[str, Any] = field(default_factory=dict)

    def build_initial_state(
        self,
        initial_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        state = {
            "workflow_id": self.workflow_id,
            "workflow_run_id": self.workflow_run_id,
            "output": ""
        }

        if self.default_state:
            state.update(self.default_state)

        if initial_state:
            state.update(initial_state)


        return state

    def _prepare_runtime(
        self,
        *,
        require_interrupt_runtime: bool,
    ) -> tuple[Any, dict[str, Any] | None, AuthContext]:
        workflow_graph = WorkflowGraphFactory(self.workflow).build()
        has_interrupts = workflow_graph.has_node_class("InterruptNode")

        if require_interrupt_runtime and not has_interrupts:
            raise ValueError("resume requires a workflow with interrupt nodes")

        config = None
        checkpointer = None

        if has_interrupts:
            if self.thread_id is None:
                raise ValueError("thread_id is required for workflows with interrupt nodes")

            if self.checkpointer is None:
                raise ValueError("checkpointer is required for workflows with interrupt nodes")

            config = {
                "configurable": {
                    "thread_id": self.thread_id
                }
            }
            checkpointer = self.checkpointer

        compiled_app = workflow_graph.compile(checkpointer=checkpointer)
        context = AuthContext(accessor_id=self.user_id, access_token=self.token)
        return compiled_app, config, context

    def prepare_first_time(
        self,
        initial_state: dict[str, Any] | None = None,
    ) -> tuple[Any, dict[str, Any], dict[str, Any] | None, AuthContext]:
        if self.workflow_run_id is None:
            raise ValueError("workflow_run_id is required")

        compiled_app, config, context = self._prepare_runtime(
            require_interrupt_runtime=False,
        )
        state = self.build_initial_state(initial_state)
        return compiled_app, state, config, context

    def prepare_resume(
        self,
        command: Command,
    ) -> tuple[Any, Command, dict[str, Any], AuthContext]:
        if command is None:
            raise ValueError("command is required to resume workflow")

        if self.workflow_run_id is None:
            raise ValueError("workflow_run_id is required to resume workflow")

        compiled_app, config, context = self._prepare_runtime(
            require_interrupt_runtime=True,
        )
        if config is None:
            raise ValueError("config is required to resume workflow")

        return compiled_app, command, config, context


    async def invoke_first_time(
        self,
        initial_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Invoke workflow for the first time."""
        compiled_app, state, config, context = self.prepare_first_time(initial_state)

        if config is None:
            return await compiled_app.ainvoke(state, context=context)

        return await compiled_app.ainvoke(state, config=config, context=context)

    
    

    async def invoke_resume(
        self,
        command: Command,
    ) -> dict[str, Any]:
        """Resume an interrupted workflow."""
        compiled_app, resume_command, config, context = self.prepare_resume(command)
        return await compiled_app.ainvoke(resume_command, config=config, context=context)



