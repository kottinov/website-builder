"""WSB Component Builder following the Builder design pattern.

This module provides a builder class for constructing valid WSB component JSON
structures with proper validation and field mapping.
"""

from typing import Any, Dict, List, Optional
from react_agent.signatures import CreateInput

STYLE_FIELDS = {
    "style",
    "styles",
    "hover",
    "onHover",
    "press",
    "imageStyle",
    "captionBoxStyle",
    "captionTitleTextStyle",
    "captionDescriptionTextStyle",
    "captionStyle",
    "textStyleMeta",
}


def _camelize_css_key(key: str) -> str:
    """Convert kebab/underscore CSS keys to camelCase for React inline styles."""
    if not isinstance(key, str):
        return key
    sanitized = key.replace("_", "-")
    parts = sanitized.split("-")
    if len(parts) == 1:
        return key
    return parts[0] + "".join(part.capitalize() for part in parts[1:] if part)


def _camelize_style_value(value: Any) -> Any:
    """Recursively camelCase dict keys used in style fragments."""
    if isinstance(value, dict):
        return {
            _camelize_css_key(k): _camelize_style_value(v)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [_camelize_style_value(v) for v in value]
    return value


def normalize_style_fields(component: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize style-ish fields to React-friendly camelCase keys."""
    for field in STYLE_FIELDS:
        if field not in component:
            continue
        field_value = component[field]
        if field == "styles" and isinstance(field_value, list):
            component[field] = [
                _camelize_style_value(entry) if isinstance(entry, dict) else entry
                for entry in field_value
            ]
        elif isinstance(field_value, dict):
            component[field] = _camelize_style_value(field_value)
    return component


def get_component_defaults(kind: str) -> Dict[str, Any]:
    """Get smart defaults based on component kind.

    Returns minimal sensible defaults for basic functionality.
    The LLM is responsible for providing complete component specifications
    based on the tool descriptions and examples.

    Args:
        kind: Component kind (SECTION, CONTAINER, TEXT, BUTTON, etc.)

    Returns:
        Dictionary of default field values
    """
    defaults: Dict[str, Any] = {}

    if kind == "SECTION":
        defaults.update({
            "stretch": True,
            "pin": 0,
            "selectedTheme": "White",
            "selectedGradientTheme": None,
            "selectedBorderTheme": None,
            "mobileSettings": {"size": "cover"}
        })

    elif kind == "CONTAINER":
        defaults.update({
            "wrap": False
        })

    elif kind == "TEXT":
        defaults.update({
            "fontSize": 16,
            "lineHeight": 1.5,
            "text": "",
            "styles": [],
            "paras": [],
            "links": [],
            "mobileDown": False,
            "mobileHide": False,
            "mobileSettings": {"align": None, "font": 0},
            "verticalAlignment": "top",
            "globalStyleId": "GLOBAL_TEXT_STYLE_DEFAULT",
            "themeShadowBlurRadius": 3,
            "themeShadowOffsetX": 3,
            "themeShadowOffsetY": 3,
            "themeShadowColor": None,
        })

    elif kind == "BUTTON":
        defaults.update({
            "corners": {"radius": 5},
            "fontSize": 16,
            "bold": True,
            "mobileDown": False,
            "mobileHide": False,
            "mobileSettings": {"align": "justify"},
            "buttonThemeSelected": "primary",
            "style": {
                "border": None,
                "background": None,
                "globalId": "BUTTON_STYLE_DEFAULT",
                "globalName": "[button.default]",
                "type": "web.data.styles.StyleButton",
                "text": {"size": None},
            },
        })

    return defaults


class WSBComponentBuilder:
    """Builder for creating valid WSB component JSON structures.

    Follows the Builder pattern to construct complex WSB components with proper:
    - Field name mapping (type -> kind)
    - Typed nested structures conversion
    - Required field validation
    - Optional field handling

    Example:
        builder = WSBComponentBuilder(component_id="ABC-123")
        builder.set_core_fields("TEXT", False, False)
        builder.add_content(content="<p>Hello</p>", text="Hello")
        component = builder.build()
    """

    def __init__(self, component_id: str) -> None:
        """Initialize builder with component ID.

        Args:
            component_id: Unique identifier for the component
        """
        self._component_id = component_id
        self.reset()

    def reset(self) -> None:
        """Reset builder to initial state with required fields."""
        self._component: Dict[str, Any] = {
            "id": self._component_id,
            "kind": None, 
            "inTemplate": False,
            "orderIndex": None,
            "wrap": False,
        }

    def set_core_fields(
        self, kind: str, in_template: bool, wrap: bool
    ) -> "WSBComponentBuilder":
        """Set required core fields.

        Args:
            kind: Component kind identifier
            in_template: Whether component belongs to template
            wrap: Wrap flag for containers

        Returns:
            Self for method chaining
        """
        self._component["kind"] = kind
        self._component["inTemplate"] = in_template
        self._component["wrap"] = wrap

        return self

    def add_layout(
        self,
        left: Optional[int] = None,
        top: Optional[int] = None,
        right: Optional[int] = None,
        bottom: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> "WSBComponentBuilder":
        """Add layout positioning fields.

        Args:
            left: Left position in pixels
            top: Top position in pixels
            right: Right position in pixels
            bottom: Bottom position in pixels
            width: Width in pixels
            height: Height in pixels

        Returns:
            Self for method chaining
        """
        if left is not None:
            self._component["left"] = left
        if top is not None:
            self._component["top"] = top
        if right is not None:
            self._component["right"] = right
        if bottom is not None:
            self._component["bottom"] = bottom
        if width is not None:
            self._component["width"] = width
        if height is not None:
            self._component["height"] = height
        return self

    def add_relational(
        self,
        rel_in: Any = None,
        rel_to: Any = None,
        rel_page: Any = None,
        rel_para: Any = None,
    ) -> "WSBComponentBuilder":
        """Add relational positioning fields.

        Converts Pydantic models to dicts for JSON serialization.
        ALWAYS includes all four fields (relIn, relTo, relPage, relPara),
        setting them to null if not provided - this matches WSB's expected format.

        Args:
            rel_in: Relative positioning to parent
            rel_to: Relative positioning to sibling
            rel_page: Page-level positioning
            rel_para: Paragraph-level positioning

        Returns:
            Self for method chaining
        """
        self._component["relIn"] = (
            rel_in if isinstance(rel_in, dict) else (rel_in.model_dump(mode="json") if rel_in else None)
        )

        self._component["relTo"] = (
            rel_to if isinstance(rel_to, dict) else (rel_to.model_dump(mode="json") if rel_to else None)
        )

        self._component["relPage"] = (
            rel_page if isinstance(rel_page, dict) else (rel_page.model_dump(mode="json") if rel_page else None)
        )

        self._component["relPara"] = (
            rel_para if isinstance(rel_para, dict) else (rel_para.model_dump(mode="json") if rel_para else None)
        )

        return self

    def add_content(
        self,
        content: Optional[str] = None,
        text: Optional[str] = None,
        title: Optional[str] = None,
        name: Optional[str] = None,
    ) -> "WSBComponentBuilder":
        """Add content fields.

        Args:
            content: HTML content
            text: Plain text content
            title: Title or label
            name: Component name

        Returns:
            Self for method chaining
        """
        if content is not None:
            self._component["content"] = content
        if text is not None:
            self._component["text"] = text
        if title is not None:
            self._component["title"] = title
        if name is not None:
            self._component["name"] = name

        return self

    def add_items(
        self, items: Optional[List[Dict[str, Any]]] = None
    ) -> "WSBComponentBuilder":
        """Add child items for container components.

        Args:
            items: List of child component dictionaries

        Returns:
            Self for method chaining
        """
        if items is not None:
            self._component["items"] = items

        return self

    def add_field(self, key: str, value: Any) -> "WSBComponentBuilder":
        """Add arbitrary field.

        Use this for fields not covered by specific methods.

        Args:
            key: Field name
            value: Field value

        Returns:
            Self for method chaining
        """
        if value is not None:
            self._component[key] = value

        return self

    def add_fields(self, fields: Dict[str, Any]) -> "WSBComponentBuilder":
        """Add multiple fields at once.

        Args:
            fields: Dictionary of field name to value mappings

        Returns:
            Self for method chaining
        """
        for key, value in fields.items():
            if value is not None:
                self._component[key] = value

        return self

    def build(self) -> Dict[str, Any]:
        """Build and return the final component.

        Returns:
            Valid WSB component dictionary

        Raises:
            ValueError: If required fields are missing
        """
        if self._component["kind"] is None:
            raise ValueError("Component 'kind' (type) must be set before building")

        component = self._component
        self.reset()

        return component


def build_component(payload: CreateInput, component_id: str) -> Dict[str, Any]:
    """Build a valid WSB component JSON from CreateInput.

    This function acts as a director, orchestrating the builder to construct
    a complete WSB component from the validated input.

    Applies smart defaults based on component kind, which can be overridden
    by explicitly provided values.

    Args:
        payload: The validated CreateInput with component data
        component_id: The generated or provided component ID

    Returns:
        Valid WSB component dictionary ready for insertion

    Example output:
        {
            "id": "ABC-123",
            "kind": "TEXT",
            "inTemplate": false,
            "orderIndex": null,
            "wrap": false,
            "items": [],
            "content": "<p>Hello</p>",
            "text": "Hello",
            "relIn": {
                "id": "parent-id",
                "left": 100,
                "top": 50,
                "right": null,
                "bottom": 0
            }
        }
    """
    builder = WSBComponentBuilder(component_id)
    defaults = get_component_defaults(payload.kind)

    builder.add_fields(defaults)

    builder.set_core_fields(payload.kind, payload.inTemplate, payload.wrap)

    builder.add_layout(
        left=payload.left,
        top=payload.top,
        right=payload.right,
        bottom=payload.bottom,
        width=payload.width,
        height=payload.height,
    )

    builder.add_relational(
        rel_in=payload.relIn,
        rel_to=payload.relTo,
        rel_page=payload.relPage,
        rel_para=payload.relPara,
    )

    builder.add_content(
        content=payload.content,
        text=payload.text,
        title=payload.title,
        name=payload.name,
    )

    builder.add_items(payload.items)

    remaining_fields = payload.model_dump(
        exclude={
            "file_path", "parent_id", "before_id", "after_id",
            "id", "kind", "inTemplate", "orderIndex", "wrap",
            "left", "top", "right", "bottom", "width", "height",
            "relIn", "relTo", "relPage", "relPara",
            "content", "text", "title", "name",
            "items",
            "response_format",
        },
        exclude_unset=True,
        mode="json",
    )

    builder.add_fields(remaining_fields)

    component = builder.build()
    normalize_style_fields(component)
    return component
