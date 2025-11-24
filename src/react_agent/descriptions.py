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