"""Tool descriptions for the React agent.

This module contains detailed descriptions for each tool, providing guidance
to the LLM on how to use them correctly.
"""

CREATE_TOOL_DESCRIPTION = """Create WSB components using the full schema from components-map.json, with smart defaults and flat relIn/relTo layout.

CORE KINDS & DEFAULTS
- SECTION: stretch=true, pin=0, selectedTheme="White", mobileSettings.size="cover"
- CONTAINER: wrap=false by default
- TEXT: fontSize=16, lineHeight=1.5
- BUTTON: bold=true, corners.radius=5, fontSize=16
- IMAGE/SVG/LOGO/MENU/FORM/MAP/etc. supported; pass required style/data as below.

LAYOUT (FLAT STRUCTURE)
- parent_id sets relIn.id automatically; children stay in the root list.
- relTo stacks siblings: e.g., relTo={"id": "<prev-section>", "below": 0}. after_id/before_id auto-add relTo with below=0.
- Position with left/top/width/height; verticalAlignment/horizontalAlignment optional; bbox can hold bounding box ints.
- For precise placement, set relIn offsets (e.g., {"id": "<section>", "left": 120, "top": 80}); use relTo only for stacking relative to a sibling.
- Sections: always give relTo to stack them; inner blocks: give relIn with numeric offsets or alignment plus width/height.

CONTENT/STYLES
- content/text/title/name plus paras/links/globalStyleId for rich text.
- style/background: background.colorData.color=[\"HSL\", h,s,l,a], background.assetData.asset={url,width,height,etag,...}, repeat/position/size/scrollEffect/opacity supported.
- style/global refs: globalId, globalName, type, text={size: int}.
- styles accepts mixed Style or raw JSON fragments (as seen in components-map).
- Theming: selectedTheme/selectedGradientTheme, themeColorType, themeOverrideColor/themeHighlightColor/themeShadow*.
- Border/corners/padding accept structured data; gradient/seo/hover/onHover/press/svgJson allow JSON blobs.

MOBILE & VISIBILITY
- mobileSettings {align,font,size}, mobileHide, mobileDown, mobileHorizontalAlignment, mobileFontSize, mobileSize.
- size/mobileSize accept str or int.

LINKS & ACTIONS
- linkAction {link:{type,value}, openInNewWindow}, link/openLink (string or bool), linkId, buttonThemeSelected, fuButtonThemeSelected.

FORMS & CONTACT
- formElements {fieldName: {inputType,isRequired,errorMessage,name,values}}, formElementsOrder (list), recipientEmail, subject, submitBtn, successMessage.
- isCaptchaEnabled, captchaLang, isMarketingConsentEnabled, marketingConsentCheckBoxText, readPrivacyPolicyText.
- styleForm {font,fontSize,fontColor}, styleButton/styleForm/subStyle (Style), themeStyles {mainMenu, submenu}, themeColorType.

MENUS/HEADER
- layoutType (e.g., HORIZONTAL_DROPDOWN), startLevel, moreButtonEnabled/moreText, isStickyToHeader, logoHorizontalAlignment, logoTitleScale, horizontalAlign/verticalAlign.
- generic info blocks: generic {customPrefixText, iconSize, iconTextSpacing, textStyle{bold,color,fontFamily,fontSize,letterSpacing,lineHeight,prefix*}, themeOverrideColor, mobile* flags}.
- specific info blocks: specific {placeholderText, placeholder{addressName/addressLine1/…}, showCountry, showWebsiteTitleBeforeAddress}.

MAP/ADDRESS
- addressLocation {lat,lng}, addressText, addressUrl, zoom, useOriginalColors, colors [{fromColor,toColor,toThemeColor}], defaultFillColor.

FLEXIBLE FIELDS (LOOSE JSON OK)
- styles can mix Style objects with raw fragments (e.g., [1,1,{\"globalId\":\"...\",\"type\":\"web.data.styles.StyleText\"}]).
- gradient/seo/svgJson/hover/onHover/press accept structured JSON blobs as needed by the renderer.

PLACEHOLDER IMAGES
- For IMAGE/GALLERY assets, use placeholder URLs matching component size: "https://placehold.co/<width>x<height>" and set asset.isExternalLink=true.
- Asset schema supports isExternalLink, width, height, url, contentType, etc.

EXAMPLES
- Section hero: kind="SECTION", title="Hero", height=700, selectedTheme="Main", relTo={"id": "<prev>", "below":0}, style.background.assetData.asset.url="repository:/image.jpg"
- Menu: kind="MENU", layoutType="HORIZONTAL_DROPDOWN", themeStyles.mainMenu={id,name}, startLevel=1, moreButtonEnabled=true
- Form: kind="FORM", formElements={name:{inputType:"text",isRequired:true}}, recipientEmail="hi@example.com", isCaptchaEnabled=true
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
