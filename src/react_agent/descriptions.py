"""Tool descriptions for the React agent.

This module contains detailed descriptions for each tool, providing guidance
to the LLM on how to use them correctly.
"""

CREATE_TOOL_DESCRIPTION = """Create stunning WSB components with smart defaults and professional structure.

COMPONENT TYPES & AUTO-DEFAULTS:
- SECTION: Full-width layout sections (auto: stretch=true, selectedTheme="White", pin=0, mobile responsive)
- CONTAINER: Flexible layout boxes for nested content
- TEXT: Typography elements (auto: fontSize=16, lineHeight=1.5)
- BUTTON: Interactive buttons (auto: rounded corners, bold text)
- IMAGE, SVG, LOGO, etc.

TWO LAYOUT PATTERNS:

Pattern A - Simple Nesting (for cards, components):
  kind="CONTAINER", width=300, height=400, background="#fff", padding={"top":20,"left":20,"right":20,"bottom":20}
  └─ Use parent_id to nest children
  └─ Use left/top/width/height for positioning

Pattern B - Section-Based (for full pages):
  kind="SECTION", title="Hero", height=700, selectedTheme="Main"
  └─ Use relTo={"id":"previous-section-id","below":0} to stack sections vertically
  └─ Children use relIn={"id":"section-id","left":100,"top":50} for absolute positioning within section

KEY FEATURES:
- Smart defaults per component type (override any default explicitly)
- Professional theming: selectedTheme="Main"|"White"|"Dark"
- Relational positioning: relTo (stack sections), relIn (position in section)
- Mobile responsive: mobileSettings, stretch, mobileHide
- Rich styling: style, corners, padding, border, gradient, shadows

EXAMPLES:

Professional section:
  kind="SECTION", title="Hero", height=700, background="#f5f5f5"

Pricing card:
  kind="CONTAINER", width=300, background="#fff", padding={"top":30,"bottom":30,"left":20,"right":20},
  corners={"radius":8}, border={"width":1,"color":"#ddd"}

Styled text:
  kind="TEXT", content="<h2>Title</h2>", fontSize=36, bold=true, color="#333"

Call-to-action button:
  kind="BUTTON", text="Get Started", background="#007bff", color="#fff", width=200, height=50
"""

LIST_TOOL_DESCRIPTION = """List components in the current page JSON so you can reference ids and hierarchy when editing.

Returns a flat array with:
- id: unique component id (use to target future edits)
- kind: component kind (SECTION, CONTAINER, TEXT, BUTTON, etc.)
- orderIndex: sibling order within its parent
- parentId: id of the parent component (null for top-level sections)
- title: human-friendly label (title/name/text/content fallback)

Usage: call first to discover component ids before retrieve/update/remove.

Examples:
- Get top-level sections: call with no params; filter by parentId=null.
- Get children under a specific section: call list, find the section id, then filter rows with that parentId.
- Identify a button to update: call list, look for title or kind="BUTTON" rows, grab the id."""

RETRIEVE_TOOL_DESCRIPTION = """Fetch a single component (with its children) by id from the page JSON.

Inputs:
- component_id: required id of the component (use the list tool first to find ids)
- file_path: optional path to the page JSON; defaults to static/wsb/page.json

Returns:
- The full component dict, including nested items if it is a container/section.
- null if the id is not found.

Examples:
- Fetch a section for inspection: component_id="97175A3B-27F1-4784-A9CC-83DBAFD25393"
- Fetch a nested button to edit text/color: component_id="5D1A5A7E-8B9F-4354-A5FB-45FEB435E259"
- When unsure of ids: call list first, then retrieve with the chosen id."""

REMOVE_TOOL_DESCRIPTION = """Delete a component (and its children) from the page JSON by id.

Inputs:
- component_id: required id of the component to delete (use list to find ids)
- file_path: optional path to the page JSON; defaults to static/wsb/page.json

Behavior:
- Removes the target component and any nested items (works for top-level or deeply nested children; parent stays intact).
- Renumbers remaining siblings' orderIndex to stay sequential.
- Returns true if something was removed, false if the id was not found.

Examples:
- Remove an unused section: component_id="97175A3B-27F1-4784-A9CC-83DBAFD25393"
- Remove a button inside a card (parent remains): component_id="5D1A5A7E-8B9F-4354-A5FB-45FEB435E259"
- Delete a specific text block inside a container without touching siblings: component_id="<text-id-from-list>"
- No-op if id is wrong: returns false; call list/find first to validate.
- Safety flow: call list to confirm the id, then call remove with that id."""

REORDER_TOOL_DESCRIPTION = """Reorder siblings under a parent (or top-level) by providing the desired id order.

Inputs:
- order_ids: required list of component ids in the new order (ids not included stay appended)
- parent_id: optional parent component id; use null/omit for top-level sections
- file_path: optional path to the page JSON; defaults to static/wsb/page.json

Behavior:
- Rebuilds the sibling list in the provided order, then renumbers orderIndex sequentially.
- Returns the updated list of components under that parent.
- Ignores unknown ids in order_ids; if parent_id is not found, returns [] unchanged.

Examples:
- Reorder top-level sections: parent_id=null, order_ids=["550E2D25-41EE-4C5E-8ABA-D102FE0A624A", "97175A3B-27F1-4784-A9CC-83DBAFD25393"]
- Reorder cards inside a section: parent_id="<section-id>", order_ids=["A02D5E8D-F51F-452B-A5F7-A2D5D0FD348E", "550E2D25-41EE-4C5E-8ABA-D102FE0A624A"]
- Keep unspecified siblings: omit their ids and they will stay appended in original order."""

FIND_TOOL_DESCRIPTION = """Search for components whose visible text contains a substring (case-insensitive).

Inputs:
- text: substring to search for in text/content/title/name fields
- file_path: optional path to the page JSON; defaults to static/wsb/page.json

Returns:
- Array of hits with: id, kind, matchField (text|content|title|name)

Examples:
- Find pricing labels: text="per month"
- Find call-to-action buttons: text="get started"
- Find a specific plan name: text="Pro"
- Note: matches raw HTML inside content (e.g., <h3>Pro</h3>), so include expected text only.
- Workflow: call find to get ids, then retrieve to inspect or remove to delete."""

EDIT_TOOL_DESCRIPTION = """Edit an existing component by applying a partial update (only provided fields change).

Inputs:
- component_id: required id of the component to modify (use list/find to get it)
- Inline fields to override (e.g., width, height, color, background, text, content, fontSize, padding, border, corners, relIn, relTo, mobileSettings)
- file_path: optional path to the page JSON; defaults to static/wsb/page.json

Behavior:
- Shallow merges the provided fields into the target component; leaves other fields (including children) untouched.
- Does not allow changing id or insertion-related fields; kind must match if provided.
- Validates against the create schema to avoid invalid WSB keys.

Examples:
- Change button label and colors: component_id="<button-id>", text="Buy now", background="#111", color="#fff"
- Resize a container: component_id="<container-id>", width=400, height=420, padding={"top":32,"left":24,"right":24,"bottom":32}
- Reposition within a section: component_id="<card-id>", relIn={"id":"<section-id>","left":120,"top":80}"""
