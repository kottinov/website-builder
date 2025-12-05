"""Utility & helper functions."""

import json
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from langchain.chat_models import init_chat_model
from langchain_anthropic import convert_to_anthropic_tool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

from react_agent.builder import build_component, normalize_style_fields
from react_agent.constants import (
    CACHEABLE_TOOL_NAMES,
    DEFAULT_HEADER_ID,
    EDIT_EXCLUDE_FIELDS,
    EDIT_VALIDATION_FIELDS,
    FAKE_ID_PATTERNS,
)
from react_agent.signatures import (
    CreateInput,
    EditInput,
    RelIn,
    RemoveInput,
    ReorderInput,
)

_ANTHROPIC_TOOLS_CACHE: List[Dict[str, Any]] | None = None


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
            if tool.get("name") in CACHEABLE_TOOL_NAMES:
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


def build_component_index(items: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Build an index mapping component IDs to component objects.

    Args:
        items: List of component items to index.

    Returns:
        Dictionary mapping component ID to component object.
    """
    index: Dict[str, Dict[str, Any]] = {}

    def walk(current_items: List[Dict[str, Any]]) -> None:
        for item in current_items:
            item_id = item.get("id")
            if item_id:
                index[item_id] = item
            if item.get("items"):
                walk(item["items"])

    walk(items)
    return index


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


def format_component_response(
    component: Dict[str, Any], response_format: str | None
) -> Dict[str, Any]:
    """Return a concise or detailed component representation.

    Args:
        component: Component dictionary to format.
        response_format: "concise" (default) or "detailed".

    Returns:
        Formatted component dictionary.
    """
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


def prune_by_ids(page: Dict[str, Any], target_ids: set[str]) -> bool:
    """Remove components matching target_ids and any descendants referencing them via relIn.

    Args:
        page: Page data structure containing items to prune.
        target_ids: Set of component IDs to remove.

    Returns:
        True if any components were removed, False otherwise.
    """
    items = page.get("items", [])
    parent_map: Dict[Optional[str], List[str]] = {}

    def _build_parent_map(current_items: List[Dict[str, Any]]) -> None:
        for item in current_items:
            item_id = item.get("id")
            rel_parent = get_rel_parent_id(item)
            parent_map.setdefault(rel_parent, []).append(item_id)

            if item.get("items"):
                _build_parent_map(item["items"])

    _build_parent_map(items)

    ids_to_remove = set(target_ids)

    def _collect_descendants(parent_id: str) -> None:
        """Recursively mark all descendants of a removed component."""
        for child_id in parent_map.get(parent_id, []):
            if child_id not in ids_to_remove:
                ids_to_remove.add(child_id)
                _collect_descendants(child_id)

    for target_id in target_ids:
        _collect_descendants(target_id)

    removed_any = False

    def _prune(items_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        nonlocal removed_any
        new_items: List[Dict[str, Any]] = []

        for item in items_list:
            item["items"] = _prune(item.get("items", []))

            if item.get("id") in ids_to_remove:
                removed_any = True
                continue

            rel_parent = get_rel_parent_id(item)

            if rel_parent in ids_to_remove:
                removed_any = True
                continue

            new_items.append(item)

        return new_items

    new_items = _prune(items)
    page["items"] = new_items

    return removed_any


def resolve_alias_references(value: Any, alias_map: Dict[str, str]) -> Any:
    """Resolve alias to concrete ID if the value is an alias.

    Args:
        value: Value to resolve (may be an alias string or any other type).
        alias_map: Mapping from alias names to concrete IDs.

    Returns:
        Resolved ID if value was an alias, otherwise the original value.
    """
    if isinstance(value, str) and value in alias_map:
        return alias_map[value]
    return value


def flatten_components_list(
    items: List[Dict[str, Any]], parent_id: str | None = None
) -> List[Dict[str, Any]]:
    """Recursively flatten component tree into a list with concise info.

    Args:
        items: List of component items to flatten.
        parent_id: Optional parent ID for top-level items.

    Returns:
        Flattened list of components with id, kind, orderIndex, parentId, title.
    """
    result: List[Dict[str, Any]] = []

    def walk(current_items: List[Dict[str, Any]], current_parent: str | None) -> None:
        for item in current_items:
            kind = item.get("kind") or item.get("type")
            rel_parent = get_rel_parent_id(item)

            result.append(
                {
                    "id": item.get("id"),
                    "kind": kind,
                    "orderIndex": item.get("orderIndex"),
                    "parentId": rel_parent or current_parent,
                    "title": item.get("title")
                    or item.get("name")
                    or item.get("text")
                    or item.get("content"),
                }
            )
            if item.get("items"):
                walk(item["items"], item.get("id"))

    walk(items, parent_id)

    return result


def search_components_by_text(
    items: List[Dict[str, Any]], search_text: str
) -> List[Dict[str, Any]]:
    """Recursively search components for text matches in visible fields.

    Args:
        items: List of component items to search.
        search_text: Text to search for (case-insensitive).

    Returns:
        List of matching components with id, kind, and matchField.
    """
    hits: List[Dict[str, Any]] = []
    needle = search_text.lower()

    def walk(current_items: List[Dict[str, Any]]) -> None:
        for item in current_items:
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

    walk(items)
    return hits


def execute_create_operation(
    page: Dict[str, Any],
    kwargs: Dict[str, Any],
    response_format: str,
) -> Dict[str, Any]:
    """Execute a CREATE operation within a batch (no load/save).

    Args:
        page: Page data structure to modify.
        kwargs: Keyword arguments for creating the component.
        response_format: "concise" or "detailed".

    Returns:
        Formatted component response.

    Raises:
        ValueError: If validation fails or referenced IDs don't exist.
    """

    def _strip_cdata(value: Any) -> Any:
        if isinstance(value, str):
            trimmed = value.strip()
            if trimmed.startswith("<![CDATA[") and trimmed.endswith("]]>"):
                return trimmed[len("<![CDATA[") : -len("]]>")]
        return value

    if "content" in kwargs:
        kwargs["content"] = _strip_cdata(kwargs.get("content"))

    rel_in_kw = kwargs.get("relIn")

    if (
        kwargs.get("parent_id") is None
        and isinstance(rel_in_kw, dict)
        and rel_in_kw.get("id")
    ):
        kwargs["parent_id"] = rel_in_kw["id"]

    if kwargs.get("kind") == "SECTION":
        kwargs["relIn"] = None

        if kwargs.get("relTo") is None:
            existing_sections = [
                item
                for item in page.get("items", [])
                if (item.get("kind") or item.get("type")) == "SECTION"
            ]
            if existing_sections:
                last_section = max(
                    existing_sections,
                    key=lambda s: s.get("orderIndex", -1),
                )
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
                if (
                    any(p in rel_to_id.lower() for p in FAKE_ID_PATTERNS)
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

        top = kwargs.get("top")
        left = kwargs.get("left")
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

    return format_component_response(new_component, response_format)


def execute_edit_operation(
    page: Dict[str, Any],
    kwargs: Dict[str, Any],
    response_format: str,
) -> Dict[str, Any]:
    """Execute an EDIT operation within a batch (no load/save).

    Args:
        page: Page data structure to modify.
        kwargs: Keyword arguments for editing the component.
        response_format: "concise" or "detailed".

    Returns:
        Formatted component response.

    Raises:
        ValueError: If component not found or validation fails.
    """
    payload = EditInput(**kwargs)

    target = find_component_by_id(page.get("items", []), payload.component_id)
    if target is None:
        raise ValueError(f"Component not found: {payload.component_id}")

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

    return format_component_response(target, response_format)


def execute_remove_operation(
    page: Dict[str, Any],
    kwargs: Dict[str, Any],
) -> bool:
    """Execute a REMOVE operation within a batch (no load/save).

    Args:
        page: Page data structure to modify.
        kwargs: Keyword arguments containing component_id to remove.

    Returns:
        True if component was removed, False otherwise.
    """
    payload = RemoveInput(**kwargs)
    component_id = payload.component_id

    return prune_by_ids(page, {component_id})


def execute_reorder_operation(
    page: Dict[str, Any],
    kwargs: Dict[str, Any],
    response_format: str,
) -> List[Dict[str, Any]]:
    """Execute a REORDER operation within a batch (no load/save).

    Args:
        page: Page data structure to modify.
        kwargs: Keyword arguments containing parent_id and order_ids.
        response_format: "concise" or "detailed".

    Returns:
        List of reordered components in their new order.
    """
    payload = ReorderInput(**kwargs)

    def matches_parent(item: Dict[str, Any]) -> bool:
        rel_parent = get_rel_parent_id(item)

        return (
            rel_parent == payload.parent_id
            if payload.parent_id is not None
            else rel_parent is None
        )

    target_list = [item for item in page.get("items", []) if matches_parent(item)]

    if not target_list:
        return []

    id_to_item = {item.get("id"): item for item in target_list}
    new_list = [id_to_item[i] for i in payload.order_ids if i in id_to_item]

    reordered_ids = {item.get("id") for item in new_list}

    for item in target_list:
        if item.get("id") not in reordered_ids:
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

    return [format_component_response(item, response_format) for item in new_list]
