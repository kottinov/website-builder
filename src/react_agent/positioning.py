"""Automatic positioning helpers for component creation.

This module provides smart positioning strategies that calculate relIn/relTo
values automatically, reducing the cognitive load on agents.
"""

from typing import Any, Dict, List, Optional

from react_agent.signatures import AutoPosition, RelIn, RelTo
from react_agent.utils import find_component_by_id, get_rel_parent_id


def calculate_auto_position(
    auto_pos: AutoPosition,
    page: Dict[str, Any],
    component_width: int,
    component_height: int,
) -> tuple[Optional[RelIn], Optional[RelTo]]:
    """Calculate relIn and relTo based on auto-positioning strategy.

    Args:
        auto_pos: AutoPosition configuration
        page: Page JSON data
        component_width: Width of component being positioned
        component_height: Height of component being positioned

    Returns:
        Tuple of (relIn, relTo) for the component

    Raises:
        ValueError: If parent not found or strategy requirements not met
    """
    parent = find_component_by_id(page.get("items", []), auto_pos.parent_id)
    if not parent:
        raise ValueError(f"Parent component '{auto_pos.parent_id}' not found")

    parent_width = parent.get("width", 0)
    parent_height = parent.get("height", 0)
    parent_left = parent.get("left", 0)
    parent_top = parent.get("top", 0)

    strategy = auto_pos.strategy
    gap_px = auto_pos.gap_px

    if strategy == "below_last_child":
        return _position_below_last_child(
            parent, page, parent_left, parent_top, parent_width, parent_height,
            component_width, component_height, gap_px
        )

    elif strategy == "above_first_child":
        return _position_above_first_child(
            parent, page, parent_left, parent_top, parent_width, parent_height,
            component_width, component_height, gap_px
        )

    elif strategy == "centered":
        return _position_centered(
            parent, parent_left, parent_top, parent_width, parent_height,
            component_width, component_height
        )

    elif strategy == "fill_width":
        return _position_fill_width(
            parent, parent_left, parent_top, parent_width, parent_height,
            component_height, gap_px
        )

    elif strategy == "stack_below":
        if not auto_pos.sibling_id:
            raise ValueError("stack_below strategy requires sibling_id")
        return _position_stack_below(
            parent, page, auto_pos.sibling_id, parent_left, parent_top,
            parent_width, parent_height, component_width, component_height, gap_px
        )

    raise ValueError(f"Unknown positioning strategy: {strategy}")


def _get_children(parent: Dict[str, Any], page: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get all children of a parent component."""
    parent_id = parent.get("id")
    children = []

    def walk(items: List[Dict[str, Any]]) -> None:
        for item in items:
            rel_parent = get_rel_parent_id(item)
            if rel_parent == parent_id:
                children.append(item)
            if item.get("items"):
                walk(item["items"])

    walk(page.get("items", []))
    return children


def _position_below_last_child(
    parent: Dict[str, Any],
    page: Dict[str, Any],
    parent_left: int,
    parent_top: int,
    parent_width: int,
    parent_height: int,
    component_width: int,
    component_height: int,
    gap_px: int,
) -> tuple[RelIn, Optional[RelTo]]:
    """Position component below the last child (or at top if no children)."""
    children = _get_children(parent, page)

    if not children:
        # First child - position at top of parent
        rel_in = RelIn(
            id=parent.get("id"),
            left=0,
            top=gap_px,
            right=-(parent_width - component_width),
            bottom=-(parent_height - gap_px - component_height)
        )
        return rel_in, None

    # Find last child by bottom position
    last_child = max(children, key=lambda c: (c.get("top", 0) + c.get("height", 0)))
    last_child_bottom = last_child.get("top", 0) + last_child.get("height", 0)

    # Position below last child
    new_top = last_child_bottom + gap_px
    rel_in = RelIn(
        id=parent.get("id"),
        left=0,
        top=new_top - parent_top,
        right=-(parent_width - component_width),
        bottom=-(parent_height - (new_top - parent_top) - component_height)
    )

    rel_to = RelTo(id=last_child.get("id"), below=gap_px)

    return rel_in, rel_to


def _position_above_first_child(
    parent: Dict[str, Any],
    page: Dict[str, Any],
    parent_left: int,
    parent_top: int,
    parent_width: int,
    parent_height: int,
    component_width: int,
    component_height: int,
    gap_px: int,
) -> tuple[RelIn, None]:
    """Position component above the first child (at top of parent)."""
    rel_in = RelIn(
        id=parent.get("id"),
        left=0,
        top=gap_px,
        right=-(parent_width - component_width),
        bottom=-(parent_height - gap_px - component_height)
    )
    return rel_in, None


def _position_centered(
    parent: Dict[str, Any],
    parent_left: int,
    parent_top: int,
    parent_width: int,
    parent_height: int,
    component_width: int,
    component_height: int,
) -> tuple[RelIn, None]:
    """Position component centered within parent."""
    left_offset = (parent_width - component_width) // 2
    top_offset = (parent_height - component_height) // 2

    rel_in = RelIn(
        id=parent.get("id"),
        left=left_offset,
        top=top_offset,
        right=-(parent_width - left_offset - component_width),
        bottom=-(parent_height - top_offset - component_height)
    )
    return rel_in, None


def _position_fill_width(
    parent: Dict[str, Any],
    parent_left: int,
    parent_top: int,
    parent_width: int,
    parent_height: int,
    component_height: int,
    gap_px: int,
) -> tuple[RelIn, None]:
    """Position component to fill parent width (with gap margin)."""
    rel_in = RelIn(
        id=parent.get("id"),
        left=gap_px,
        top=gap_px,
        right=-gap_px,
        bottom=-(parent_height - gap_px - component_height)
    )
    return rel_in, None


def _position_stack_below(
    parent: Dict[str, Any],
    page: Dict[str, Any],
    sibling_id: str,
    parent_left: int,
    parent_top: int,
    parent_width: int,
    parent_height: int,
    component_width: int,
    component_height: int,
    gap_px: int,
) -> tuple[RelIn, RelTo]:
    """Position component below a specific sibling."""
    sibling = find_component_by_id(page.get("items", []), sibling_id)
    if not sibling:
        raise ValueError(f"Sibling component '{sibling_id}' not found")

    # Verify sibling is actually a child of the same parent
    sibling_parent = get_rel_parent_id(sibling)
    if sibling_parent != parent.get("id"):
        raise ValueError(
            f"Sibling '{sibling_id}' is not a child of parent '{parent.get('id')}'"
        )

    sibling_bottom = sibling.get("top", 0) + sibling.get("height", 0)
    new_top = sibling_bottom + gap_px

    rel_in = RelIn(
        id=parent.get("id"),
        left=sibling.get("left", 0) - parent_left,
        top=new_top - parent_top,
        right=-(parent_width - component_width - (sibling.get("left", 0) - parent_left)),
        bottom=-(parent_height - (new_top - parent_top) - component_height)
    )

    rel_to = RelTo(id=sibling_id, below=gap_px)

    return rel_in, rel_to
