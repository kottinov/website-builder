"""Tools exposed to the LangGraph agent, including WSB JSON manipulation."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from langchain.tools import tool

from react_agent.utils import (
    generate_id,
    get_default_page_path,
    insert_component,
    load_page,
    renumber_components,
    save_page,
)

from react_agent.signatures import CreateInput
from react_agent.builder import build_component

from react_agent.descriptions import CREATE_TOOL_DESCRIPTION


def list(file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return a flat list of components with id, kind, orderIndex, parentId, title."""
    page = load_page(Path(file_path) if file_path else get_default_page_path())
    result: List[Dict[str, Any]] = []

    def walk(items: List[Dict[str, Any]], parent_id: Optional[str]) -> None:
        for item in items:
            result.append(
                {
                    "id": item.get("id"),
                    "kind": item.get("type"),
                    "orderIndex": item.get("orderIndex"),
                    "parentId": parent_id,
                    "title": item.get("title") or item.get("name"),
                }
            )
            if item.get("items"):
                walk(item["items"], item.get("id"))

    walk(page.get("items", []), None)
    return result


@tool(description=CREATE_TOOL_DESCRIPTION, args_schema=CreateInput)
def create(**kwargs) -> Dict[str, Any]:
    """Create a new WSB component and insert it into the page JSON.

    This function uses the bullet-proof builder to ensure:
    - Typed nested structures (relIn, mobileSettings, etc)
    - Only provided fields are included
    - Valid WSB JSON structure

    Args:
        **kwargs: Component data and insertion metadata matching CreateInput schema.

    Returns:
        The newly created component as a dictionary with all resolved fields.

    Raises:
        ValueError: If the component type is missing.
    """
    payload = CreateInput(**kwargs)

    page_path = Path(payload.file_path) if payload.file_path else get_default_page_path()
    
    page = load_page(page_path)
    new_id = payload.id or generate_id()

    new_component = build_component(payload, new_id)
    page_items = page.setdefault("items", [])

    insert_component(
        new_component,
        page_items,
        parent_id=payload.parent_id,
        before_id=payload.before_id,
        after_id=payload.after_id,
    )

    renumber_components(page_items)
    save_page(page_path, page)

    return new_component


def retrieve(file_path: str, component_id: str) -> Optional[Dict[str, Any]]:
    """Return a single component by id."""
    page = load_page(Path(file_path))

    def find(items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        for item in items:
            if item.get("id") == component_id:
                return item
            child = find(item.get("items", []))
            if child:
                return child
        return None

    return find(page.get("items", []))

def remove(file_path: str, component_id: str) -> bool:
    """Remove a component by id."""
    page_path = Path(file_path)
    page = load_page(page_path)
    
    removed = False

    def prune(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        nonlocal removed
        new_items = []
        for item in items:
            if item.get("id") == component_id:
                removed = True
                continue
            item["items"] = prune(item.get("items", []))
            new_items.append(item)
        return new_items

    page["items"] = prune(page.get("items", []))

    def renumber(items: List[Dict[str, Any]]) -> None:
        for idx, item in enumerate(items):
            item["orderIndex"] = idx
            if item.get("items"):
                renumber(item["items"])

    renumber(page["items"])
    save_page(page_path, page)
    return removed


def reorder(file_path: str, parent_id: Optional[str], order_ids: List[str]) -> List[Dict[str, Any]]:
    """Reorder children under a parent, or top-level if parent_id is None."""
    page_path = Path(file_path)
    page = load_page(page_path)

    def find_list(items: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        if parent_id is None:
            return items
        for item in items:
            if item.get("id") == parent_id:
                return item.setdefault("items", [])
            sub = find_list(item.get("items", []))
            if sub is not None:
                return sub
        return None

    target_list = find_list(page.get("items", []))
    if target_list is None:
        return []

    id_to_item = {item.get("id"): item for item in target_list}
    new_list = [id_to_item[i] for i in order_ids if i in id_to_item]
    for item in target_list:
        if item not in new_list:
            new_list.append(item)
    for idx, item in enumerate(new_list):
        item["orderIndex"] = idx
    if parent_id is None:
        page["items"] = new_list
    else:
        def set_list(items: List[Dict[str, Any]]) -> bool:
            for item in items:
                if item.get("id") == parent_id:
                    item["items"] = new_list
                    return True
                if set_list(item.get("items", [])):
                    return True
            return False

        set_list(page["items"])

    save_page(page_path, page)
    return new_list


def find(file_path: str, text: str) -> List[Dict[str, Any]]:
    """Locate components whose visible text contains a substring."""
    page = load_page(Path(file_path))
    hits: List[Dict[str, Any]] = []
    needle = text.lower()

    def walk(items: List[Dict[str, Any]]) -> None:
        for item in items:
            for key in ("text", "content", "title", "name"):
                val = item.get(key)
                if isinstance(val, str) and needle in val.lower():
                    hits.append({"id": item.get("id"), "kind": item.get("type"), "matchField": key})
                    break
            if item.get("items"):
                walk(item["items"])

    walk(page.get("items", []))
    return hits


TOOLS: List[Callable[..., Any]] = [
    create,
    list,
    retrieve,
    remove,
    reorder,
    find,
]
