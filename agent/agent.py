from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List, Optional

from .llm import BaseLLM, LLMResponse
from .tools import Tool, as_openai_tools_schema, execute_tool_call


SYSTEM_PROMPT = (
    "You are a helpful AI agent. You can think step-by-step, call tools when helpful, "
    "and provide concise final answers. Prefer accurate, cited, and up-to-date info."
)


class Agent:
    def __init__(
        self,
        llm: BaseLLM,
        tools: List[Tool],
        max_steps: int = 4,
        temperature: float = 0.2,
    ) -> None:
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.temperature = temperature

    def run(self, task: str, model: Optional[str] = None, verbose: bool = True) -> str:
        now = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": f"{SYSTEM_PROMPT} Today is {now}."},
            {"role": "user", "content": task},
        ]
        tools_schema = as_openai_tools_schema(self.tools)

        for step in range(1, self.max_steps + 1):
            response: LLMResponse = self.llm.complete(
                messages=messages,
                tools=tools_schema,
                model=model,
                temperature=self.temperature,
            )

            if response.tool_calls:
                for tool_call in response.tool_calls:
                    name = tool_call.get("function", {}).get("name", "")
                    arguments_json = tool_call.get("function", {}).get("arguments", "{}")
                    tool_call_id = tool_call.get("id")
                    result = execute_tool_call(self.tools, name=name, arguments_json=arguments_json)
                    messages.append(
                        {
                            "role": "assistant",
                            "content": "",
                            "tool_calls": [tool_call],
                        }
                    )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "name": name,
                            "content": result,
                        }
                    )
                # Continue loop after tool execution
                continue

            # No tool calls => produce final answer
            final = response.content.strip() or "No answer produced."
            return final

        # If we exit the loop without a final non-tool message
        return "Reached step limit without a final answer."