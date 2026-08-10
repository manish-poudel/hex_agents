from __future__ import annotations

import uuid
from typing import Any

from langgraph.types import Command
from psycopg import AsyncConnection
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from hex_agents.factories.workflow_graph_factory import WorkflowGraphFactory
from hex_agents.model.auth_context import AuthContext


class WorkflowExecutor:

    def __init__(
        self,
        workflow: dict[str, Any],
        context: AuthContext,
        database_url: str,
        workflow_id: str,
        workflow_run_id: str | None = None,
    ):
        self.workflow = workflow
        self.context = context
        self.database_url = database_url
        self.workflow_id = workflow_id
        self.workflow_run_id = workflow_run_id or uuid.uuid4().hex

        self.workflow_graph = WorkflowGraphFactory(
            workflow
        ).build()

        self.conn: AsyncConnection | None = None
        self.checkpointer: AsyncPostgresSaver | None = None
        self.compiled_app = None

    @property
    def has_interrupt_node(self) -> bool:
        return self.workflow_graph.has_node_class(
            "InterruptNode"
        )

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

        self.checkpointer = AsyncPostgresSaver(
            self.conn
        )

        await self.checkpointer.setup()

    async def acompile(
        self,
        with_checkpointer: bool | None = None,
    ):
        if self.compiled_app is not None:
            return self.compiled_app

        if with_checkpointer is None:
            with_checkpointer = self.has_interrupt_node

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

        print(str(self.workflow["id"]))

        initial_state = {
            "workflow_id": self.workflow_id,
            "workflow_run_id": self.workflow_run_id,
            "output": "",
        }

        if self.has_interrupt_node:
            result = await app.ainvoke(
                initial_state,
                config=self.config,
                context=self.context,
            )
        else:
            result = await app.ainvoke(
                initial_state,
                context=self.context,
            )

        return {
            "workflow_run_id": self.workflow_run_id,
            "thread_id": (
                self.thread_id
                if self.has_interrupt_node
                else None
            ),
            "result": result,
        }

    async def aresume(
        self,
        command: Command,
    ) -> dict[str, Any]:
        app = await self.acompile(
            with_checkpointer=True
        )

        result = await app.ainvoke(
            command,
            config=self.config,
            context=self.context,
        )

        return {
            "workflow_run_id": self.workflow_run_id,
            "thread_id": self.thread_id,
            "result": result,
        }

    async def aget_state(self):
        if self.compiled_app is None:
            raise RuntimeError(
                "Workflow has not been compiled."
            )

        return await self.compiled_app.aget_state(
            self.config
        )

    async def acleanup(self) -> None:
        if self.checkpointer is not None:
            await self.checkpointer.adelete_thread(
                self.thread_id
            )

    async def aclose(self) -> None:
        if self.conn is not None:
            await self.conn.close()
            self.conn = None

        self.checkpointer = None
        self.compiled_app = None