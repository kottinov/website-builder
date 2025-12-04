from __future__ import annotations

"""Pydantic schemas for WSB component creation and manipulation.

This module defines the data structures used by the React agent to create
and modify components in the Website Builder JSON format.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, model_validator

# Generic JSON-friendly type to allow structured data without fully untyped schemas.
LooseJSON = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


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
    size: Optional[str] = Field(default=None, description="Background/size configuration on mobile.")
    columns: Optional[int] = Field(default=None, description="Column count for mobile grids/galleries.")
    spacingPx: Optional[int] = Field(default=None, description="Spacing in px for mobile grids/galleries.")

    class Config:
        extra = "forbid"


class PageLink(BaseModel):
    """Internal link reference used by linkAction."""
    type: str = Field(description="Link type (e.g., 'page').")
    value: str = Field(description="Target identifier (e.g., page id).")

    class Config:
        extra = "forbid"


class LinkAction(BaseModel):
    """Link action configuration."""
    link: PageLink
    openInNewWindow: bool = Field(default=False, description="Open link in a new window.")

    class Config:
        extra = "forbid"


class ColorData(BaseModel):
    """Color/gradient data for backgrounds."""
    color: List[LooseJSON] = Field(description="Color array (e.g., HSL specification).")
    gradient: Optional[LooseJSON] = Field(default=None, description="Gradient definition.")

    class Config:
        extra = "forbid"


class Asset(BaseModel):
    """Asset metadata for background images."""
    alpha: Optional[float] = Field(default=None, description="Alpha transparency.")
    animated: Optional[bool] = Field(default=None, description="Whether the asset is animated.")
    bpp: Optional[int] = Field(default=None, description="Bits per pixel.")
    contentType: Optional[str] = Field(default=None, description="MIME type, e.g., image/jpeg.")
    etag: Optional[str] = Field(default=None, description="ETag for caching.")
    filesize: Optional[int] = Field(default=None, description="Filesize in bytes.")
    height: Optional[int] = Field(default=None, description="Image height.")
    image: Optional[LooseJSON] = Field(default=None, description="Optional embedded image data.")
    recommendedFormat: Optional[str] = Field(default=None, description="Recommended format.")
    url: Optional[str] = Field(default=None, description="Repository URL for the asset.")
    width: Optional[int] = Field(default=None, description="Image width.")
    id: Optional[str] = Field(default=None, description="Optional asset id.")
    isExternalLink: Optional[bool] = Field(default=None, description="True when using external/placeholder asset URLs.")

    class Config:
        extra = "forbid"


class AssetData(BaseModel):
    """Asset data wrapper with positioning."""
    asset: Asset
    repeat: List[bool] = Field(description="Background repeat flags [x,y].")
    position: List[str] = Field(description="Background position, e.g., ['50%','50%'].")
    size: str = Field(description="Background size, e.g., 'cover'.")
    scrollEffect: Optional[str] = Field(default=None, description="Scroll effect, e.g., 'parallax'.")
    opacity: Optional[float] = Field(default=None, description="Background opacity.")

    class Config:
        extra = "forbid"


class Background(BaseModel):
    """Background definition supporting color and asset data."""
    colorData: Optional[ColorData] = Field(default=None, description="Solid color or gradient data.")
    assetData: Optional[AssetData] = Field(default=None, description="Asset-backed background data.")

    class Config:
        extra = "forbid"


class BBox(BaseModel):
    """Bounding box coordinates."""
    bottom: Optional[int] = Field(default=None, description="Bottom coordinate.")
    left: Optional[int] = Field(default=None, description="Left coordinate.")
    right: Optional[int] = Field(default=None, description="Right coordinate.")
    top: Optional[int] = Field(default=None, description="Top coordinate.")

    class Config:
        extra = "forbid"


class ThemeStyleRef(BaseModel):
    """Reference to a theme style definition."""
    id: str
    name: str

    class Config:
        extra = "forbid"


class ThemeStyles(BaseModel):
    """Theme styles mapping for menus."""
    mainMenu: Optional[ThemeStyleRef] = None
    submenu: Optional[ThemeStyleRef] = None

    class Config:
        extra = "forbid"


class TextStyleMeta(BaseModel):
    """Text style metadata for generic info blocks."""
    bold: Optional[bool] = None
    color: Optional[List[LooseJSON]] = None
    fontFamily: Optional[str] = None
    fontSize: Optional[int] = None
    italic: Optional[bool] = None
    letterSpacing: Optional[float] = None
    lineHeight: Optional[float] = None
    prefixBold: Optional[bool] = None
    prefixCase: Optional[str] = None
    prefixItalic: Optional[bool] = None
    prefixUnderline: Optional[bool] = None
    underline: Optional[bool] = None
    valueCase: Optional[str] = None

    class Config:
        extra = "forbid"


class GenericInfo(BaseModel):
    """Generic contact/info block settings."""
    customPrefixText: Optional[str] = None
    horizontalAlignment: Optional[str] = None
    iconSize: Optional[int] = None
    iconTextSpacing: Optional[int] = None
    mobileFontSize: Optional[int] = None
    mobileHorizontalAlignment: Optional[str] = None
    mobileIconSize: Optional[int] = None
    showCustomTitleFirst: Optional[bool] = None
    showIcon: Optional[bool] = None
    showOnOneLine: Optional[bool] = None
    textStyle: Optional[TextStyleMeta] = None
    themeOverrideColor: Optional[LooseJSON] = None

    class Config:
        extra = "forbid"


class SpecificInfo(BaseModel):
    """Specific info block settings."""
    placeholderText: Optional[str] = None
    placeholder: Optional[Dict[str, Any]] = None
    showCountry: Optional[bool] = None
    showWebsiteTitleBeforeAddress: Optional[bool] = None

    class Config:
        extra = "forbid"


class ColorStop(BaseModel):
    """Color stop definitions."""
    fromColor: Optional[str] = None
    toColor: Optional[str] = None
    toThemeColor: Optional[str] = None

    class Config:
        extra = "forbid"


class FormElement(BaseModel):
    """Form field definition."""
    errorMessage: Optional[str] = None
    inputType: Optional[str] = None
    isRequired: Optional[bool] = None
    name: Optional[str] = None
    values: Optional[LooseJSON] = None
    hasCustomErrMsg: Optional[bool] = None
    autocomplete: Optional[str] = None

    class Config:
        extra = "forbid"


class Animation(BaseModel):
    """Animation settings for components."""
    delay: Optional[str] = None
    direction: Optional[str] = None
    effect: Optional[str] = None
    enabled: Optional[bool] = None
    speed: Optional[str] = None

    class Config:
        extra = "forbid"


class StyleForm(BaseModel):
    """Form style definition."""
    font: Optional[str] = None
    fontSize: Optional[int] = None
    fontColor: Optional[List[LooseJSON]] = None

    class Config:
        extra = "forbid"


class AddressLocation(BaseModel):
    """Geolocation for map/address components."""
    lat: float
    lng: float

    class Config:
        extra = "forbid"


class WidgetSetting(BaseModel):
    """Generic widget setting entry."""
    ref: str
    value: LooseJSON

    class Config:
        extra = "forbid"


class WidgetState(BaseModel):
    """Widget state for embeds (e.g., Youtube)."""
    id: Optional[str] = None
    type: Optional[str] = None
    settings: Optional[List[WidgetSetting]] = None

    class Config:
        extra = "forbid"


class GalleryImage(BaseModel):
    """Gallery image entry with asset metadata."""
    title: Optional[str] = None
    altText: Optional[str] = None
    caption: Optional[str] = None
    action: Optional[LooseJSON] = None
    asset: Optional[Asset] = None

    class Config:
        extra = "forbid"


class FullWidthOption(BaseModel):
    """Gallery full width option."""
    margin: Optional[int] = None
    maxWidth: Optional[int] = None
    originalLeft: Optional[int] = None
    originalWidth: Optional[int] = None

    class Config:
        extra = "forbid"


class Style(BaseModel):
    """Style wrapper used on sections/buttons/etc."""
    border: Optional[LooseJSON] = Field(default=None, description="Border definition.")
    background: Optional[Background] = Field(default=None, description="Background settings.")
    globalId: Optional[str] = Field(default=None, description="Global style id.")
    globalName: Optional[str] = Field(default=None, description="Global style name.")
    type: Optional[str] = Field(default=None, description="Style type identifier.")
    text: Optional[Dict[str, LooseJSON]] = Field(default=None, description="Text style payload.")

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
    items: Optional[List[Dict[str, LooseJSON]]] = Field(default=None, description="Child components (for containers).")

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
    paras: Optional[List[LooseJSON]] = Field(default=None, description="Paragraph metadata for rich text.")
    links: Optional[List[LooseJSON]] = Field(default=None, description="Link metadata for text elements.")
    globalStyleId: Optional[str] = Field(default=None, description="Global style reference id.")

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

    style: Optional[Style] = Field(default=None, description="CSS-like style properties.")
    styles: Optional[List[Union[Style, LooseJSON]]] = Field(default=None, description="Array of style definitions.")
    styleType: Optional[str] = Field(default=None, description="Style type identifier.")
    buttonThemeSelected: Optional[str] = Field(default=None, description="Selected button theme variant.")
    opacity: Optional[float] = Field(default=None, description="Opacity value (0-1).")
    rotation: Optional[float] = Field(default=None, description="Rotation angle in degrees.")
    scale: Optional[float] = Field(default=None, description="Scale factor.")
    border: Optional[LooseJSON] = Field(default=None, description="Border properties.")
    corners: Optional[LooseJSON] = Field(default=None, description="Corner radius properties.")
    padding: Optional[LooseJSON] = Field(default=None, description="Padding properties.")

    image: Optional[str] = Field(default=None, description="Image URL or identifier.")
    asset: Optional[Union[str, Asset]] = Field(default=None, description="Asset identifier or metadata.")
    assetData: Optional[AssetData] = Field(default=None, description="Asset metadata.")
    cropLeft: Optional[float] = Field(default=None, description="Image crop left offset.")
    cropTop: Optional[float] = Field(default=None, description="Image crop top offset.")
    scaleStrategy: Optional[str] = Field(default=None, description="Image scaling strategy.")
    lightBoxEnabled: Optional[bool] = Field(default=None, description="Enable lightbox for images.")

    link: Optional[str] = Field(default=None, description="Link URL.")
    linkAction: Optional[LinkAction] = Field(default=None, description="Link action configuration.")
    linkId: Optional[str] = Field(default=None, description="Link target component ID.")
    openInNewWindow: Optional[bool] = Field(default=None, description="Open link in new window.")
    openLink: Optional[Union[str, bool]] = Field(default=None, description="Link opening behavior.")
    dialogProps: Optional[Dict[str, LooseJSON]] = Field(default=None, description="Dialog properties for widgets (e.g., youtube).")
    state: Optional[WidgetState] = Field(default=None, description="Widget state for embedded components.")
    dialogProps: Optional[Dict[str, LooseJSON]] = Field(default=None, description="Dialog properties for widgets (e.g., youtube).")
    state: Optional[WidgetState] = Field(default=None, description="Widget state for embedded components.")
    dialogProps: Optional[Dict[str, LooseJSON]] = Field(default=None, description="Dialog properties for widgets (e.g., youtube).")
    state: Optional[WidgetState] = Field(default=None, description="Widget state for embedded components.")
    dialogProps: Optional[Dict[str, LooseJSON]] = Field(default=None, description="Dialog properties for widgets (e.g., youtube).")
    state: Optional[WidgetState] = Field(default=None, description="Widget state for embedded components.")
    dialogProps: Optional[Dict[str, LooseJSON]] = Field(default=None, description="Dialog properties for widgets (e.g., youtube).")
    state: Optional[WidgetState] = Field(default=None, description="Widget state for embedded components.")

    mobileDown: Optional[bool] = Field(default=None, description="Push content down on mobile.")
    mobileHide: Optional[bool] = Field(default=None, description="Hide component on mobile.")
    mobileSettings: Optional[MobileSettings] = Field(default=None, description="Mobile-specific settings.")
    mobileFontSize: Optional[int] = Field(default=None, description="Font size for mobile.")
    mobileSize: Optional[Union[str, int]] = Field(default=None, description="Size configuration for mobile.")
    mobileHorizontalAlignment: Optional[str] = Field(default=None, description="Horizontal alignment on mobile.")

    animated: Optional[bool] = Field(default=None, description="Enable animation.")
    animation: Optional[Animation] = Field(default=None, description="Animation configuration.")
    scrollEffect: Optional[str] = Field(default=None, description="Scroll-triggered effect.")
    hover: Optional[LooseJSON] = Field(default=None, description="Hover state properties.")
    onHover: Optional[LooseJSON] = Field(default=None, description="On hover behavior.")
    press: Optional[LooseJSON] = Field(default=None, description="Press/click state properties.")

    rawSvg: Optional[str] = Field(default=None, description="Raw SVG markup.")
    svgJson: Optional[LooseJSON] = Field(default=None, description="SVG structure as JSON.")
    viewBox: Optional[str] = Field(default=None, description="SVG viewBox attribute.")

    hidden: Optional[bool] = Field(default=None, description="Hide component.")
    show: Optional[bool] = Field(default=None, description="Show component.")
    spacing: Optional[float] = Field(default=None, description="Spacing value.")
    size: Optional[Union[str, int]] = Field(default=None, description="Size configuration.")
    position: Optional[str] = Field(default=None, description="Position type (absolute, relative, etc).")
    repeat: Optional[bool] = Field(default=None, description="Repeat pattern.")
    gradient: Optional[Dict[str, LooseJSON]] = Field(default=None, description="Gradient configuration.")
    seo: Optional[Dict[str, LooseJSON]] = Field(default=None, description="SEO metadata.")
    images: Optional[List[GalleryImage]] = Field(default=None, description="Gallery images with assets.")
    crop: Optional[bool] = Field(default=None, description="Whether to crop gallery images.")
    captionsEnabled: Optional[bool] = Field(default=None, description="Enable captions for gallery.")
    captionsAlignment: Optional[str] = Field(default=None, description="Caption alignment for gallery.")
    columns: Optional[int] = Field(default=None, description="Gallery columns.")
    spacingPx: Optional[int] = Field(default=None, description="Gallery spacing in pixels.")
    onClickAction: Optional[str] = Field(default=None, description="Gallery click action.")
    imageStyle: Optional[LooseJSON] = Field(default=None, description="Gallery image style overrides.")
    captionBoxStyle: Optional[LooseJSON] = Field(default=None, description="Gallery caption box style.")
    previousCaptionStyle: Optional[str] = Field(default=None, description="Previous caption style.")
    captionStyle: Optional[str] = Field(default=None, description="Caption style.")
    imageRatio: Optional[str] = Field(default=None, description="Gallery image ratio.")
    captionTitleTextStyle: Optional[LooseJSON] = Field(default=None, description="Caption title text style.")
    captionDescriptionTextStyle: Optional[LooseJSON] = Field(default=None, description="Caption description text style.")
    captionMinHeight: Optional[int] = Field(default=None, description="Minimum caption height.")
    fullWidthOption: Optional[FullWidthOption] = Field(default=None, description="Gallery full width option.")
    compactView: Optional[bool] = Field(default=None, description="Enable compact gallery view.")
    type: Optional[str] = Field(default=None, description="Gallery type identifier.")
    captionsPlacement: Optional[str] = Field(default=None, description="Placement of captions in gallery/slider.")
    delay: Optional[int] = Field(default=None, description="Delay for slideshows.")
    autoNext: Optional[bool] = Field(default=None, description="Auto-advance slides.")
    indicator: Optional[str] = Field(default=None, description="Indicator style for slideshows.")
    navigator: Optional[str] = Field(default=None, description="Navigator visibility for slideshows.")
    transition: Optional[str] = Field(default=None, description="Transition type for slideshows.")
    originalSize: Optional[bool] = Field(default=None, description="Show media in original size.")
    columnCount: Optional[int] = Field(default=None, description="Column count for sliders/grids.")
    showBackground: Optional[bool] = Field(default=None, description="Show background behind media.")
    captionsPlacement: Optional[str] = Field(default=None, description="Placement of captions in gallery/slider.")
    delay: Optional[int] = Field(default=None, description="Delay for slideshows.")
    autoNext: Optional[bool] = Field(default=None, description="Auto-advance slides.")
    indicator: Optional[str] = Field(default=None, description="Indicator style for slideshows.")
    navigator: Optional[str] = Field(default=None, description="Navigator visibility for slideshows.")
    transition: Optional[str] = Field(default=None, description="Transition type for slideshows.")
    originalSize: Optional[bool] = Field(default=None, description="Show media in original size.")
    columnCount: Optional[int] = Field(default=None, description="Column count for sliders/grids.")
    showBackground: Optional[bool] = Field(default=None, description="Show background behind media.")
    captionsPlacement: Optional[str] = Field(default=None, description="Placement of captions in gallery/slider.")
    delay: Optional[int] = Field(default=None, description="Delay for slideshows.")
    autoNext: Optional[bool] = Field(default=None, description="Auto-advance slides.")
    indicator: Optional[str] = Field(default=None, description="Indicator style for slideshows.")
    navigator: Optional[str] = Field(default=None, description="Navigator visibility for slideshows.")
    transition: Optional[str] = Field(default=None, description="Transition type for slideshows.")
    originalSize: Optional[bool] = Field(default=None, description="Show media in original size.")
    columnCount: Optional[int] = Field(default=None, description="Column count for sliders/grids.")
    showBackground: Optional[bool] = Field(default=None, description="Show background behind media.")
    captionsPlacement: Optional[str] = Field(default=None, description="Placement of captions in gallery/slider.")
    delay: Optional[int] = Field(default=None, description="Delay for slideshows.")
    autoNext: Optional[bool] = Field(default=None, description="Auto-advance slides.")
    indicator: Optional[str] = Field(default=None, description="Indicator style for slideshows.")
    navigator: Optional[str] = Field(default=None, description="Navigator visibility for slideshows.")
    transition: Optional[str] = Field(default=None, description="Transition type for slideshows.")
    originalSize: Optional[bool] = Field(default=None, description="Show media in original size.")
    columnCount: Optional[int] = Field(default=None, description="Column count for sliders/grids.")
    showBackground: Optional[bool] = Field(default=None, description="Show background behind media.")

    bbox: Optional[BBox] = Field(default=None, description="Bounding box coordinates (bottom, left, right, top).")
    selectedTheme: Optional[str] = Field(default=None, description="Selected theme name (e.g., 'Main', 'White', 'Dark').")
    selectedGradientTheme: Optional[str] = Field(default=None, description="Selected gradient theme name.")
    stretch: Optional[bool] = Field(default=None, description="Stretch component to fill width (typically for SECTION).")
    pin: Optional[int] = Field(default=None, description="Pin component position (0 for unpinned).")
    colorType: Optional[str] = Field(default=None, description="Color type for theme adaptation (LIGHT, DARK).")
    addressLocation: Optional[AddressLocation] = Field(default=None, description="Geolocation for map/address components.")
    addressText: Optional[str] = Field(default=None, description="Address display text.")
    addressUrl: Optional[str] = Field(default=None, description="Address link URL.")
    captchaLang: Optional[str] = Field(default=None, description="Captcha language code.")
    colors: Optional[List[ColorStop]] = Field(default=None, description="Color stop definitions.")
    defaultFillColor: Optional[str] = Field(default=None, description="Default fill color.")
    formElements: Optional[Dict[str, FormElement]] = Field(default=None, description="Form field definitions keyed by field name.")
    formElementsOrder: Optional[List[str]] = Field(default=None, description="Order of form fields.")
    fuButtonThemeSelected: Optional[str] = Field(default=None, description="File-upload button theme selection.")
    generic: Optional[GenericInfo] = Field(default=None, description="Generic info block settings.")
    horizontalAlign: Optional[str] = Field(default=None, description="Horizontal alignment for menu/logo components.")
    isCaptchaEnabled: Optional[bool] = Field(default=None, description="Enable captcha for forms.")
    isDecorative: Optional[bool] = Field(default=None, description="Mark element as decorative.")
    isMarketingConsentEnabled: Optional[bool] = Field(default=None, description="Require marketing consent.")
    isStickyToHeader: Optional[bool] = Field(default=None, description="Stick component to header.")
    layoutType: Optional[str] = Field(default=None, description="Layout type identifier.")
    locale: Optional[str] = Field(default=None, description="Locale code.")
    logoHorizontalAlignment: Optional[str] = Field(default=None, description="Logo alignment in menus.")
    logoTitleScale: Optional[float] = Field(default=None, description="Logo title scale factor.")
    marketingConsentCheckBoxText: Optional[str] = Field(default=None, description="Marketing consent checkbox text.")
    moreButtonEnabled: Optional[bool] = Field(default=None, description="Enable more button in menu.")
    moreText: Optional[str] = Field(default=None, description="More button text.")
    readPrivacyPolicyText: Optional[str] = Field(default=None, description="Privacy policy link text.")
    recipientEmail: Optional[str] = Field(default=None, description="Form recipient email.")
    source: Optional[str] = Field(default=None, description="Source identifier.")
    specific: Optional[SpecificInfo] = Field(default=None, description="Specific info block settings.")
    startLevel: Optional[int] = Field(default=None, description="Menu start level.")
    styleButton: Optional[Style] = Field(default=None, description="Button style reference.")
    styleForm: Optional[StyleForm] = Field(default=None, description="Form style definition.")
    subStyle: Optional[Style] = Field(default=None, description="Submenu style reference.")
    subject: Optional[str] = Field(default=None, description="Form subject line.")
    submitBtn: Optional[str] = Field(default=None, description="Submit button label.")
    successMessage: Optional[str] = Field(default=None, description="Success message after form submit.")
    themeColorType: Optional[str] = Field(default=None, description="Theme color type.")
    themeStyles: Optional[ThemeStyles] = Field(default=None, description="Theme style references for menus.")
    useOriginalColors: Optional[bool] = Field(default=None, description="Use original colors for icons/assets.")
    verticalAlign: Optional[str] = Field(default=None, description="Vertical alignment for menu/logo components.")
    zoom: Optional[int] = Field(default=None, description="Map zoom level.")
    pageURL: Optional[str] = Field(default=None, description="Social/embed page URL.")
    tabs: Optional[List[str]] = Field(default=None, description="Tabs for social embeds.")
    hideCover: Optional[bool] = Field(default=None, description="Hide cover image.")
    showFacepile: Optional[bool] = Field(default=None, description="Show facepile in embeds.")
    showCTA: Optional[bool] = Field(default=None, description="Show call-to-action in embeds.")
    smallHeader: Optional[bool] = Field(default=None, description="Use small header in embeds.")
    adaptContainerWidth: Optional[bool] = Field(default=None, description="Adapt container width for embeds.")
    timelineLink: Optional[str] = Field(default=None, description="Twitter timeline link.")
    listLink: Optional[str] = Field(default=None, description="Twitter list link.")
    tweetHTML: Optional[str] = Field(default=None, description="Embedded tweet HTML.")
    theme: Optional[str] = Field(default=None, description="Embed theme.")
    doNotTrack: Optional[bool] = Field(default=None, description="Disable tracking for embeds.")
    direction: Optional[str] = Field(default=None, description="Text direction for embeds.")
    cells: Optional[List[LooseJSON]] = Field(default=None, description="Table/gallery cells data.")
    commonCellsData: Optional[Dict[str, LooseJSON]] = Field(default=None, description="Shared cell data for grids/tables.")
    cells: Optional[List[LooseJSON]] = Field(default=None, description="Table/gallery cells data.")
    commonCellsData: Optional[Dict[str, LooseJSON]] = Field(default=None, description="Shared cell data for grids/tables.")
    timelineLink: Optional[str] = Field(default=None, description="Twitter timeline link.")
    listLink: Optional[str] = Field(default=None, description="Twitter list link.")
    tweetHTML: Optional[str] = Field(default=None, description="Embedded tweet HTML.")
    theme: Optional[str] = Field(default=None, description="Embed theme.")
    doNotTrack: Optional[bool] = Field(default=None, description="Disable tracking for embeds.")
    direction: Optional[str] = Field(default=None, description="Text direction for embeds.")
    pageURL: Optional[str] = Field(default=None, description="Social/embed page URL.")
    tabs: Optional[List[str]] = Field(default=None, description="Tabs for social embeds.")
    hideCover: Optional[bool] = Field(default=None, description="Hide cover image.")
    showFacepile: Optional[bool] = Field(default=None, description="Show facepile in embeds.")
    showCTA: Optional[bool] = Field(default=None, description="Show call-to-action in embeds.")
    smallHeader: Optional[bool] = Field(default=None, description="Use small header in embeds.")
    adaptContainerWidth: Optional[bool] = Field(default=None, description="Adapt container width for embeds.")

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
    items: Optional[List[Dict[str, LooseJSON]]] = Field(default=None, description="Child components (for containers).")

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
    paras: Optional[List[LooseJSON]] = Field(default=None, description="Paragraph metadata for rich text.")
    links: Optional[List[LooseJSON]] = Field(default=None, description="Link metadata for text elements.")
    globalStyleId: Optional[str] = Field(default=None, description="Global style reference id.")

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

    style: Optional[Style] = Field(default=None, description="CSS-like style properties.")
    styles: Optional[List[Union[Style, LooseJSON]]] = Field(default=None, description="Array of style definitions.")
    styleType: Optional[str] = Field(default=None, description="Style type identifier.")
    buttonThemeSelected: Optional[str] = Field(default=None, description="Selected button theme variant.")
    opacity: Optional[float] = Field(default=None, description="Opacity value (0-1).")
    rotation: Optional[float] = Field(default=None, description="Rotation angle in degrees.")
    scale: Optional[float] = Field(default=None, description="Scale factor.")
    border: Optional[LooseJSON] = Field(default=None, description="Border properties.")
    corners: Optional[LooseJSON] = Field(default=None, description="Corner radius properties.")
    padding: Optional[LooseJSON] = Field(default=None, description="Padding properties.")

    image: Optional[str] = Field(default=None, description="Image URL or identifier.")
    asset: Optional[Union[str, Asset]] = Field(default=None, description="Asset identifier or metadata.")
    assetData: Optional[AssetData] = Field(default=None, description="Asset metadata.")
    cropLeft: Optional[float] = Field(default=None, description="Image crop left offset.")
    cropTop: Optional[float] = Field(default=None, description="Image crop top offset.")
    scaleStrategy: Optional[str] = Field(default=None, description="Image scaling strategy.")
    lightBoxEnabled: Optional[bool] = Field(default=None, description="Enable lightbox for images.")

    link: Optional[str] = Field(default=None, description="Link URL.")
    linkAction: Optional[LinkAction] = Field(default=None, description="Link action configuration.")
    linkId: Optional[str] = Field(default=None, description="Link target component ID.")
    openInNewWindow: Optional[bool] = Field(default=None, description="Open link in new window.")
    openLink: Optional[Union[str, bool]] = Field(default=None, description="Link opening behavior.")
    dialogProps: Optional[Dict[str, LooseJSON]] = Field(default=None, description="Dialog properties for widgets (e.g., youtube).")
    state: Optional[WidgetState] = Field(default=None, description="Widget state for embedded components.")

    mobileDown: Optional[bool] = Field(default=None, description="Push content down on mobile.")
    mobileHide: Optional[bool] = Field(default=None, description="Hide component on mobile.")
    mobileSettings: Optional[MobileSettings] = Field(default=None, description="Mobile-specific settings.")
    mobileFontSize: Optional[int] = Field(default=None, description="Font size for mobile.")
    mobileSize: Optional[Union[str, int]] = Field(default=None, description="Size configuration for mobile.")
    mobileHorizontalAlignment: Optional[str] = Field(default=None, description="Horizontal alignment on mobile.")

    animated: Optional[bool] = Field(default=None, description="Enable animation.")
    animation: Optional[Animation] = Field(default=None, description="Animation configuration.")
    scrollEffect: Optional[str] = Field(default=None, description="Scroll-triggered effect.")
    hover: Optional[LooseJSON] = Field(default=None, description="Hover state properties.")
    onHover: Optional[LooseJSON] = Field(default=None, description="On hover behavior.")
    press: Optional[LooseJSON] = Field(default=None, description="Press/click state properties.")

    rawSvg: Optional[str] = Field(default=None, description="Raw SVG markup.")
    svgJson: Optional[LooseJSON] = Field(default=None, description="SVG structure as JSON.")
    viewBox: Optional[str] = Field(default=None, description="SVG viewBox attribute.")

    hidden: Optional[bool] = Field(default=None, description="Hide component.")
    show: Optional[bool] = Field(default=None, description="Show component.")
    spacing: Optional[float] = Field(default=None, description="Spacing value.")
    size: Optional[Union[str, int]] = Field(default=None, description="Size configuration.")
    position: Optional[str] = Field(default=None, description="Position type (absolute, relative, etc).")
    repeat: Optional[bool] = Field(default=None, description="Repeat pattern.")
    gradient: Optional[LooseJSON] = Field(default=None, description="Gradient configuration.")
    seo: Optional[LooseJSON] = Field(default=None, description="SEO metadata.")
    images: Optional[List[GalleryImage]] = Field(default=None, description="Gallery images with assets.")
    crop: Optional[bool] = Field(default=None, description="Whether to crop gallery images.")
    captionsEnabled: Optional[bool] = Field(default=None, description="Enable captions for gallery.")
    captionsAlignment: Optional[str] = Field(default=None, description="Caption alignment for gallery.")
    columns: Optional[int] = Field(default=None, description="Gallery columns.")
    spacingPx: Optional[int] = Field(default=None, description="Gallery spacing in pixels.")
    onClickAction: Optional[str] = Field(default=None, description="Gallery click action.")
    imageStyle: Optional[LooseJSON] = Field(default=None, description="Gallery image style overrides.")
    captionBoxStyle: Optional[LooseJSON] = Field(default=None, description="Gallery caption box style.")
    previousCaptionStyle: Optional[str] = Field(default=None, description="Previous caption style.")
    captionStyle: Optional[str] = Field(default=None, description="Caption style.")
    imageRatio: Optional[str] = Field(default=None, description="Gallery image ratio.")
    captionTitleTextStyle: Optional[LooseJSON] = Field(default=None, description="Caption title text style.")
    captionDescriptionTextStyle: Optional[LooseJSON] = Field(default=None, description="Caption description text style.")
    captionMinHeight: Optional[int] = Field(default=None, description="Minimum caption height.")
    fullWidthOption: Optional[FullWidthOption] = Field(default=None, description="Gallery full width option.")
    compactView: Optional[bool] = Field(default=None, description="Enable compact gallery view.")
    type: Optional[str] = Field(default=None, description="Gallery type identifier.")

    bbox: Optional[BBox] = Field(default=None, description="Bounding box coordinates (bottom, left, right, top).")
    selectedTheme: Optional[str] = Field(default=None, description="Selected theme name (e.g., 'Main', 'White', 'Dark').")
    selectedGradientTheme: Optional[str] = Field(default=None, description="Selected gradient theme name.")
    stretch: Optional[bool] = Field(default=None, description="Stretch component to fill width (typically for SECTION).")
    pin: Optional[int] = Field(default=None, description="Pin component position (0 for unpinned).")
    colorType: Optional[str] = Field(default=None, description="Color type for theme adaptation (LIGHT, DARK).")
    addressLocation: Optional[AddressLocation] = Field(default=None, description="Geolocation for map/address components.")
    addressText: Optional[str] = Field(default=None, description="Address display text.")
    addressUrl: Optional[str] = Field(default=None, description="Address link URL.")
    captchaLang: Optional[str] = Field(default=None, description="Captcha language code.")
    colors: Optional[List[ColorStop]] = Field(default=None, description="Color stop definitions.")
    defaultFillColor: Optional[str] = Field(default=None, description="Default fill color.")
    formElements: Optional[Dict[str, FormElement]] = Field(default=None, description="Form field definitions keyed by field name.")
    formElementsOrder: Optional[List[str]] = Field(default=None, description="Order of form fields.")
    fuButtonThemeSelected: Optional[str] = Field(default=None, description="File-upload button theme selection.")
    generic: Optional[GenericInfo] = Field(default=None, description="Generic info block settings.")
    horizontalAlign: Optional[str] = Field(default=None, description="Horizontal alignment for menu/logo components.")
    isCaptchaEnabled: Optional[bool] = Field(default=None, description="Enable captcha for forms.")
    isDecorative: Optional[bool] = Field(default=None, description="Mark element as decorative.")
    isMarketingConsentEnabled: Optional[bool] = Field(default=None, description="Require marketing consent.")
    isStickyToHeader: Optional[bool] = Field(default=None, description="Stick component to header.")
    layoutType: Optional[str] = Field(default=None, description="Layout type identifier.")
    locale: Optional[str] = Field(default=None, description="Locale code.")
    logoHorizontalAlignment: Optional[str] = Field(default=None, description="Logo alignment in menus.")
    logoTitleScale: Optional[float] = Field(default=None, description="Logo title scale factor.")
    marketingConsentCheckBoxText: Optional[str] = Field(default=None, description="Marketing consent checkbox text.")
    moreButtonEnabled: Optional[bool] = Field(default=None, description="Enable more button in menu.")
    moreText: Optional[str] = Field(default=None, description="More button text.")
    readPrivacyPolicyText: Optional[str] = Field(default=None, description="Privacy policy link text.")
    recipientEmail: Optional[str] = Field(default=None, description="Form recipient email.")
    source: Optional[str] = Field(default=None, description="Source identifier.")
    specific: Optional[SpecificInfo] = Field(default=None, description="Specific info block settings.")
    startLevel: Optional[int] = Field(default=None, description="Menu start level.")
    styleButton: Optional[Style] = Field(default=None, description="Button style reference.")
    styleForm: Optional[StyleForm] = Field(default=None, description="Form style definition.")
    subStyle: Optional[Style] = Field(default=None, description="Submenu style reference.")
    subject: Optional[str] = Field(default=None, description="Form subject line.")
    submitBtn: Optional[str] = Field(default=None, description="Submit button label.")
    successMessage: Optional[str] = Field(default=None, description="Success message after form submit.")
    themeColorType: Optional[str] = Field(default=None, description="Theme color type.")
    themeStyles: Optional[ThemeStyles] = Field(default=None, description="Theme style references for menus.")
    useOriginalColors: Optional[bool] = Field(default=None, description="Use original colors for icons/assets.")
    verticalAlign: Optional[str] = Field(default=None, description="Vertical alignment for menu/logo components.")
    zoom: Optional[int] = Field(default=None, description="Map zoom level.")

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


# Ensure gallery/slider extra fields are registered on CreateInput (py right now misses them in __annotations__).
_gallery_extra_annotations: Dict[str, Any] = {
    "captionsPlacement": Optional[str],
    "delay": Optional[int],
    "autoNext": Optional[bool],
    "indicator": Optional[str],
    "navigator": Optional[str],
    "transition": Optional[str],
    "originalSize": Optional[bool],
    "columnCount": Optional[int],
    "showBackground": Optional[bool],
}
CreateInput.__annotations__.update(_gallery_extra_annotations)
for _field in _gallery_extra_annotations:
    setattr(CreateInput, _field, None)
CreateInput.model_rebuild(force=True)

# Rebuild CreateInput with gallery/slider extras to ensure model_fields include them.
from pydantic import create_model
CreateInput = create_model(
    "CreateInput",
    captionsPlacement=(Optional[str], None),
    delay=(Optional[int], None),
    autoNext=(Optional[bool], None),
    indicator=(Optional[str], None),
    navigator=(Optional[str], None),
    transition=(Optional[str], None),
    originalSize=(Optional[bool], None),
    columnCount=(Optional[int], None),
    showBackground=(Optional[bool], None),
    pageURL=(Optional[str], None),
    tabs=(Optional[List[str]], None),
    hideCover=(Optional[bool], None),
    showFacepile=(Optional[bool], None),
    showCTA=(Optional[bool], None),
    smallHeader=(Optional[bool], None),
    adaptContainerWidth=(Optional[bool], None),
    timelineLink=(Optional[str], None),
    listLink=(Optional[str], None),
    tweetHTML=(Optional[str], None),
    theme=(Optional[str], None),
    doNotTrack=(Optional[bool], None),
    direction=(Optional[str], None),
    cells=(Optional[List[Any]], None),
    commonCellsData=(Optional[Dict[str, Any]], None),
    __base__=CreateInput,
)
