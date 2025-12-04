"""Consolidated tools for WSB component manipulation (v2 architecture).

This module provides two main tools following Codex's design:
1. get_components: Flexible querying with filtering and projection
2. mutate_components: Batch mutations (create/edit/remove/reorder)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain.tools import tool

from react_agent.builder import build_component, normalize_style_fields
from react_agent.positioning import calculate_auto_position
from react_agent.signatures import (
    CreateInput,
    EditInput,
    GetComponentsInput,
    MutateComponentsInput,
    MutateOperation,
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

DEFAULT_HEADER_ID = "22FC8C5B-CD71-42B7-9DF2-486F577581A9"


GET_COMPONENTS_DESCRIPTION = """Query components with flexible filtering and output control.

Returns component data based on filters. Defaults to concise summaries (id, kind, orderIndex, parentId, title).

FILTERS (all optional, combine as needed):
- ids: Specific component IDs
- parent_id: Children of a parent (null for top-level)
- kinds: Component types (e.g., ["SECTION", "TEXT"])
- text_contains: Search text/content/title/name fields

OUTPUT CONTROL:
- response_format: "concise" (default) or "detailed" (full JSON)
- fields: Custom field list (e.g., ["id", "kind"]) overrides response_format

EXAMPLES:
- All sections: kinds=["SECTION"]
- Section children: parent_id="ABC-123"
- Search text: text_contains="pricing"
- Specific IDs: ids=["ABC-123", "DEF-456"]
- Minimal output: fields=["id"]
"""


MUTATE_COMPONENTS_DESCRIPTION = """Apply batch create/edit/remove/reorder operations.

Executes operations sequentially, returning results for each.

OPERATION TYPES:

1. CREATE: {"op": "create", "payload": {...}, "auto_position": {...}}
   - payload: CreateInput fields (kind, width, height, content, etc.)
   - auto_position (optional): Automatic positioning helper
     * parent_id: Parent component ID
     * strategy: "below_last_child" | "above_first_child" | "centered" | "fill_width" | "stack_below"
     * sibling_id: Required for "stack_below"
     * gap_px: Spacing (default 0)
     * Requires width and height in payload and a real parent_id (no blanks/placeholder; use manual coords for sections)
   - If auto_position is used, relIn/relTo are calculated automatically; relIn/relTo you supply are ignored

2. EDIT: {"op": "edit", "id": "...", "payload": {...}}
   - id: Component to update
   - payload: Fields to change (partial update)

3. REMOVE: {"op": "remove", "id": "..."}
   - id: Component to delete (includes children)

4. REORDER: {"op": "reorder", "parent_id": "...", "order_ids": [...]}
   - parent_id: Parent whose children to reorder (null for top-level)
   - order_ids: New order of component IDs

CRITICAL LAYOUT RULES (flat structure):
- All components live in flat items[] array
- SECTIONS: relIn=null, relTo chains to previous section
- CHILDREN: relIn links to parent, relTo (optional) chains to sibling
- Use auto_position to avoid manual relIn/relTo math

REQUIRED FIELDS for CREATE:
- kind, left, top, width, height (or use auto_position to fill left/top/relIn/relTo)
- SECTIONS: selectedGradientTheme=null
- TEXT: verticalAlignment, globalStyleId, mobileSettings, styles=[], paras=[], links=[], text=""
- BUTTON: style (with globalId/globalName/type), buttonThemeSelected
- Backgrounds: use style.background as either a CSS string (e.g., "linear-gradient(...)") or a dict (colorData/assetData/angle/colorStops); plain background strings are accepted
- relIn must be an object with id/offsets (never just a string id). For children without auto_position: relIn.id=parent_id and include left/top offsets.
- For auto_position children: provide parent_id and width/height; relIn is computed. Sections must set relIn=null and relTo to chain manually.
- Sections without relTo will auto-chain to the template header anchor id.
- Sections without relTo will auto-chain to the template header anchor id.

RESPONSE:
- response_format: "concise" (default, id+status) or "detailed" (full component)
- Returns list of results matching operations order

EXAMPLES:
- Create section + child: [
    {"op": "create", "payload": {"kind": "SECTION", ...}},
    {"op": "create", "payload": {"kind": "TEXT", ...}, "auto_position": {"parent_id": "...", "strategy": "below_last_child"}}
  ]
