"""Pydantic schemas for WSB component creation and manipulation.

This module defines the data structures used by the React agent to create
and modify components in the Website Builder JSON format.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator


class RelIn(BaseModel):
    """Relative positioning within parent container.

    Defines how a component is positioned relative to its parent's boundaries.
    """
    id: str = Field(description="Parent container component ID.")
    left: Optional[int] = Field(default=None, description="Left offset from parent left edge.")
    top: Optional[int] = Field(default=None, description="Top offset from parent top edge.")
    right: Optional[int] = Field(default=None, description="Right offset from parent right edge.")
    bottom: Optional[int] = Field(default=None, description="Bottom offset from parent bottom edge.")

    class Config:
        extra = "forbid"


class RelTo(BaseModel):
    """Relative positioning to a sibling component.

    Positions this component relative to another sibling component.
    """
    id: str = Field(description="Target sibling component ID.")
    below: Optional[int] = Field(default=None, description="Vertical space below target component.")

    class Config:
        extra = "forbid"


class RelPage(BaseModel):
    """Page-level positioning relation.

    Defines positioning relative to the page itself.
    """
    class Config:
        extra = "allow"


class RelPara(BaseModel):
    """Paragraph-level positioning relation.

    Used for text components to position within paragraph flow.
    """
    index: int = Field(description="Paragraph index.")
    offset: int = Field(description="Character offset within paragraph.")

    class Config:
        extra = "forbid"


class MobileSettings(BaseModel):
    """Mobile-specific settings for responsive behavior."""
    align: Optional[str] = Field(default=None, description="Text alignment on mobile.")
    font: Optional[int] = Field(default=None, description="Font size index for mobile.")

    class Config:
        extra = "forbid"


class CreateComponent(BaseModel):
    """Component data payload for WSB component creation.

    Represents the core attributes of a Website Builder component including
    layout, styling, and hierarchical relationships. All fields are validated
    against the WSB schema to prevent hallucinations.
    """

    type: str = Field(description="WSB component type identifier (e.g., 'TEXT', 'IMAGE', 'BUTTON', 'CONTAINER').")

    id: Optional[str] = Field(default=None, description="Optional explicit id; if omitted a UUID is generated.")
    inTemplate: Optional[bool] = Field(default=False, description="Set true if component belongs to template.")
    orderIndex: Optional[int] = Field(default=None, description="Sibling order index (automatically set during insert).")
    wrap: Optional[bool] = Field(default=False, description="Enable wrapping behavior for container components.")
    items: Optional[List[Dict[str, Any]]] = Field(default=None, description="Child components (for containers).")

    left: Optional[int] = Field(default=None, description="Left position in pixels.")
    top: Optional[int] = Field(default=None, description="Top position in pixels.")
    right: Optional[int] = Field(default=None, description="Right position in pixels.")
    bottom: Optional[int] = Field(default=None, description="Bottom position in pixels.")
    width: Optional[int] = Field(default=None, description="Component width in pixels.")
    height: Optional[int] = Field(default=None, description="Component height in pixels.")
    relIn: Optional[RelIn] = Field(default=None, description="Relative positioning to parent container.")
    relTo: Optional[RelTo] = Field(default=None, description="Relative positioning to another sibling component.")
    relPage: Optional[RelPage] = Field(default=None, description="Page-level positioning relation.")
    relPara: Optional[RelPara] = Field(default=None, description="Paragraph-level positioning relation.")

    horizontalAlignment: Optional[str] = Field(default=None, description="Horizontal alignment (left, center, right).")
    verticalAlignment: Optional[str] = Field(default=None, description="Vertical alignment (top, center, bottom).")

    content: Optional[str] = Field(default=None, description="HTML content for text components.")
    text: Optional[str] = Field(default=None, description="Plain text content.")
    title: Optional[str] = Field(default=None, description="Title or label text.")
    name: Optional[str] = Field(default=None, description="Component name.")
    placeholder: Optional[str] = Field(default=None, description="Placeholder text for inputs.")
    placeholderText: Optional[str] = Field(default=None, description="Alternative placeholder text field.")

    font: Optional[str] = Field(default=None, description="Font family or font index.")
    fontFamily: Optional[str] = Field(default=None, description="Explicit font family name.")
    fontSize: Optional[int] = Field(default=None, description="Font size in pixels or points.")
    bold: Optional[bool] = Field(default=None, description="Bold text style.")
    italic: Optional[bool] = Field(default=None, description="Italic text style.")
    underline: Optional[bool] = Field(default=None, description="Underline text style.")
    letterSpacing: Optional[float] = Field(default=None, description="Letter spacing value.")
    lineHeight: Optional[float] = Field(default=None, description="Line height multiplier.")
    textStyle: Optional[str] = Field(default=None, description="Predefined text style identifier.")

    color: Optional[str] = Field(default=None, description="Text or foreground color.")
    background: Optional[str] = Field(default=None, description="Background color or gradient.")
    themeColor: Optional[str] = Field(default=None, description="Theme color identifier.")
    themeHighlightColor: Optional[str] = Field(default=None, description="Theme highlight color.")
    themeOverrideColor: Optional[str] = Field(default=None, description="Override theme color.")
    themeStyle: Optional[str] = Field(default=None, description="Theme style identifier.")
    themeShadowColor: Optional[str] = Field(default=None, description="Theme shadow color.")
    themeShadowBlurRadius: Optional[float] = Field(default=None, description="Shadow blur radius.")
    themeShadowOffsetX: Optional[float] = Field(default=None, description="Shadow horizontal offset.")
    themeShadowOffsetY: Optional[float] = Field(default=None, description="Shadow vertical offset.")

    style: Optional[Dict[str, Any]] = Field(default=None, description="CSS-like style properties.")
    styles: Optional[List[Any]] = Field(default=None, description="Array of style definitions.")
    styleType: Optional[str] = Field(default=None, description="Style type identifier.")
    opacity: Optional[float] = Field(default=None, description="Opacity value (0-1).")
    rotation: Optional[float] = Field(default=None, description="Rotation angle in degrees.")
    scale: Optional[float] = Field(default=None, description="Scale factor.")
    border: Optional[Dict[str, Any]] = Field(default=None, description="Border properties.")
    corners: Optional[Dict[str, Any]] = Field(default=None, description="Corner radius properties.")
    padding: Optional[Dict[str, Any]] = Field(default=None, description="Padding properties.")

    image: Optional[str] = Field(default=None, description="Image URL or identifier.")
    asset: Optional[str] = Field(default=None, description="Asset identifier.")
    assetData: Optional[Dict[str, Any]] = Field(default=None, description="Asset metadata.")
    cropLeft: Optional[float] = Field(default=None, description="Image crop left offset.")
    cropTop: Optional[float] = Field(default=None, description="Image crop top offset.")
    scaleStrategy: Optional[str] = Field(default=None, description="Image scaling strategy.")
    lightBoxEnabled: Optional[bool] = Field(default=None, description="Enable lightbox for images.")

    link: Optional[str] = Field(default=None, description="Link URL.")
    linkAction: Optional[str] = Field(default=None, description="Link action type.")
    linkId: Optional[str] = Field(default=None, description="Link target component ID.")
    openInNewWindow: Optional[bool] = Field(default=None, description="Open link in new window.")
    openLink: Optional[str] = Field(default=None, description="Link opening behavior.")

    mobileDown: Optional[bool] = Field(default=None, description="Push content down on mobile.")
    mobileHide: Optional[bool] = Field(default=None, description="Hide component on mobile.")
    mobileSettings: Optional[MobileSettings] = Field(default=None, description="Mobile-specific settings.")
    mobileFontSize: Optional[int] = Field(default=None, description="Font size for mobile.")
    mobileSize: Optional[str] = Field(default=None, description="Size configuration for mobile.")
    mobileHorizontalAlignment: Optional[str] = Field(default=None, description="Horizontal alignment on mobile.")

    animated: Optional[bool] = Field(default=None, description="Enable animation.")
    animation: Optional[str] = Field(default=None, description="Animation type or configuration.")
    scrollEffect: Optional[str] = Field(default=None, description="Scroll-triggered effect.")
    hover: Optional[Dict[str, Any]] = Field(default=None, description="Hover state properties.")
    onHover: Optional[Dict[str, Any]] = Field(default=None, description="On hover behavior.")
    press: Optional[Dict[str, Any]] = Field(default=None, description="Press/click state properties.")

    rawSvg: Optional[str] = Field(default=None, description="Raw SVG markup.")
    svgJson: Optional[Dict[str, Any]] = Field(default=None, description="SVG structure as JSON.")
    viewBox: Optional[str] = Field(default=None, description="SVG viewBox attribute.")

    hidden: Optional[bool] = Field(default=None, description="Hide component.")
    show: Optional[bool] = Field(default=None, description="Show component.")
    spacing: Optional[float] = Field(default=None, description="Spacing value.")
    size: Optional[str] = Field(default=None, description="Size configuration.")
    position: Optional[str] = Field(default=None, description="Position type (absolute, relative, etc).")
    repeat: Optional[bool] = Field(default=None, description="Repeat pattern.")
    gradient: Optional[Dict[str, Any]] = Field(default=None, description="Gradient configuration.")
    seo: Optional[Dict[str, Any]] = Field(default=None, description="SEO metadata.")

    bbox: Optional[Dict[str, Any]] = Field(default=None, description="Bounding box coordinates (bottom, left, right, top).")
    selectedTheme: Optional[str] = Field(default=None, description="Selected theme name (e.g., 'Main', 'White', 'Dark').")
    selectedGradientTheme: Optional[str] = Field(default=None, description="Selected gradient theme name.")
    stretch: Optional[bool] = Field(default=None, description="Stretch component to fill width (typically for SECTION).")
    pin: Optional[int] = Field(default=None, description="Pin component position (0 for unpinned).")
    colorType: Optional[str] = Field(default=None, description="Color type for theme adaptation (LIGHT, DARK).")

    class Config:
        extra = "forbid"


class ListInput(BaseModel):
    """Input schema for listing components from a WSB page."""
    file_path: Optional[str] = Field(
        default=None,
        description="Optional path to the page JSON; defaults to static/wsb/page.json.",
    )

    class Config:
        extra = "forbid"


class RetrieveInput(BaseModel):
    """Input schema for retrieving a single component by id."""
    file_path: Optional[str] = Field(
        default=None,
        description="Optional path to the page JSON; defaults to static/wsb/page.json.",
    )
    component_id: str = Field(description="The component id to retrieve.")

    class Config:
        extra = "forbid"


class RemoveInput(BaseModel):
    """Input schema for removing a component by id."""
    file_path: Optional[str] = Field(
        default=None,
        description="Optional path to the page JSON; defaults to static/wsb/page.json.",
    )
    component_id: str = Field(description="The component id to delete.")

    class Config:
        extra = "forbid"


class ReorderInput(BaseModel):
    """Input schema for reordering sibling components."""
    file_path: Optional[str] = Field(
        default=None,
        description="Optional path to the page JSON; defaults to static/wsb/page.json.",
    )
    parent_id: Optional[str] = Field(
        default=None,
        description="Parent component id whose children will be reordered; omit for top-level.",
    )
    order_ids: List[str] = Field(
        description="List of component ids in the desired order; missing ids stay appended in their previous relative order.",
    )

    class Config:
        extra = "forbid"


class FindInput(BaseModel):
    """Input schema for searching components by text."""
    file_path: Optional[str] = Field(
        default=None,
        description="Optional path to the page JSON; defaults to static/wsb/page.json.",
    )
    text: str = Field(description="Substring to search for (case-insensitive).")

    class Config:
        extra = "forbid"


class CreateInput(BaseModel):
    """Input schema for creating a new WSB component.

    Contains both the component data and insertion metadata (file path,
    parent relationship, and sibling positioning). Combines CreateComponent
    fields with insertion control fields.
    """

    file_path: Optional[str] = Field(
        default=None,
        description="Target page JSON path; defaults to static/wsb/page.json when omitted.",
    )

    parent_id: Optional[str] = Field(
        default=None,
        description="Optional parent component id to nest the new component under.",
    )

    before_id: Optional[str] = Field(
        default=None,
        description="Optional sibling id; insert new component immediately before this component.",
    )
    
    after_id: Optional[str] = Field(
        default=None,
        description="Optional sibling id; insert new component immediately after this component.",
    )

    kind: str = Field(description="WSB component kind identifier (e.g., 'TEXT', 'IMAGE', 'BUTTON', 'CONTAINER').")

    id: Optional[str] = Field(default=None, description="Optional explicit id; if omitted a UUID is generated.")
    inTemplate: Optional[bool] = Field(default=False, description="Set true if component belongs to template.")
    orderIndex: Optional[int] = Field(default=None, description="Sibling order index (automatically set during insert).")
    wrap: Optional[bool] = Field(default=False, description="Enable wrapping behavior for container components.")
    items: Optional[List[Dict[str, Any]]] = Field(default=None, description="Child components (for containers).")

    left: Optional[int] = Field(default=None, description="Left position in pixels.")
    top: Optional[int] = Field(default=None, description="Top position in pixels.")
    right: Optional[int] = Field(default=None, description="Right position in pixels.")
    bottom: Optional[int] = Field(default=None, description="Bottom position in pixels.")
    width: Optional[int] = Field(default=None, description="Component width in pixels.")
    height: Optional[int] = Field(default=None, description="Component height in pixels.")
    relIn: Optional[RelIn] = Field(default=None, description="Relative positioning to parent container.")
    relTo: Optional[RelTo] = Field(default=None, description="Relative positioning to another sibling component.")
    relPage: Optional[RelPage] = Field(default=None, description="Page-level positioning relation.")
    relPara: Optional[RelPara] = Field(default=None, description="Paragraph-level positioning relation.")

    horizontalAlignment: Optional[str] = Field(default=None, description="Horizontal alignment (left, center, right).")
    verticalAlignment: Optional[str] = Field(default=None, description="Vertical alignment (top, center, bottom).")

    content: Optional[str] = Field(default=None, description="HTML content for text components.")
    text: Optional[str] = Field(default=None, description="Plain text content.")
    title: Optional[str] = Field(default=None, description="Title or label text.")
    name: Optional[str] = Field(default=None, description="Component name.")
    placeholder: Optional[str] = Field(default=None, description="Placeholder text for inputs.")
    placeholderText: Optional[str] = Field(default=None, description="Alternative placeholder text field.")

    font: Optional[str] = Field(default=None, description="Font family or font index.")
    fontFamily: Optional[str] = Field(default=None, description="Explicit font family name.")
    fontSize: Optional[int] = Field(default=None, description="Font size in pixels or points.")
    bold: Optional[bool] = Field(default=None, description="Bold text style.")
    italic: Optional[bool] = Field(default=None, description="Italic text style.")
    underline: Optional[bool] = Field(default=None, description="Underline text style.")
    letterSpacing: Optional[float] = Field(default=None, description="Letter spacing value.")
    lineHeight: Optional[float] = Field(default=None, description="Line height multiplier.")
    textStyle: Optional[str] = Field(default=None, description="Predefined text style identifier.")

    color: Optional[str] = Field(default=None, description="Text or foreground color.")
    background: Optional[str] = Field(default=None, description="Background color or gradient.")
    themeColor: Optional[str] = Field(default=None, description="Theme color identifier.")
    themeHighlightColor: Optional[str] = Field(default=None, description="Theme highlight color.")
    themeOverrideColor: Optional[str] = Field(default=None, description="Override theme color.")
    themeStyle: Optional[str] = Field(default=None, description="Theme style identifier.")
    themeShadowColor: Optional[str] = Field(default=None, description="Theme shadow color.")
    themeShadowBlurRadius: Optional[float] = Field(default=None, description="Shadow blur radius.")
    themeShadowOffsetX: Optional[float] = Field(default=None, description="Shadow horizontal offset.")
    themeShadowOffsetY: Optional[float] = Field(default=None, description="Shadow vertical offset.")

    style: Optional[Dict[str, Any]] = Field(default=None, description="CSS-like style properties.")
    styles: Optional[List[Any]] = Field(default=None, description="Array of style definitions.")
    styleType: Optional[str] = Field(default=None, description="Style type identifier.")
    opacity: Optional[float] = Field(default=None, description="Opacity value (0-1).")
    rotation: Optional[float] = Field(default=None, description="Rotation angle in degrees.")
    scale: Optional[float] = Field(default=None, description="Scale factor.")
    border: Optional[Dict[str, Any]] = Field(default=None, description="Border properties.")
    corners: Optional[Dict[str, Any]] = Field(default=None, description="Corner radius properties.")
    padding: Optional[Dict[str, Any]] = Field(default=None, description="Padding properties.")

    image: Optional[str] = Field(default=None, description="Image URL or identifier.")
    asset: Optional[str] = Field(default=None, description="Asset identifier.")
    assetData: Optional[Dict[str, Any]] = Field(default=None, description="Asset metadata.")
    cropLeft: Optional[float] = Field(default=None, description="Image crop left offset.")
    cropTop: Optional[float] = Field(default=None, description="Image crop top offset.")
    scaleStrategy: Optional[str] = Field(default=None, description="Image scaling strategy.")
    lightBoxEnabled: Optional[bool] = Field(default=None, description="Enable lightbox for images.")

    link: Optional[str] = Field(default=None, description="Link URL.")
    linkAction: Optional[str] = Field(default=None, description="Link action type.")
    linkId: Optional[str] = Field(default=None, description="Link target component ID.")
    openInNewWindow: Optional[bool] = Field(default=None, description="Open link in new window.")
    openLink: Optional[str] = Field(default=None, description="Link opening behavior.")

    mobileDown: Optional[bool] = Field(default=None, description="Push content down on mobile.")
    mobileHide: Optional[bool] = Field(default=None, description="Hide component on mobile.")
    mobileSettings: Optional[MobileSettings] = Field(default=None, description="Mobile-specific settings.")
    mobileFontSize: Optional[int] = Field(default=None, description="Font size for mobile.")
    mobileSize: Optional[str] = Field(default=None, description="Size configuration for mobile.")
    mobileHorizontalAlignment: Optional[str] = Field(default=None, description="Horizontal alignment on mobile.")

    animated: Optional[bool] = Field(default=None, description="Enable animation.")
    animation: Optional[str] = Field(default=None, description="Animation type or configuration.")
    scrollEffect: Optional[str] = Field(default=None, description="Scroll-triggered effect.")
    hover: Optional[Dict[str, Any]] = Field(default=None, description="Hover state properties.")
    onHover: Optional[Dict[str, Any]] = Field(default=None, description="On hover behavior.")
    press: Optional[Dict[str, Any]] = Field(default=None, description="Press/click state properties.")

    rawSvg: Optional[str] = Field(default=None, description="Raw SVG markup.")
    svgJson: Optional[Dict[str, Any]] = Field(default=None, description="SVG structure as JSON.")
    viewBox: Optional[str] = Field(default=None, description="SVG viewBox attribute.")

    hidden: Optional[bool] = Field(default=None, description="Hide component.")
    show: Optional[bool] = Field(default=None, description="Show component.")
    spacing: Optional[float] = Field(default=None, description="Spacing value.")
    size: Optional[str] = Field(default=None, description="Size configuration.")
    position: Optional[str] = Field(default=None, description="Position type (absolute, relative, etc).")
    repeat: Optional[bool] = Field(default=None, description="Repeat pattern.")
    gradient: Optional[Dict[str, Any]] = Field(default=None, description="Gradient configuration.")
    seo: Optional[Dict[str, Any]] = Field(default=None, description="SEO metadata.")

    bbox: Optional[Dict[str, Any]] = Field(default=None, description="Bounding box coordinates (bottom, left, right, top).")
    selectedTheme: Optional[str] = Field(default=None, description="Selected theme name (e.g., 'Main', 'White', 'Dark').")
    selectedGradientTheme: Optional[str] = Field(default=None, description="Selected gradient theme name.")
    stretch: Optional[bool] = Field(default=None, description="Stretch component to fill width (typically for SECTION).")
    pin: Optional[int] = Field(default=None, description="Pin component position (0 for unpinned).")
    colorType: Optional[str] = Field(default=None, description="Color type for theme adaptation (LIGHT, DARK).")

    class Config:
        extra = "forbid"


class EditInput(CreateInput):
    """Input schema for editing an existing component using partial updates."""

    component_id: str = Field(description="The component id to edit.")
    file_path: Optional[str] = Field(
        default=None,
        description="Optional path to the page JSON; defaults to static/wsb/page.json.",
    )
    kind: Optional[str] = Field(
        default=None,
        description="Optional; if provided must match the target component kind.",
    )

    class Config:
        extra = "forbid"

    @model_validator(mode="after")
    def _forbid_insert_fields(self) -> "EditInput":
        forbidden = {
            "id": self.id,
            "parent_id": self.parent_id,
            "before_id": self.before_id,
            "after_id": self.after_id,
        }
        provided = [name for name, value in forbidden.items() if value is not None]
        if provided:
            raise ValueError(f"These fields are not editable: {provided}")
        return self
