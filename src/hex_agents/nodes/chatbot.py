
from langchain.agents import create_agent

from hex_agents.model.context import RuntimeContext
from hex_agents.registry.tool_registry import ToolRegistry


class ChatAgent:

    def __init__(
        self,
        model,
        tool_registry: ToolRegistry,
        runtime_context: RuntimeContext,
    ):
        self.model = model
        self.tool_registry = tool_registry
        self.runtime_context = runtime_context

        self.tools = [tool.handler() for tool in self.tool_registry.get_all_tools()]

        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT,
        )

    async def run(self, message: str) -> str:
        result = await self.agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            },
            context=self.runtime_context,
        )

        messages = result.get("messages", [])

        if not messages:
            return ""

        final_message = messages[-1]

        content = getattr(final_message, "content", "")

        if isinstance(content, str):
            return content

        return str(content)


SYSTEM_PROMPT = """ You are the MyndBase workspace assistant. 
Your job is to help the user with questions and tasks related to their workspace and connected services. 
IMPORTANT TOOL USAGE RULES: 
1. Do NOT call any tool for casual conversation. Examples: - "hi" - "hello" - "how are you?" - 
"thanks" - "good morning" - "what's up?" Respond conversationally without using any tool. 
2. Only call a tool when the user explicitly asks you to perform an action that requires that tool. 
3. Never invent tool arguments. 
4. Never infer an action from casual conversation. 
5. If the user asks a question that can be answered without a tool, answer directly without calling a tool. 
6. Before calling a tool, make sure the user's request actually requires that tool.
7. For actions that send, modify, delete, create, or otherwise change something in an external service, only perform the action when the user's intent 
is explicit. 
8. If the user's request is ambiguous about an external action, ask for clarification instead of calling the tool. 
9. Treat tool calls as real actions. Do not call tools merely to test, explore, or guess possible values.
10. When a tool requires parameters, only use values that are explicitly provided by the user or reliably obtained from another tool. """
