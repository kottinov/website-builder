"""Tools exposed to the LangGraph agent, including WSB JSON manipulation."""

from pathlib import Path
from typing import Any, Callable, Dict, List

from langchain.tools import tool

from react_agent.descriptions import (
    FIND_TOOL_DESCRIPTION,
    LIST_TOOL_DESCRIPTION,
    MUTATE_TOOL_DESCRIPTION,
    RETRIEVE_TOOL_DESCRIPTION,
)
from react_agent.signatures import (
    FindInput,
    ListInput,
    MutateInput,
    Operation,
    RetrieveInput,
)
from react_agent.utils import (
    execute_create_operation,
    execute_edit_operation,
    execute_remove_operation,
    execute_reorder_operation,
    find_component_by_id,
    flatten_components_list,
    format_component_response,
    generate_id,
    get_default_page_path,
    load_page,
    renumber_components,
    resolve_alias_references,
    save_page,
    search_components_by_text,
)


@tool(description=LIST_TOOL_DESCRIPTION, args_schema=ListInput)
def list_components(file_path: str | None = None) -> List[Dict[str, Any]]:
    """Return a flat list of components with id, kind, orderIndex, parentId, title."""
    page = load_page(Path(file_path) if file_path else get_default_page_path())
    return flatten_components_list(page.get("items", []))


@tool(description=RETRIEVE_TOOL_DESCRIPTION, args_schema=RetrieveInput)
def retrieve_component(
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

    return format_component_response(component, response_format)


@tool(description=FIND_TOOL_DESCRIPTION, args_schema=FindInput)
def find_component(text: str, file_path: str | None = None) -> List[Dict[str, Any]]:
    """Locate components whose visible text contains a substring."""
    page = load_page(Path(file_path) if file_path else get_default_page_path())
    return search_components_by_text(page.get("items", []), text)


@tool(description=MUTATE_TOOL_DESCRIPTION, args_schema=MutateInput)
def mutate_components(
    operations: List[Any],
    file_path: str | None = None,
    response_format: str = "concise",
) -> List[Dict[str, Any]]:
    """Execute multiple CREATE and EDIT operations in a single batch.

    This tool optimizes token usage by allowing multiple component mutations
    in one tool call instead of separate calls. Operations are executed
    sequentially with fail-fast behavior: if any operation fails, the entire
    batch is rolled back and no changes are saved.

    Args:
        operations: List of operation payloads, each with {op: "CREATE"|"EDIT", payload: {...}}
        file_path: Optional path to page JSON; defaults to static/wsb/page.json
        response_format: "concise" (default) or "detailed"

    Returns:
        List of results corresponding to each operation (same order as input)

    Raises:
        ValueError: If any operation fails validation or execution
    """
    page_path = Path(file_path) if file_path else get_default_page_path()
    page = load_page(page_path)

    results: List[Dict[str, Any]] = []
    normalized_ops: List[Dict[str, Any]] = []

    for idx, op_wrapper in enumerate(operations):
        op_type = op_wrapper.op if hasattr(op_wrapper, "op") else op_wrapper.get("op")
        op_payload = (
            op_wrapper.payload
            if hasattr(op_wrapper, "payload")
            else op_wrapper.get("payload")
        )

        alias = getattr(op_wrapper, "alias", None)
        if alias is None and isinstance(op_wrapper, dict):
            alias = op_wrapper.get("alias")

        if hasattr(op_payload, "model_dump"):
            payload_dict = op_payload.model_dump(exclude_none=True)
        else:
            payload_dict = dict(op_payload) if isinstance(op_payload, dict) else {}

        if "orderIds" in payload_dict and "order_ids" not in payload_dict:
            payload_dict["order_ids"] = payload_dict.pop("orderIds")

        normalized_ops.append(
            {"index": idx, "op": op_type, "payload": payload_dict, "alias": alias}
        )

    alias_map: Dict[str, str] = {}

    for op in normalized_ops:
        if op["op"] == Operation.CREATE or op["op"] == "CREATE":
            alias = op.get("alias")

            if alias:
                if alias in alias_map:
                    raise ValueError(
                        f"Duplicate alias '{alias}' at index {op['index']}"
                    )

            payload = op["payload"]
            explicit_id = payload.get("id")

            if explicit_id is None:
                explicit_id = generate_id()
                payload["id"] = explicit_id

            if alias:
                alias_map[alias] = explicit_id

    try:
        for op in normalized_ops:
            op_type = op["op"]
            payload_dict = op["payload"]

            for key in ("parent_id", "before_id", "after_id"):
                if key in payload_dict:
                    payload_dict[key] = resolve_alias_references(
                        payload_dict.get(key), alias_map
                    )

            rel_in_kw = payload_dict.get("relIn")

            if isinstance(rel_in_kw, dict) and "id" in rel_in_kw:
                rel_in_kw["id"] = resolve_alias_references(
                    rel_in_kw.get("id"), alias_map
                )
                payload_dict["relIn"] = rel_in_kw

            rel_to_kw = payload_dict.get("relTo")

            if isinstance(rel_to_kw, dict) and "id" in rel_to_kw:
                rel_to_kw["id"] = resolve_alias_references(
                    rel_to_kw.get("id"), alias_map
                )
                payload_dict["relTo"] = rel_to_kw

            if op_type == Operation.EDIT or op_type == "EDIT":
                payload_dict["component_id"] = resolve_alias_references(
                    payload_dict.get("component_id"), alias_map
                )
            elif op_type == Operation.REMOVE or op_type == "REMOVE":
                payload_dict["component_id"] = resolve_alias_references(
                    payload_dict.get("component_id"), alias_map
                )
            elif op_type == Operation.REORDER or op_type == "REORDER":
                payload_dict["parent_id"] = resolve_alias_references(
                    payload_dict.get("parent_id"), alias_map
                )
                order_ids = payload_dict.get("order_ids") or []
                payload_dict["order_ids"] = [
                    resolve_alias_references(oid, alias_map) for oid in order_ids
                ]

            payload_dict["file_path"] = str(page_path)
            payload_dict["response_format"] = response_format

            if op_type == Operation.CREATE or op_type == "CREATE":
                result = execute_create_operation(page, payload_dict, response_format)
                results.append(result)

            elif op_type == Operation.EDIT or op_type == "EDIT":
                result = execute_edit_operation(page, payload_dict, response_format)
                results.append(result)

            elif op_type == Operation.REMOVE or op_type == "REMOVE":
                result = execute_remove_operation(page, payload_dict)
                results.append(result)

            elif op_type == Operation.REORDER or op_type == "REORDER":
                result = execute_reorder_operation(page, payload_dict, response_format)
                results.append(result)

            else:
                raise ValueError(
                    f"Unknown operation type at index {op['index']}: {op_type}"
                )

        renumber_components(page.get("items", []))
        save_page(page_path, page)

        return results

    except Exception as e:
        raise ValueError(
            f"Batch operation failed: {str(e)}. All changes rolled back."
        ) from e


TOOLS: List[Callable[..., Any]] = [
    list_components,
    retrieve_component,
    find_component,
    mutate_components,
]
