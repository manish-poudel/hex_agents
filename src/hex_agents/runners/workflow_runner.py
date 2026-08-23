from __future__ import annotations

from typing import Any
from hex_agents.model.context import RuntimeContext
from langgraph.types import Command
from psycopg import AsyncConnection
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from hex_agents.factories.workflow_graph_factory import WorkflowGraphFactory
from hex_agents.registry.action_registry import ActionRegistry
from hex_agents.registry.tool_registry import ToolRegistry


class WorkflowExecutor:

    def _debug(self, message: str) -> None:
        print(f"[WorkflowExecutor:{self.workflow_run_id}] {message}")

    def __init__(
        self,
        workflow: dict[str, Any],
        database_url: str,
        workflow_id: str,
        tool_registry: ToolRegistry,
        action_registry: ActionRegistry,
        workflow_run_id: str | None = None,
        context: RuntimeContext | None = None,
    ):
        self.workflow = workflow
        self.context = context
        self.database_url = database_url
        self.workflow_id = workflow_id
        self.workflow_run_id = workflow_run_id

        self.workflow_graph = WorkflowGraphFactory(
            workflow,
            tool_registry=tool_registry,
            action_registry=action_registry,
        ).build()

        self.conn: AsyncConnection | None = None
        self.checkpointer: AsyncPostgresSaver | None = None
        self.compiled_app = None
        print(f"WorkflowExecutor initialized with workflow_id: {self.workflow_id}")

    @property
    def has_interrupt_node(self) -> bool:
        return self.workflow_graph.has_node_class("InterruptNode")

    @property
    def thread_id(self) -> str:
        return self.workflow_run_id

    @property
    def config(self) -> dict[str, Any]:
        return {
            "configurable": {
                "thread_id": self.thread_id,
            }
        }

    async def _initialize_checkpointer(self) -> None:
        self.conn = await AsyncConnection.connect(
            self.database_url,
            autocommit=True,
        )

        self.checkpointer = AsyncPostgresSaver(self.conn)

        await self.checkpointer.setup()

    async def acompile(
        self,
        with_checkpointer: bool | None = None,
    ):
        if self.compiled_app is not None:
            self._debug("reusing compiled app")
            return self.compiled_app

        if with_checkpointer is None:
            with_checkpointer = self.has_interrupt_node

        self._debug(f"compiling workflow with_checkpointer={with_checkpointer}")

        if with_checkpointer:
            await self._initialize_checkpointer()

            self.compiled_app = self.workflow_graph.compile(
                checkpointer=self.checkpointer
            )
        else:
            self.compiled_app = self.workflow_graph.compile()

        return self.compiled_app

    async def arun(self) -> dict[str, Any]:
        app = await self.acompile()
        self._debug("starting arun")
        print("workflow graph:")
        print(self.workflow_graph.print_graph())

        initial_state = {
            "workflow_id": self.workflow_id,
            "workflow_run_id": self.workflow_run_id,
        }

        self._debug(f"initial state keys={list(initial_state.keys())}")

        if self.has_interrupt_node:
            self._debug("invoking app with checkpointer")
            result = await app.ainvoke(
                initial_state,
                config=self.config,
                context=self.context,
            )
        else:
            self._debug("invoking app without checkpointer")
            result = await app.ainvoke(
                initial_state,
                context=self.context,
            )

        self._debug(
            f"arun finished result keys={list(result.keys()) if isinstance(result, dict) else type(result)}"
        )

        return result

    async def aresume(
        self,
        command: Command,
    ) -> dict[str, Any]:
        app = await self.acompile(with_checkpointer=True)

        self._debug(f"resuming with command={command}")
        self._debug(f"resuming with config={self.config}")

        result = await app.ainvoke(
            command,
            config=self.config,
            context=self.context,
        )

        self._debug(
            f"resume finished result keys={list(result.keys()) if isinstance(result, dict) else type(result)}"
        )

        return result

    async def astreamrun(
        self,
    ):
        app = await self.acompile()

        initial_state = {
            "workflow_id": self.workflow_id,
            "workflow_run_id": self.workflow_run_id,
        }

        stream_kwargs = {
            "context": self.context,
            "stream_mode": "values",
        }

        if self.has_interrupt_node:
            stream_kwargs["config"] = self.config

        return app.astream(
            initial_state,
            **stream_kwargs,
        )

    async def streamresume(
        self,
        command: Command,
    ):
        app = await self.acompile(with_checkpointer=True)

        self._debug(f"resuming with command={command}")
        self._debug(f"resuming with config={self.config}")

        return app.astream(
            command,
            config=self.config,
            context=self.context,
            stream_mode="values",
        )

    async def aget_state(self):
        if self.compiled_app is None:
            raise RuntimeError("Workflow has not been compiled.")

        return await self.compiled_app.aget_state(self.config)

    async def acleanup(self) -> None:
        if self.checkpointer is not None:
            await self.checkpointer.adelete_thread(self.thread_id)

    async def aclose(self) -> None:
        if self.conn is not None:
            await self.conn.close()
            self.conn = None

        self.checkpointer = None
        self.compiled_app = None
