"""Tools exposed to the LangGraph agent, including WSB JSON manipulation."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from langchain.tools import tool

from react_agent.builder import build_component, normalize_style_fields
from react_agent.descriptions import (
    CREATE_TOOL_DESCRIPTION,
    EDIT_TOOL_DESCRIPTION,
    FIND_TOOL_DESCRIPTION,
    LIST_TOOL_DESCRIPTION,
    REMOVE_TOOL_DESCRIPTION,
    REORDER_TOOL_DESCRIPTION,
    RETRIEVE_TOOL_DESCRIPTION,
)
from react_agent.signatures import (
    CreateInput,
    EditInput,
    FindInput,
    ListInput,
    RelIn,
    RemoveInput,
    ReorderInput,
    RetrieveInput,
)
from react_agent.utils import (
    find_component_by_id,
    generate_id,
    get_default_page_path,
    get_rel_parent_id,
    insert_component,
    load_page,
    renumber_components,
    save_page,
)

EDIT_EXCLUDE_FIELDS = {"component_id", "file_path", "kind", "response_format"}
EDIT_VALIDATION_FIELDS = {
    name
    for name in CreateInput.model_fields
    if name
    not in {"file_path", "parent_id", "before_id", "after_id", "kind", "response_format"}
}


def _format_component_response(
    component: Dict[str, Any], response_format: str | None
) -> Dict[str, Any]:
    """Return a concise or detailed component representation."""
    fmt = (response_format or "concise").lower()
    if fmt == "detailed":
        return component
    parent_id = get_rel_parent_id(component)
    return {
        "id": component.get("id"),
        "kind": component.get("kind") or component.get("type"),
        "orderIndex": component.get("orderIndex"),
        "parentId": parent_id,
        "title": component.get("title")
        or component.get("name")
        or component.get("text")
        or component.get("content"),
    }


@tool(description=LIST_TOOL_DESCRIPTION, args_schema=ListInput)
def list(file_path: str | None = None) -> List[Dict[str, Any]]:
    """Return a flat list of components with id, kind, orderIndex, parentId, title."""
    page = load_page(Path(file_path) if file_path else get_default_page_path())
    result: List[Dict[str, Any]] = []

    def walk(items: List[Dict[str, Any]], parent_id: str | None) -> None:
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
    def _strip_cdata(value: Any) -> Any:
        if isinstance(value, str):
            trimmed = value.strip()
            if trimmed.startswith("<![CDATA[") and trimmed.endswith("]]>"):
                return trimmed[len("<![CDATA[") : -len("]]>")]
        return value

    if "content" in kwargs:
        kwargs["content"] = _strip_cdata(kwargs.get("content"))

    page_path = (
        Path(kwargs.get("file_path"))
        if kwargs.get("file_path")
        else get_default_page_path()
    )

    page = load_page(page_path)
    rel_in_kw = kwargs.get("relIn")

    if (
        kwargs.get("parent_id") is None
        and isinstance(rel_in_kw, dict)
        and rel_in_kw.get("id")
    ):
        kwargs["parent_id"] = rel_in_kw["id"]

    # default header id for wsb templates ( first section )
    DEFAULT_HEADER_ID = "22FC8C5B-CD71-42B7-9DF2-486F577581A9"

    if kwargs.get("kind") == "SECTION":
        kwargs["relIn"] = None

        if kwargs.get("relTo") is None:
            existing_sections = [
                item
                for item in page.get("items", [])
                if (item.get("kind") or item.get("type")) == "SECTION"
            ]
            if existing_sections:
                last_section = sorted(
                    existing_sections,
                    key=lambda s: s.get("orderIndex", -1),
                )[-1]
                gap = 0
                if (
                    last_section.get("top") is not None
                    and last_section.get("height") is not None
                    and kwargs.get("top") is not None
                ):
                    gap = kwargs["top"] - (last_section["top"] + last_section["height"])
                kwargs["relTo"] = {"id": last_section.get("id"), "below": gap}
            else:
                kwargs["relTo"] = {"id": DEFAULT_HEADER_ID, "below": 0}
        else:
            rel_to_provided = kwargs.get("relTo")
            if isinstance(rel_to_provided, dict):
                rel_to_id = rel_to_provided.get("id", "")
                fake_patterns = [
                    "temp",
                    "anchor",
                    "placeholder",
                    "dummy",
                    "fake",
                    "mock",
                ]
                if (
                    any(p in rel_to_id.lower() for p in fake_patterns)
                    and rel_to_id != DEFAULT_HEADER_ID
                ):
                    kwargs["relTo"] = {
                        "id": DEFAULT_HEADER_ID,
                        "below": rel_to_provided.get("below", 0),
                    }

    parent = None
    parent_id = kwargs.get("parent_id") or (
        rel_in_kw.get("id") if isinstance(rel_in_kw, dict) else None
    )

    if parent_id:
        parent = find_component_by_id(page.get("items", []), parent_id)
        if parent is None:
            raise ValueError(
                f"relIn/parent_id references unknown id '{parent_id}'. Use list() to pick an existing parent id."
            )

    if parent:
        rel_in = (
            dict(rel_in_kw)
            if isinstance(rel_in_kw, dict)
            else (rel_in_kw.model_dump() if rel_in_kw else {})
        )

        if rel_in.get("id") is None:
            rel_in["id"] = parent.get("id")

        left = kwargs.get("left")
        top = kwargs.get("top")
        width = kwargs.get("width")
        height = kwargs.get("height")

        if (
            rel_in.get("left") is None
            and left is not None
            and parent.get("left") is not None
        ):
            rel_in["left"] = left - parent["left"]

        if (
            rel_in.get("top") is None
            and top is not None
            and parent.get("top") is not None
        ):
            rel_in["top"] = top - parent["top"]

        if (
            rel_in.get("right") is None
            and width is not None
            and parent.get("width") is not None
            and rel_in.get("left") is not None
        ):
            rel_in["right"] = -(parent["width"] - (rel_in["left"] + width))

        if (
            rel_in.get("bottom") is None
            and height is not None
            and parent.get("height") is not None
            and rel_in.get("top") is not None
        ):
            rel_in["bottom"] = -(parent["height"] - (rel_in["top"] + height))

        kwargs["relIn"] = rel_in

    rel_to_kw = kwargs.get("relTo")

    if rel_to_kw and isinstance(rel_to_kw, dict):
        rel_to_target = rel_to_kw.get("id")
        is_section = kwargs.get("kind") == "SECTION"
        is_template_id = rel_to_target == DEFAULT_HEADER_ID

        if rel_to_target and not is_section and not is_template_id:
            if find_component_by_id(page.get("items", []), rel_to_target) is None:
                raise ValueError(
                    f"relTo references unknown id '{rel_to_target}'. Use list() to pick an existing sibling/section id."
                )

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

    new_id = payload.id or generate_id()

    new_component = build_component(payload, new_id)
    page_items = page.setdefault("items", [])

    insert_component(
        new_component,
        page_items,
        parent_id=None,
        before_id=payload.before_id,
        after_id=payload.after_id,
    )

    renumber_components(page_items)
    save_page(page_path, page)

    return _format_component_response(new_component, payload.response_format)


@tool(description=RETRIEVE_TOOL_DESCRIPTION, args_schema=RetrieveInput)
def retrieve(
    component_id: str,
    file_path: str | None = None,
    response_format: str = "concise",
) -> Dict[str, Any] | None:
    """Return a single component by id."""
    page_path = Path(file_path) if file_path else get_default_page_path()
    page = load_page(page_path)

    component = find_component_by_id(page.get("items", []), component_id)
    if component is None:
        return None
    return _format_component_response(component, response_format)


@tool(description=REMOVE_TOOL_DESCRIPTION, args_schema=RemoveInput)
def remove(component_id: str, file_path: str | None = None) -> bool:
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
def edit(**kwargs: Any) -> Dict[str, Any] | None:
    """Apply a partial update to an existing component."""
    payload = EditInput(**kwargs)
    page_path = (
        Path(payload.file_path) if payload.file_path else get_default_page_path()
    )
    page = load_page(page_path)

    target = find_component_by_id(page.get("items", []), payload.component_id)
    if target is None:
        return None

    kind_value = target.get("kind") or target.get("type")
    if not kind_value:
        raise ValueError("Target component missing kind/type; cannot validate update.")

    if payload.kind and payload.kind != kind_value:
        raise ValueError(
            f"Kind mismatch: target has '{kind_value}', got '{payload.kind}'."
        )

    updates = payload.model_dump(
        exclude_none=True,
        exclude=EDIT_EXCLUDE_FIELDS,
    )
    normalize_style_fields(updates)
    target.update(updates)
    normalize_style_fields(target)

    validation_payload: Dict[str, Any] = {
        field: target[field]
        for field in EDIT_VALIDATION_FIELDS
        if field in target and target[field] is not None
    }
    validation_payload["kind"] = kind_value

    CreateInput(**validation_payload)
    save_page(page_path, page)

    return _format_component_response(target, payload.response_format)


@tool(description=REORDER_TOOL_DESCRIPTION, args_schema=ReorderInput)
def reorder(
    order_ids: List[str],
    parent_id: str | None = None,
    file_path: str | None = None,
    response_format: str = "concise",
) -> List[Dict[str, Any]]:
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

    return [
        _format_component_response(item, response_format) for item in new_list
    ]


@tool(description=FIND_TOOL_DESCRIPTION, args_schema=FindInput)
def find(text: str, file_path: str | None = None) -> List[Dict[str, Any]]:
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
