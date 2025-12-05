"""Utility & helper functions."""

import json
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from langchain.chat_models import init_chat_model
from langchain_anthropic import convert_to_anthropic_tool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage


def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)

    if provider.lower() == "anthropic":
        return init_chat_model(
            model,
            model_provider=provider,
            default_headers={"anthropic-beta": "prompt-caching-2024-07-31"},
        )

    return init_chat_model(model, model_provider=provider)


_ANTHROPIC_TOOLS_CACHE: Optional[List[Dict[str, Any]]] = None
_CACHEABLE_TOOL_NAMES = {"mutate_components"}


def retrieve_tools(tools: List[Callable]) -> List[Dict[str, Any]]:
    """Convert tools to Anthropic format with prompt caching enabled.

    Converts tools once and caches them for reuse across all LLM calls.
    Applies cache_control only to selected tools to stay under Anthropic limits.

    Args:
        tools: List of LangChain tool callables to convert.

    Returns:
        List of Anthropic tool schemas with cache_control configured.
    """
    global _ANTHROPIC_TOOLS_CACHE

    if _ANTHROPIC_TOOLS_CACHE is None:
        _ANTHROPIC_TOOLS_CACHE = [convert_to_anthropic_tool(tool) for tool in tools]

        for tool in _ANTHROPIC_TOOLS_CACHE:
            if tool.get("name") in _CACHEABLE_TOOL_NAMES:
                tool["cache_control"] = {"type": "ephemeral"}

    return _ANTHROPIC_TOOLS_CACHE


def generate_id() -> str:
    """Generate a unique ID for components and pages.

    Returns:
        str: A unique UUID in uppercase format.
    """
    return str(uuid.uuid4()).upper()


def get_default_page_path() -> Path:
    """Get the default path for the page.json file.

    Returns:
        Path: Path to the default page.json file in static/wsb directory.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    return project_root / "static" / "wsb" / "page.json"


def load_page(path: Path) -> Dict[str, Any]:
    """Load a page from the given path, creating a new one if it doesn't exist.

    Args:
        path: Path to the page.json file.

    Returns:
        Dict[str, Any]: The page data structure.
    """

    def _create_page() -> Dict[str, Any]:
        page_id = generate_id()
        template_id = generate_id()

        page = {
            "id": page_id,
            "type": "web.data.components.Page",
            "name": "Generated Page",
            "templateId": template_id,
            "items": [],
            "shareHeaderAndFirstSectionBgImg": False,
            "shareBgImgOffsetTop": 0,
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(page, indent=2))

        return page

    if path.exists():
        text = path.read_text()
        if text.strip():
            try:
                return json.loads(text)
            except (json.JSONDecodeError, ValueError):
                pass

    return _create_page()


def save_page(path: Path, page: Dict[str, Any]) -> None:
    """Save a page to the given path.

    Args:
        path: Path to save the page.json file.
        page: The page data structure to save.
    """
    path.write_text(json.dumps(page, indent=2))


def get_rel_parent_id(item: Dict[str, Any]) -> Optional[str]:
    """Return the parent id from relIn, if present."""
    rel_in = item.get("relIn")
    if isinstance(rel_in, dict):
        return rel_in.get("id")
    return None


def renumber_components(items: list[Dict[str, Any]]) -> None:
    """Recursively renumber orderIndex for all components.

    Ensures that all components have sequential orderIndex values
    starting from 0 within their sibling group.

    Args:
        items: List of components to renumber.
    """
    parent_buckets: dict[Optional[str], list[Dict[str, Any]]] = {}

    for item in items:
        parent_id = get_rel_parent_id(item)
        parent_buckets.setdefault(parent_id, []).append(item)
        if item.get("items"):
            renumber_components(item["items"])

    for siblings in parent_buckets.values():
        for idx, item in enumerate(siblings):
            item["orderIndex"] = idx


def find_component_by_id(
    items: list[Dict[str, Any]], component_id: str
) -> Optional[Dict[str, Any]]:
    """Depth-first search for a component by id."""
    for item in items:
        if item.get("id") == component_id:
            return item
        child = find_component_by_id(item.get("items", []), component_id)
        if child:
            return child
    return None


def insert_component(
    component: Dict[str, Any],
    page_items: list[Dict[str, Any]],
    parent_id: str | None = None,
    before_id: str | None = None,
    after_id: str | None = None,
) -> bool:
    """Insert a component into the page list.

    Components are kept in a flat list; relIn is used to indicate parent
    relationships for rendering and ordering.

    Args:
        component: Component dictionary to insert.
        page_items: Root-level page items list.
        parent_id: Optional parent component ID; sets relIn.id when provided.
        before_id: Optional sibling ID to insert before (global ordering).
        after_id: Optional sibling ID to insert after (global ordering).

    Returns:
        True if insertion was successful.
    """
    target_list = page_items
    if parent_id and not component.get("relIn"):
        component["relIn"] = {"id": parent_id}

    if before_id or after_id:
        for idx, item in enumerate(target_list):
            if item.get("id") == before_id:
                target_list.insert(idx, component)
                return True
            if item.get("id") == after_id:
                target_list.insert(idx + 1, component)
                return True

    target_list.append(component)
    return True