- Edit then reorder: [
    {"op": "edit", "id": "ABC-123", "payload": {"width": 500}},
    {"op": "reorder", "parent_id": "DEF-456", "order_ids": ["ABC-123", "GHI-789"]}
  ]
"""


def _format_component(
    component: Dict[str, Any],
    response_format: str,
    fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Format component output based on response_format and fields."""
    if fields:
        return {k: component.get(k) for k in fields}

    if response_format == "detailed":
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


@tool(description=GET_COMPONENTS_DESCRIPTION, args_schema=GetComponentsInput)
def get_components(
    file_path: str | None = None,
    ids: List[str] | None = None,
    parent_id: str | None = None,
    kinds: List[str] | None = None,
    text_contains: str | None = None,
    response_format: str = "concise",
    fields: List[str] | None = None,
) -> List[Dict[str, Any]]:
    """Query components with flexible filtering and output control."""
    page_path = Path(file_path) if file_path else get_default_page_path()
    page = load_page(page_path)

    all_components: List[Dict[str, Any]] = []

    def walk(items: List[Dict[str, Any]]) -> None:
        for item in items:
            all_components.append(item)
            if item.get("items"):
                walk(item["items"])

    walk(page.get("items", []))

    filtered = all_components

    if ids is not None:
        id_set = set(ids)
        filtered = [c for c in filtered if c.get("id") in id_set]

    if parent_id is not None:
        filtered = [c for c in filtered if get_rel_parent_id(c) == parent_id]

    if kinds is not None:
        kind_set = set(kinds)
        filtered = [
            c for c in filtered
            if (c.get("kind") or c.get("type")) in kind_set
        ]

    if text_contains is not None:
        needle = text_contains.lower()
        filtered = [
            c for c in filtered
            if any(
                needle in str(c.get(field, "")).lower()
                for field in ["text", "content", "title", "name"]
            )
        ]

    return [_format_component(c, response_format, fields) for c in filtered]


@tool(description=MUTATE_COMPONENTS_DESCRIPTION, args_schema=MutateComponentsInput)
def mutate_components(
    file_path: str | None = None,
    operations: List[Dict[str, Any]] = None,
    response_format: str = "concise",
) -> List[Dict[str, Any]]:
    """Apply batch create/edit/remove/reorder operations."""
    if operations is None:
        operations = []

    page_path = Path(file_path) if file_path else get_default_page_path()
    page = load_page(page_path)
    results = []
    last_created_id: str | None = None
    last_created_section_id: str | None = None

    for op_data in operations:
        # Handle both dict and already-parsed MutateOperation
        if isinstance(op_data, MutateOperation):
            op = op_data
        else:
            op = MutateOperation(**op_data)

        try:
            if op.op == "create":
                # Auto-fill parent_id for auto_position when user omitted it but we have a recent section
                if op.auto_position:
                    if not op.auto_position.parent_id:
                        if last_created_section_id:
                            op.auto_position.parent_id = last_created_section_id
                        else:
                            raise ValueError(
                                "auto_position requires parent_id of an existing parent (no blank/placeholder). "
                                "Create a parent section first in this batch or set auto_position.parent_id to a real section id from get_components."
                            )

                new_component, result = _execute_create(op, page, response_format)
                last_created_id = new_component.get("id")
                kind_value = new_component.get("kind") or new_component.get("type")
                if kind_value == "SECTION":
                    last_created_section_id = last_created_id
            elif op.op == "edit":
                result = _execute_edit(op, page, response_format)
            elif op.op == "remove":
                result = _execute_remove(op, page, response_format)
            elif op.op == "reorder":
                result = _execute_reorder(op, page, response_format)
            else:
                result = {"error": f"Unknown operation: {op.op}"}

            results.append(result)

        except Exception as e:
            results.append({"op": op.op, "error": str(e)})

    save_page(page_path, page)

    return results


