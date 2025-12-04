"""Tools exposed to the LangGraph agent, including WSB JSON manipulation."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from langchain.tools import tool

from react_agent.utils import (
    generate_id,
    get_default_page_path,
    find_component_by_id,
    get_rel_parent_id,
    insert_component,
    load_page,
    renumber_components,
    save_page,
)

from react_agent.signatures import (
    CreateInput,
    EditInput,
    FindInput,
    ListInput,
    RelIn,
    ReorderInput,
    RetrieveInput,
    RemoveInput,
)
from react_agent.builder import build_component

from react_agent.descriptions import (
    CREATE_TOOL_DESCRIPTION,
    EDIT_TOOL_DESCRIPTION,
    FIND_TOOL_DESCRIPTION,
    LIST_TOOL_DESCRIPTION,
    REMOVE_TOOL_DESCRIPTION,
    REORDER_TOOL_DESCRIPTION,
    RETRIEVE_TOOL_DESCRIPTION,
)

EDIT_EXCLUDE_FIELDS = {"component_id", "file_path", "kind"}
EDIT_VALIDATION_FIELDS = {
    name
    for name in CreateInput.model_fields
    if name not in {"file_path", "parent_id", "before_id", "after_id", "kind"}
}


@tool(description=LIST_TOOL_DESCRIPTION, args_schema=ListInput)
def list(file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return a flat list of components with id, kind, orderIndex, parentId, title."""
    page = load_page(Path(file_path) if file_path else get_default_page_path())
    result: List[Dict[str, Any]] = []

    def walk(items: List[Dict[str, Any]], parent_id: Optional[str]) -> None:
        for item in items:
            kind = item.get("kind") or item.get("type")
            rel_parent = get_rel_parent_id(item)
            result.append(
                {
                    "id": item.get("id"),
                    "kind": kind,
                    "orderIndex": item.get("orderIndex"),
                    "parentId": rel_parent or parent_id,
                    "title": item.get("title")
                    or item.get("name")
                    or item.get("text")
                    or item.get("content"),
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
    updates: Dict[str, Any] = {}

    if payload.parent_id and payload.relIn is None:
        updates["relIn"] = RelIn(id=payload.parent_id)

    if payload.relTo is None:
        if payload.after_id:
            updates["relTo"] = {"id": payload.after_id, "below": 0}
        elif payload.before_id:
            updates["relTo"] = {"id": payload.before_id, "below": 0}

    if updates:
        payload = payload.model_copy(update=updates)

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


@tool(description=RETRIEVE_TOOL_DESCRIPTION, args_schema=RetrieveInput)
def retrieve(component_id: str, file_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Return a single component by id."""
    page_path = Path(file_path) if file_path else get_default_page_path()
    page = load_page(page_path)

    return find_component_by_id(page.get("items", []), component_id)

@tool(description=REMOVE_TOOL_DESCRIPTION, args_schema=RemoveInput)
def remove(component_id: str, file_path: Optional[str] = None) -> bool:
    """Remove a component by id."""
    page_path = Path(file_path) if file_path else get_default_page_path()
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

    renumber_components(page["items"])
    save_page(page_path, page)
    return removed


@tool(description=EDIT_TOOL_DESCRIPTION, args_schema=EditInput)
def edit(**kwargs: Any) -> Optional[Dict[str, Any]]:
    """Apply a partial update to an existing component."""
    payload = EditInput(**kwargs)
    page_path = Path(payload.file_path) if payload.file_path else get_default_page_path()
    page = load_page(page_path)

    target = find_component_by_id(page.get("items", []), payload.component_id)
    if target is None:
        return None

    kind_value = target.get("kind") or target.get("type")
    if not kind_value:
        raise ValueError("Target component missing kind/type; cannot validate update.")

    if payload.kind and payload.kind != kind_value:
        raise ValueError(f"Kind mismatch: target has '{kind_value}', got '{payload.kind}'.")

    updates = payload.model_dump(
        exclude_none=True,
        exclude=EDIT_EXCLUDE_FIELDS,
    )
    target.update(updates)

    validation_payload: Dict[str, Any] = {
        field: target[field]
        for field in EDIT_VALIDATION_FIELDS
        if field in target and target[field] is not None
    }
    validation_payload["kind"] = kind_value

    CreateInput(**validation_payload)
    save_page(page_path, page)
    return target


@tool(description=REORDER_TOOL_DESCRIPTION, args_schema=ReorderInput)
def reorder(order_ids: List[str], parent_id: Optional[str] = None, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Reorder children under a parent, or top-level if parent_id is None."""
    page_path = Path(file_path) if file_path else get_default_page_path()
    page = load_page(page_path)

    def matches_parent(item: Dict[str, Any]) -> bool:
        rel_parent = get_rel_parent_id(item)
        return rel_parent == parent_id if parent_id is not None else rel_parent is None

    target_list = [item for item in page.get("items", []) if matches_parent(item)]
    if not target_list:
        return []

    id_to_item = {item.get("id"): item for item in target_list}
    new_list = [id_to_item[i] for i in order_ids if i in id_to_item]
    for item in target_list:
        if item not in new_list:
            new_list.append(item)
    for idx, item in enumerate(new_list):
        item["orderIndex"] = idx
    sibling_ids = {item.get("id") for item in target_list}
    new_items: List[Dict[str, Any]] = []
    new_iter = iter(new_list)
    for item in page.get("items", []):
        if item.get("id") in sibling_ids:
            new_items.append(next(new_iter))
        else:
            new_items.append(item)

    page["items"] = new_items

    renumber_components(page["items"])
    save_page(page_path, page)
    return new_list


@tool(description=FIND_TOOL_DESCRIPTION, args_schema=FindInput)
def find(text: str, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Locate components whose visible text contains a substring."""
    page = load_page(Path(file_path) if file_path else get_default_page_path())
    hits: List[Dict[str, Any]] = []
    needle = text.lower()

    def walk(items: List[Dict[str, Any]]) -> None:
        for item in items:
            for key in ("text", "content", "title", "name"):
                val = item.get(key)
                if isinstance(val, str) and needle in val.lower():
                    hits.append(
                        {
                            "id": item.get("id"),
                            "kind": item.get("kind") or item.get("type"),
                            "matchField": key,
                        }
                    )
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
    edit,
    reorder,
    find,
]
