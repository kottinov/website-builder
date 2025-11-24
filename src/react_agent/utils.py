"""Utility & helper functions."""

import json
import uuid

from pathlib import Path
from typing import Any, Dict

from langchain.chat_models import init_chat_model
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
    return init_chat_model(model, model_provider=provider)

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


def renumber_components(items: list[Dict[str, Any]]) -> None:
    """Recursively renumber orderIndex for all components.

    Ensures that all components have sequential orderIndex values
    starting from 0 within their sibling group.

    Args:
        items: List of components to renumber.
    """
    for idx, item in enumerate(items):
        item["orderIndex"] = idx
        if item.get("items"):
            renumber_components(item["items"])


def insert_component(
    component: Dict[str, Any],
    page_items: list[Dict[str, Any]],
    parent_id: str | None = None,
    before_id: str | None = None,
    after_id: str | None = None,
) -> bool:
    """Insert a component into the page hierarchy.

    Handles three insertion modes:
        1. Nested insertion: If parent_id is provided, insert into parent's items
        2. Positional insertion: If before_id/after_id provided, insert at position
        3. Default insertion: Append to the end of target list

    Args:
        component: Component dictionary to insert.
        page_items: Root-level page items list.
        parent_id: Optional parent component ID to nest under.
        before_id: Optional sibling ID to insert before.
        after_id: Optional sibling ID to insert after.

    Returns:
        True if insertion was successful.
    """
    target_list = page_items

    if parent_id:
        def find_parent(items: list[Dict[str, Any]]) -> list[Dict[str, Any]] | None:
            for item in items:
                if item.get("id") == parent_id:
                    return item.setdefault("items", [])
                if item.get("items"):
                    result = find_parent(item["items"])
                    if result is not None:
                        return result
            return None

        found_parent = find_parent(page_items)
        if found_parent is not None:
            target_list = found_parent

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
