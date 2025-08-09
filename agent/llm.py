from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


@dataclass
class LLMResponse:
    role: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None


class BaseLLM:
    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        raise NotImplementedError


class OpenAILLM(BaseLLM):
    def __init__(self) -> None:
        if OpenAI is None:
            raise RuntimeError("openai package not available")
        self.client = OpenAI()

    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        selected_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        response = self.client.chat.completions.create(
            model=selected_model,
            messages=messages,
            tools=tools or None,
            temperature=temperature,
        )
        message = response.choices[0].message
        # Normalize to our response dataclass
        tool_calls = None
        if message.tool_calls:
            tool_calls = []
            for call in message.tool_calls:  # type: ignore[attr-defined]
                tool_calls.append(
                    {
                        "id": call.id,
                        "type": call.type,
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                )
        return LLMResponse(
            role=message.role or "assistant",
            content=message.content or "",
            tool_calls=tool_calls,
        )


class MockLLM(BaseLLM):
    """A very small deterministic LLM for offline demos.

    Behavior:
    - If no prior tool result is present, proposes a web_search with the user query.
    - After seeing any tool output in the conversation, returns a brief answer and stops.
    """

    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        last_user: Optional[str] = None
        saw_tool = False
        for msg in messages[::-1]:
            if msg.get("role") == "tool":
                saw_tool = True
                break
            if last_user is None and msg.get("role") == "user":
                last_user = msg.get("content")
        if not saw_tool and tools:
            # Propose a single web_search tool call
            tool = None
            for t in tools:
                if t.get("function", {}).get("name") == "web_search":
                    tool = t
                    break
            if tool is not None:
                call_id = f"call_{uuid.uuid4().hex[:8]}"
                args = {"query": (last_user or ""), "num_results": 5}
                return LLMResponse(
                    role="assistant",
                    content="",
                    tool_calls=[
                        {
                            "id": call_id,
                            "type": "function",
                            "function": {
                                "name": "web_search",
                                "arguments": json.dumps(args),
                            },
                        }
                    ],
                )
        # Otherwise, produce a minimal final answer
        summary = "Here is a brief summary based on the retrieved information."
        return LLMResponse(role="assistant", content=summary)


def create_llm(provider: str) -> BaseLLM:
    provider_normalized = (provider or "").strip().lower()
    if provider_normalized == "openai":
        if os.getenv("OPENAI_API_KEY") and OpenAI is not None:
            return OpenAILLM()
        # Fallback to mock if key missing or package unavailable
        return MockLLM()
    return MockLLM()