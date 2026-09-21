from typing import Any, Awaitable, Callable
from hex_agents.factories.workflow_graph_factory_v2 import WorkflowGraphFactoryV2
from hex_agents.model.context import RuntimeContext
from langgraph.types import Command
from psycopg import AsyncConnection
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from hex_agents.registry.action_registry import ActionRegistry
from hex_agents.registry.tool_registry import ToolRegistry
from hex_agents.registry.model_registry import ModelRegistry



class WorkflowExecutor:

    def _debug(self, message: str) -> None:
        pass

    def __init__(
        self,
        workflow: dict[str, Any],
        database_url: str,
        tool_registry: ToolRegistry,
        action_registry: ActionRegistry,
        model_registry: ModelRegistry,
        state_schema: type,
        initial_state: Any | None = None,
        thread_id: str | None = None,
        context: RuntimeContext | None = None,
        before_agent_execution: Callable[
            [str, dict],
            Awaitable[None],
        ] | None = None,
        after_agent_execution: Callable[
            [str, dict],
            Awaitable[None],
        ] | None = None,
    ):
        self.workflow = workflow
        self.context = context
        self.database_url = database_url
        self.thread_id = thread_id
        self.initial_state = initial_state

        self.workflow_graph = WorkflowGraphFactoryV2(
            workflow,
            tool_registry=tool_registry,
            action_registry=action_registry,
            model_registry=model_registry,
            before_agent_execution=before_agent_execution,
            after_agent_execution=after_agent_execution,
            state_schema=state_schema,
        ).build()

        self.conn: AsyncConnection | None = None
        self.checkpointer: AsyncPostgresSaver | None = None
        self.compiled_app = None
        
    @property
    def has_interrupt_node(self) -> bool:
        return self.workflow_graph.has_node_class("InterruptNode")


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
        initial_state = self.initial_state
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

        stream_kwargs = {
            "context": self.context,
            "stream_mode": "values",
        }

        if self.has_interrupt_node:
            stream_kwargs["config"] = self.config

        return app.astream(
            self.initial_state,
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
