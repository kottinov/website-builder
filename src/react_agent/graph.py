"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""

from typing import Dict, List, Literal, cast

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime
from langchain_anthropic import convert_to_anthropic_tool

from react_agent.context import Context
from react_agent.state import InputState, State
from react_agent.tools import TOOLS
from react_agent.utils import load_chat_model

_ANTHROPIC_TOOLS_CACHED = None
_CACHEABLE_TOOL_NAMES = {"mutate_components"}


def _get_anthropic_tools():
    """Get cached Anthropic tool schemas with prompt caching enabled.

    Converts tools once and caches them for reuse across all LLM calls.
    Applies cache_control only to selected tools to stay under Anthropic limits.
    """
    global _ANTHROPIC_TOOLS_CACHED

    if _ANTHROPIC_TOOLS_CACHED is None:
        _ANTHROPIC_TOOLS_CACHED = [convert_to_anthropic_tool(tool) for tool in TOOLS]

        for tool in _ANTHROPIC_TOOLS_CACHED:
            if tool.get("name") in _CACHEABLE_TOOL_NAMES:
                tool["cache_control"] = {"type": "ephemeral"}
                # tool["cache_control"] = {"type": "ephemeral", "ttl_seconds": 900}

    return _ANTHROPIC_TOOLS_CACHED


async def call_model(
    state: State, runtime: Runtime[Context]
) -> Dict[str, List[AIMessage]]:
    """Call the LLM powering our "agent".

    This function prepares the prompt, initializes the model, and processes the response.
    Implements prompt caching and token-efficient tool use for Anthropic models.

    Args:
        state (State): The current state of the conversation.
        runtime (Runtime[Context]): Runtime configuration with model and system prompt.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    model = load_chat_model(runtime.context.model)

    if "anthropic" in runtime.context.model.lower():
        anthropic_tools = _get_anthropic_tools()
        model = model.bind_tools(anthropic_tools, parallel_tool_calls=False)
    else:
        model = model.bind_tools(TOOLS, parallel_tool_calls=False)

    system_message = runtime.context.system_prompt

    if "anthropic" in runtime.context.model.lower():
        system_content = [
            {
                "type": "text",
                "text": system_message,
                "cache_control": {"type": "ephemeral"},
            }
        ]
        messages = [{"role": "system", "content": system_content}, *state.messages]
    else:
        messages = [{"role": "system", "content": system_message}, *state.messages]

    response = cast(
        AIMessage,
        await model.ainvoke(messages),
    )

    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, I could not find an answer to your question in the specified number of steps.",
                )
            ]
        }

    return {"messages": [response]}


builder = StateGraph(State, input_schema=InputState, context_schema=Context)

builder.add_node(call_model)
builder.add_node("tools", ToolNode(TOOLS, handle_tool_errors=True))

builder.add_edge("__start__", "call_model")


def route_model_output(state: State) -> Literal["__end__", "tools"]:
    """Determine the next node based on the model's output.

    This function checks if the model's last message contains tool calls.

    Args:
        state (State): The current state of the conversation.

    Returns:
        str: The name of the next node to call ("__end__" or "tools").
    """
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(
            f"Expected AIMessage in output edges, but got {type(last_message).__name__}"
        )
    if not last_message.tool_calls:
        return "__end__"
    return "tools"


builder.add_conditional_edges(
    "call_model",
    route_model_output,
)

builder.add_edge("tools", "call_model")

graph = builder.compile(name="ReAct Agent").with_config({"recursion_limit": 100})
