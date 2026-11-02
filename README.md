# hex_agents

hex_agents is a schema-driven agent workflow engine built on top of LangGraph and LangChain.

You define a workflow as JSON (nodes + edges), then the factory layer converts that schema into an executable LangGraph state machine.

## What This Project Is

This package provides:

- A workflow schema format for agentic flows.
- A graph factory that converts schema to LangGraph nodes and edges.
- Runtime executors for run, stream, pause (interrupt), and resume.
- Registries for models, actions, and tools.
- Utilities to compile UI workflow JSON into runtime workflow JSON.

## Core Idea

The workflow JSON is the source of truth.

1. You provide a schema with `nodes` and `edges`.
2. The factory resolves each node type (`action`, `agent`, `interrupt`) into a callable runtime node.
3. It wires edges and also auto-connects `START`/`END`.
4. The executor compiles and runs the graph.

## Project Structure

- `src/hex_agents/factories/`
  - Schema -> runtime graph conversion.
- `src/hex_agents/graph/`
  - Thin wrapper over LangGraph `StateGraph`.
- `src/hex_agents/nodes/`
  - Runtime node implementations (`AgentNode`, `AsyncActionNode`, `InterruptNode`).
- `src/hex_agents/runners/`
  - Workflow execution, checkpointing, resume/stream.
- `src/hex_agents/registry/`
  - Registries for action/model/tool lookup and construction.
- `src/hex_agents/utils/compile_workflow.py`
  - Converts React Flow style payload into runtime schema.
- `src/hex_agents/workflows/`
  - Example workflow JSON files.

## Workflow Schema

Runtime workflows are plain JSON with this shape:

```json
{
  "id": "resume_email",
  "description": "HR workflow",
  "version": 1,
  "nodes": [
    {
      "id": "get_resume",
      "type": "action",
      "kind": "access_storage_node",
      "file_id": "..."
    },
    {
      "id": "analyse_resume",
      "type": "agent",
      "model": {
        "provider": "openai",
        "name": "gpt-4o-mini"
      },
      "prompt": {
        "source": "text",
        "value": "Analyse the resume and summarize strengths and risks."
      },
      "resources": [],
      "services": []
    },
    {
      "id": "approval_gate",
      "type": "interrupt",
      "title": "Manual Review",
      "message": "Continue to email drafting?"
    }
  ],
  "edges": [
    { "from": "get_resume", "to": "analyse_resume" },
    { "from": "analyse_resume", "to": "approval_gate" }
  ]
}
```

Node types:

- `action`: Executes a registered async action and updates state output.
- `agent`: Executes an LLM agent with prompt + model + tools.
- `interrupt`: Pauses the run and requires resume command.

## How It Works (End-to-End)

1. Load workflow JSON.
2. Create registries:
   - `ActionRegistry`: maps `kind` -> action factory.
   - `ModelRegistry`: maps provider + model name -> chat model instance.
   - `ToolRegistry`: resolves provider tools and optional filtering.
3. Build graph via factory.
4. Executor compiles graph.
5. Executor runs `ainvoke` (or streams), optionally with checkpointing if an interrupt node exists.
6. If interrupted, resume with `Command(resume=...)`.

## How WorkflowGraphFactory Uses Schema To Build LangGraph

The schema-to-graph conversion logic is centered in the factory classes.

### 1) Create LangGraph wrapper

The factory creates a `WorkflowGraph`, which internally holds a LangGraph `StateGraph(state_schema)` builder.

### 2) Convert each schema node into runtime callable

For every item in `workflow["nodes"]`:

- `type == "action"`
  - Uses `ActionRegistry.create(node)` to build action callable.
  - Wraps it in `AsyncActionNode` (in V1/V2 factory variants where applicable).
  - Adds node to graph using `graph.add_node(node_id, callable)`.

- `type == "agent"`
  - Builds tool list from schema resources/services or injected tools.
  - Resolves model from `ModelRegistry` using schema fields:
    - `node["model"]["provider"]`
    - `node["model"]["name"]`
  - Resolves prompt text via `PromptLoader`.
  - Builds system prompt via `PromptBuilder`.
  - Creates `AgentNode` and adds it to the graph.

- `type == "interrupt"`
  - Creates `InterruptNode(data=node)` and adds it.

### 3) Wire explicit edges

For every schema edge, it adds:

- `graph.add_edge(edge["from"], edge["to"])`

### 4) Auto-connect START and END

To keep schema simple:

- Any node with no incoming edge gets connected from LangGraph `START`.
- Any node with no outgoing edge gets connected to LangGraph `END`.

### 5) Handle edge-less fallback

If nodes exist but edges are empty:

- Connect `START -> first_node -> END`.

This guarantees a valid executable graph even for minimal workflows.

## Runtime and State

Execution is managed by `WorkflowExecutor`:

- Compiles once and reuses compiled app.
- Detects presence of `InterruptNode`.
- Enables Postgres checkpointer automatically when interrupts exist.
- Supports:
  - `arun()`
  - `astreamrun()`
  - `aresume(Command(...))`
  - state fetch and cleanup

State schema example (`LLMState`) includes:

- `last_message`
- `output`
- `token_usage`

Reducers define how each key is merged across graph steps.

## React Flow -> Runtime Schema

If your frontend sends React Flow JSON, use `compile_workflow(workflow)`.

It:

- Copies node data into runtime node objects.
- Converts edges from `source/target` to `from/to`.
- Produces normalized runtime schema consumed by factories.

## Quick Start Outline

1. Install package dependencies.
2. Build `ActionRegistry`, `ModelRegistry`, `ToolRegistry`.
3. Load workflow JSON.
4. Instantiate `WorkflowExecutor` with:
   - workflow
   - database url
   - registries
   - state schema
   - initial state/context
5. Run `await executor.arun()`.
6. If interrupted, call `await executor.aresume(Command(resume=...))`.

## Notes

- Keep secrets (API keys, tokens) in environment variables, not source code or workflow JSON.
- When using interrupt nodes, ensure Postgres is reachable for checkpointing.
- Multiple factory versions exist in this repository (`factories/` and `factories/v2/`) as the architecture evolves.