def _execute_create(
    op: MutateOperation,
    page: Dict[str, Any],
    response_format: str,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Execute create operation."""
    if not op.payload:
        raise ValueError("Create operation requires payload")

    payload_dict = dict(op.payload)

    if op.auto_position:
        auto_pos = op.auto_position
        width = payload_dict.get("width")
        height = payload_dict.get("height")

        if not width or not height:
            raise ValueError("auto_position requires width and height in payload")

        rel_in, rel_to = calculate_auto_position(auto_pos, page, width, height)

        payload_dict["relIn"] = rel_in.model_dump() if rel_in else None
        payload_dict["relTo"] = rel_to.model_dump() if rel_to else None
        payload_dict["parent_id"] = auto_pos.parent_id

    if payload_dict.get("kind") == "SECTION":
        rel_to_kw = payload_dict.get("relTo")
        rel_to_id = rel_to_kw.get("id") if isinstance(rel_to_kw, dict) else None
        if rel_to_kw is None or not rel_to_id:
            payload_dict["relTo"] = {"id": DEFAULT_HEADER_ID, "below": 0}

    if "content" in payload_dict:
        content = payload_dict["content"]
        if isinstance(content, str):
            trimmed = content.strip()
            if trimmed.startswith("<![CDATA[") and trimmed.endswith("]]>"):
                payload_dict["content"] = trimmed[len("<![CDATA[") : -len("]]>")]

    create_input = CreateInput(**payload_dict)
    new_id = create_input.id or generate_id()
    new_component = build_component(create_input, new_id)

    page_items = page.setdefault("items", [])
    insert_component(
        new_component,
        page_items,
        parent_id=None,
        before_id=create_input.before_id,
        after_id=create_input.after_id,
    )

    renumber_components(page_items)

    return new_component, _format_component(new_component, response_format)


def _execute_edit(
    op: MutateOperation,
    page: Dict[str, Any],
    response_format: str,
) -> Dict[str, Any]:
    """Execute edit operation."""
    if not op.id:
        raise ValueError("Edit operation requires id")

    if not op.payload:
        raise ValueError("Edit operation requires payload")

    target = find_component_by_id(page.get("items", []), op.id)
    if not target:
        return {"op": "edit", "id": op.id, "error": "Component not found"}

    kind_value = target.get("kind") or target.get("type")
    if not kind_value:
        raise ValueError("Target component missing kind/type")

    updates = dict(op.payload)
    normalize_style_fields(updates)
    target.update(updates)
    normalize_style_fields(target)

    # Validate edited component against create schema to avoid drift
    validation_payload = {
        key: value
        for key, value in target.items()
        if key in CreateInput.model_fields and value is not None
    }
    validation_payload["kind"] = kind_value
    CreateInput(**validation_payload)

    return _format_component(target, response_format)


def _execute_remove(
    op: MutateOperation,
    page: Dict[str, Any],
    response_format: str,
) -> Dict[str, Any]:
    """Execute remove operation."""
    if not op.id:
        raise ValueError("Remove operation requires id")

    removed = False

    def prune(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        nonlocal removed
        new_items = []
        for item in items:
            if item.get("id") == op.id:
                removed = True
                continue
            item["items"] = prune(item.get("items", []))
            new_items.append(item)
        return new_items

    page["items"] = prune(page.get("items", []))
    renumber_components(page["items"])

    return {
        "op": "remove",
        "id": op.id,
        "success": removed,
    }


def _execute_reorder(
    op: MutateOperation,
    page: Dict[str, Any],
    response_format: str,
) -> Dict[str, Any]:
    """Execute reorder operation."""
    if not op.order_ids:
        raise ValueError("Reorder operation requires order_ids")

    def matches_parent(item: Dict[str, Any]) -> bool:
        rel_parent = get_rel_parent_id(item)
        return rel_parent == op.parent_id if op.parent_id is not None else rel_parent is None

    target_list = [item for item in page.get("items", []) if matches_parent(item)]
    if not target_list:
        return {"op": "reorder", "parent_id": op.parent_id, "result": []}

    id_to_item = {item.get("id"): item for item in target_list}
    new_list = [id_to_item[i] for i in op.order_ids if i in id_to_item]

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

    return {
        "op": "reorder",
        "parent_id": op.parent_id,
        "result": [_format_component(item, response_format) for item in new_list],
    }


TOOLS_V2 = [get_components, mutate_components]
