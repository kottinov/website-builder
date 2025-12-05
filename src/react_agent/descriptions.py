"""Tool descriptions for the React agent.

This module contains detailed descriptions for each tool, providing guidance
to the LLM on how to use them correctly.
"""

CREATE_TOOL_DESCRIPTION = """Create WSB components using the strictly validated schema (extra=forbid) and flat relIn/relTo layout.

CORE KINDS & DEFAULTS
- SECTION: stretch=true, pin=0, selectedTheme="White", selectedGradientTheme=null, selectedBorderTheme=null, mobileSettings.size="cover", wrap=false (modernLayout accepted when provided)
- CONTAINER: wrap=false by default
- TEXT: fontSize=16, lineHeight=1.5, text="", styles=[], paras=[], links=[], mobileDown=false, mobileHide=false, verticalAlignment="top", mobileSettings={"align": null, "font": 0}, globalStyleId="GLOBAL_TEXT_STYLE_DEFAULT", themeShadowBlurRadius=3, themeShadowOffsetX=3, themeShadowOffsetY=3, themeShadowColor=null
- BUTTON: bold=true, corners.radius=5, fontSize=16, mobileDown=false, mobileHide=false, mobileSettings={"align": "justify"}, buttonThemeSelected="primary", style={border:null, background:null, globalId:"BUTTON_STYLE_DEFAULT", globalName:"[button.default]", type:"web.data.styles.StyleButton", text:{size:null}}
- CODE: use code + location + name along with layout/rel fields
- IMAGE/SVG/LOGO/MENU/FORM/MAP/etc. supported; pass required style/data as below.

SCHEMA RULES
- Only the documented CreateInput fields are accepted (extra=forbid); use kind only (no legacy type field).
- Required subobjects must be complete: TEXT needs relIn, globalStyleId, mobileSettings, verticalAlignment, theme shadow values; BUTTON needs style + buttonThemeSelected; SECTION allows optional modernLayout; CONTACTFORM accepts fileUploadButtonStyle; BACKGROUND/STRIP fields include backgroundColor/size/repeat/position/attachment/clip/border/padding/selectedBorderTheme/asset/scrollEffect; CODE requires code/location/name.

CRITICAL REQUIRED FIELDS FOR ALL COMPONENTS:
- inTemplate: false (default for non-template components)
- wrap: false (default for most components)
- mobileDown: false (unless specifically required)
- mobileHide: false (unless specifically required)
- onHover: null (unless hover effects are needed)
- relPage: null (always null in flat structure)
- relPara: null (always null unless text in paragraph flow)

LAYOUT (ABSOLUTE + RELATIVE, FLAT STRUCTURE)
All components live in a flat items[] array. Position is controlled by absolute coordinates (left/top/width/height) plus relIn/relTo for parent and sibling relationships.

CRITICAL RULES FOR relIn AND relTo:

1. SECTIONS:
   - relIn: MUST be null (sections have no parent)
   - relTo: CRITICAL - Each section must chain to the previous section/header
     * First section: relTo = {"id": "22FC8C5B-CD71-42B7-9DF2-486F577581A9", "below": 0}
     * Subsequent sections: relTo = {"id": "<previous-section-id>", "below": 0}
   - relPage: null, relPara: null
   - top: MUST be calculated precisely: previous_section.top + previous_section.height
   - IMPORTANT: Use list() to get the REAL previous section ID, never use placeholders
   - You can omit relTo for "SECTION" - it will be auto-populated, but providing it is safer

2. CHILDREN (TEXT, BUTTON, IMAGE, etc. inside a section):
   - relIn: REQUIRED - positions child relative to parent section
   - relTo: null for the FIRST child; subsequent children CAN chain to siblings
   - relPage: null, relPara: null

3. relIn MATH (for children inside a parent):
   - relIn.id = parent component ID
   - relIn.left = child.left - parent.left
   - relIn.top = child.top - parent.top
   - relIn.bottom = -(parent.height - (relIn.top + child.height))
   - relIn.right = -(parent.width - (relIn.left + child.width)) OR null

   EXAMPLE: Parent section at (left=0, top=90, width=1300, height=760)
            Child text at (left=185, top=250, width=680, height=260)
            relIn = {
              "id": "<section-id>",
              "left": 185,        // 185 - 0 = 185
              "top": 160,         // 250 - 90 = 160
              "right": null,
              "bottom": -340      // -(760 - (160 + 260)) = -340
            }

4. relTo for SIBLING CHAINING (optional, for children):
   - First child in section: relTo = null
   - To stack below a sibling: relTo = {"id": "<sibling-id>", "below": <gap_px>}
   - below MUST be a number (0, 10, 30, etc.), never null

   EXAMPLE: Button below a text block with 30px gap:
            relTo = {"id": "<text-component-id>", "below": 30}

5. COMPLETE COMPONENT EXAMPLES:

   SECTION (first or only section - needs existing anchor):
   {
     "kind": "SECTION",
     "inTemplate": false,
     "orderIndex": 0,
     "stretch": true,
     "wrap": false,
     "left": 0, "top": 90, "width": 1300, "height": 760,
     "relIn": null,
     "relTo": {"id": "<existing-header-or-section-id>", "below": 0},
     "relPage": null, "relPara": null,
     "style": {
       "border": null,
       "background": {
         "colorData": {
           "color": ["HSL", 0.5644999999999936, 0, 0.16820000000000002, 1],
           "gradient": null
         }
       }
     },
     "mobileSettings": {"size": "cover"},
     "pin": 0,
     "title": "Section1",
     "selectedTheme": "Black",
     "selectedGradientTheme": null
   }

   TEXT (first child - no sibling stacking):
   {
     "kind": "TEXT",
     "inTemplate": false,
     "orderIndex": 0,
     "wrap": false,
     "mobileDown": false,
     "onHover": null,
     "left": 185, "top": 250, "width": 680, "height": 260,
     "parent_id": "<section-id>",
     "relIn": {"id": "<section-id>", "left": 185, "top": 160, "right": null, "bottom": -340},
     "relTo": null,
     "relPage": null, "relPara": null,
     "verticalAlignment": "bottom",
     "mobileHide": false,
     "mobileSettings": {"align": null, "font": 0},
     "content": "<p>Your text here</p>",
     "text": "",
     "styles": [],
     "paras": [],
     "links": [],
     "themeOverrideColor": null,
     "themeHighlightColor": null,
     "themeShadowBlurRadius": 3,
     "themeShadowColor": null,
     "themeShadowOffsetX": 3,
     "themeShadowOffsetY": 3,
     "globalStyleId": "EAEA20A6-C03E-4C8C-ADA5-43EBBEF4CD23"
   }

   BUTTON (stacked below text with 30px gap):
   {
     "kind": "BUTTON",
     "inTemplate": false,
     "orderIndex": 1,
     "wrap": false,
     "mobileDown": false,
     "onHover": null,
     "left": 375, "top": 580, "width": 300, "height": 60,
     "parent_id": "<section-id>",
     "relIn": {"id": "<section-id>", "left": 375, "top": 490, "right": null, "bottom": -210},
     "relTo": {"id": "<text-id>", "below": 30},
     "relPage": null, "relPara": null,
     "text": "Click me",
     "mobileHide": false,
     "mobileSettings": {"align": "justify"},
     "style": {
       "globalId": "0E6D94E7-D717-487F-B936-712CA4C430AA",
       "globalName": "[button.1]",
       "type": "web.data.styles.StyleButton",
       "text": {"size": null}
     },
     "buttonThemeSelected": "primary"
   }

WORKFLOW:
1. ALWAYS call list() first to get existing component IDs
2. For sections: find an existing section/header ID to chain relTo
   - When adding multiple sections, calculate each section's top: prev.top + prev.height
   - Always chain sections: section2.relTo.id = section1.id, section3.relTo.id = section2.id, etc.
3. For children: use parent section ID for relIn.id
4. Calculate relIn offsets using the math above
5. Set relTo=null for first child, or chain to sibling with {"below": N}

MULTIPLE SECTIONS EXAMPLE:
  First call list() to see existing sections. Suppose the last section is at top=90 with height=600.

  Second section should be:
  {
    "kind": "SECTION",
    "top": 690,  // 90 + 600 = 690
    "height": 500,
    "relTo": {"id": "<first-section-id-from-list>", "below": 0},
    "selectedGradientTheme": null
  }

  Third section should be:
  {
    "kind": "SECTION",
    "top": 1190,  // 690 + 500 = 1190
    "height": 400,
    "relTo": {"id": "<second-section-id>", "below": 0},
    "selectedGradientTheme": null
  }

COMMON MISTAKES TO AVOID:
- Using "header" as an ID (not a real ID - use list() to find real IDs)
- Missing relIn/relTo/relPage/relPara fields (always include them, even if null)
- Setting relTo.below to null (must be a number)
- Forgetting relIn for non-section components
- Missing required fields: inTemplate, wrap, mobileDown, mobileHide, onHover (see examples above)
- Missing empty arrays for TEXT: styles=[], paras=[], links=[]
- Missing text="" field for TEXT components with content
- Missing verticalAlignment for TEXT components
- Missing complete mobileSettings objects
- Wrapping content in CDATA tags (use plain HTML instead)
- Missing theme shadow properties for TEXT components
- Missing globalStyleId for styled components
- Missing style object with globalId/globalName/type for BUTTON components
- **CRITICAL FOR SECTIONS:**
  * Missing selectedGradientTheme: null (MUST be present for all sections)
  * Wrong top calculation (must be prev.top + prev.height)
  * Wrong relTo.id (must reference actual previous section ID from list())
  * Not chaining sections properly (each section must link to the previous one)

CONTENT/STYLES
- content: HTML content for TEXT components (STRICT: do NOT wrap in CDATA, use plain HTML; CDATA will be rejected)
- text: Empty string "" for TEXT components with content, or plain text for BUTTON/simple text
- styles: Empty array [] for TEXT components unless custom styles needed
- paras: Empty array [] for TEXT components unless paragraph metadata needed
- links: Empty array [] for TEXT components unless link metadata needed
- globalStyleId: Reference to global style (e.g., "EAEA20A6-C03E-4C8C-ADA5-43EBBEF4CD23")
- style/background: background.colorData.color=[\"HSL\", h,s,l,a], background.assetData.asset={url,width,height,etag,...}, repeat/position/size/scrollEffect/opacity supported.
- style/global refs: globalId, globalName, type, text={size: int or null}.
- Theming: selectedTheme/selectedGradientTheme, themeColorType, themeOverrideColor/themeHighlightColor/themeShadow*.
- Theme shadows: themeShadowBlurRadius=3, themeShadowColor=null, themeShadowOffsetX=3, themeShadowOffsetY=3 (defaults)
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

MUTATE_TOOL_DESCRIPTION = """Batch execute multiple CREATE and EDIT operations in a single optimized tool call.

CORE KINDS & DEFAULTS (for CREATE operations)
- SECTION: stretch=true, pin=0, selectedTheme="White", selectedGradientTheme=null, selectedBorderTheme=null, mobileSettings.size="cover", wrap=false (modernLayout accepted when provided)
- CONTAINER: wrap=false by default
- TEXT: fontSize=16, lineHeight=1.5, text="", styles=[], paras=[], links=[], mobileDown=false, mobileHide=false, verticalAlignment="top", mobileSettings={"align": null, "font": 0}, globalStyleId="GLOBAL_TEXT_STYLE_DEFAULT", themeShadowBlurRadius=3, themeShadowOffsetX=3, themeShadowOffsetY=3, themeShadowColor=null
- BUTTON: bold=true, corners.radius=5, fontSize=16, mobileDown=false, mobileHide=false, mobileSettings={"align": "justify"}, buttonThemeSelected="primary", style={border:null, background:null, globalId:"BUTTON_STYLE_DEFAULT", globalName:"[button.default]", type:"web.data.styles.StyleButton", text:{size:null}}
- CODE: use code + location + name along with layout/rel fields
- IMAGE/SVG/LOGO/MENU/FORM/MAP/etc. supported; pass required style/data as below.

SCHEMA RULES (for CREATE operations)
- Only the documented CreateInput fields are accepted (extra=forbid); use kind only (no legacy type field).
- Required subobjects must be complete: TEXT needs relIn, globalStyleId, mobileSettings, verticalAlignment, theme shadow values; BUTTON needs style + buttonThemeSelected; SECTION allows optional modernLayout; CONTACTFORM accepts fileUploadButtonStyle; BACKGROUND/STRIP fields include backgroundColor/size/repeat/position/attachment/clip/border/padding/selectedBorderTheme/asset/scrollEffect; CODE requires code/location/name.

CRITICAL REQUIRED FIELDS FOR ALL COMPONENTS (CREATE):
- inTemplate: false (default for non-template components)
- wrap: false (default for most components)
- mobileDown: false (unless specifically required)
- mobileHide: false (unless specifically required)
- onHover: null (unless hover effects are needed)
- relPage: null (always null in flat structure)
- relPara: null (always null unless text in paragraph flow)

LAYOUT (ABSOLUTE + RELATIVE, FLAT STRUCTURE)
All components live in a flat items[] array. Position is controlled by absolute coordinates (left/top/width/height) plus relIn/relTo for parent and sibling relationships.

CRITICAL RULES FOR relIn AND relTo:

1. SECTIONS:
   - relIn: MUST be null (sections have no parent)
   - relTo: CRITICAL - Each section must chain to the previous section/header
     * First section: relTo = {"id": "22FC8C5B-CD71-42B7-9DF2-486F577581A9", "below": 0}
     * Subsequent sections: relTo = {"id": "<previous-section-id>", "below": 0}
   - relPage: null, relPara: null
   - top: MUST be calculated precisely: previous_section.top + previous_section.height
   - IMPORTANT: Use list() to get the REAL previous section ID, never use placeholders
   - You can omit relTo for "SECTION" - it will be auto-populated, but providing it is safer

2. CHILDREN (TEXT, BUTTON, IMAGE, etc. inside a section):
   - relIn: REQUIRED - positions child relative to parent section
   - relTo: null for the FIRST child; subsequent children CAN chain to siblings
   - relPage: null, relPara: null

3. relIn MATH (for children inside a parent):
   - relIn.id = parent component ID
   - relIn.left = child.left - parent.left
   - relIn.top = child.top - parent.top
   - relIn.bottom = -(parent.height - (relIn.top + child.height))
   - relIn.right = -(parent.width - (relIn.left + child.width)) OR null

   EXAMPLE: Parent section at (left=0, top=90, width=1300, height=760)
            Child text at (left=185, top=250, width=680, height=260)
            relIn = {
              "id": "<section-id>",
              "left": 185,        // 185 - 0 = 185
              "top": 160,         // 250 - 90 = 160
              "right": null,
              "bottom": -340      // -(760 - (160 + 260)) = -340
            }

4. relTo for SIBLING CHAINING (optional, for children):
   - First child in section: relTo = null
   - To stack below a sibling: relTo = {"id": "<sibling-id>", "below": <gap_px>}
   - below MUST be a number (0, 10, 30, etc.), never null

   EXAMPLE: Button below a text block with 30px gap:
            relTo = {"id": "<text-component-id>", "below": 30}

COMMON MISTAKES TO AVOID:
- Using "header" as an ID (not a real ID - use list() to find real IDs)
- Missing relIn/relTo/relPage/relPara fields (always include them, even if null)
- Setting relTo.below to null (must be a number)
- Forgetting relIn for non-section components
- Missing required fields: inTemplate, wrap, mobileDown, mobileHide, onHover (see examples above)
- Missing empty arrays for TEXT: styles=[], paras=[], links=[]
- Missing text="" field for TEXT components with content
- Missing verticalAlignment for TEXT components
- Missing complete mobileSettings objects
- Wrapping content in CDATA tags (use plain HTML instead)
- Missing theme shadow properties for TEXT components
- Missing globalStyleId for styled components
- Missing style object with globalId/globalName/type for BUTTON components
- **CRITICAL FOR SECTIONS:**
  * Missing selectedGradientTheme: null (MUST be present for all sections)
  * Wrong top calculation (must be prev.top + prev.height)
  * Wrong relTo.id (must reference actual previous section ID from list())
  * Not chaining sections properly (each section must link to the previous one)

CONTENT/STYLES
- content: HTML content for TEXT components (STRICT: do NOT wrap in CDATA, use plain HTML; CDATA will be rejected)
- text: Empty string "" for TEXT components with content, or plain text for BUTTON/simple text
- styles: Empty array [] for TEXT components unless custom styles needed
- paras: Empty array [] for TEXT components unless paragraph metadata needed
- links: Empty array [] for TEXT components unless link metadata needed
- globalStyleId: Reference to global style (e.g., "EAEA20A6-C03E-4C8C-ADA5-43EBBEF4CD23")
- style/background: background.colorData.color=["HSL", h,s,l,a], background.assetData.asset={url,width,height,etag,...}, repeat/position/size/scrollEffect/opacity supported.
- style/global refs: globalId, globalName, type, text={size: int or null}.
- Theming: selectedTheme/selectedGradientTheme, themeColorType, themeOverrideColor/themeHighlightColor/themeShadow*.
- Theme shadows: themeShadowBlurRadius=3, themeShadowColor=null, themeShadowOffsetX=3, themeShadowOffsetY=3 (defaults)
- Border/corners/padding accept structured data; gradient/seo/hover/onHover/press/svgJson allow JSON blobs.

EDIT OPERATION BEHAVIOR:
- Shallow merges provided fields into target component; leaves other fields untouched
- Does not allow changing id or insertion-related fields; kind must match if provided
- Validates against the create schema to avoid invalid WSB keys

BATCH EXECUTION:
- **FAIL-FAST**: Operations execute sequentially. If ANY operation fails, ALL changes are rolled back.
- Page is loaded ONCE, operations apply in order, renumbered ONCE, saved ONCE.
- Returns list of results in the same order as input operations.
- You can add `alias` on CREATE operations. The tool auto-generates a real id (if you omit `id`) and maps the alias to that id so later operations can use the alias in relIn.id/relTo.id/parent_id/component_id.

WORKFLOW:
1. Call list() ONLY when you need IDs for pre-existing components that are not in your current plan/context. If you are creating a new section plus its children in the same batch (or editing items you just created earlier in the conversation), skip list() and use aliases.
2. Build operations array with {op: "CREATE"|"EDIT"|"REMOVE"|"REORDER", payload: {...}}.
3. For CREATE operations: follow all relIn/relTo rules above. If you need to reference this new component later in the batch, set an `alias` (preferred) or set an explicit `id` yourself; do NOT invent placeholder IDs.
4. For EDIT operations: provide component_id and fields to update. For REMOVE: provide component_id. For REORDER: provide order_ids and optional parent_id.
5. Call mutate_components with operations array

INPUTS:
- operations: required list of {op: "CREATE"|"EDIT", payload: CreateInput|EditInput}
- file_path: optional path to page JSON; defaults to static/wsb/page.json
- response_format: "concise" (default) or "detailed"

EXAMPLE BATCH:
{
  "operations": [
    {
      "op": "CREATE",
      "alias": "hero",
      "payload": {
        "kind": "SECTION",
        "left": 0,
        "top": 790,
        "width": 1300,
        "height": 600,
        "relIn": null,
        "relTo": {"id": "7F6F7D6E-006A-4E0F-9683-47E2B78C70ED", "below": 0},
        "relPage": null,
        "relPara": null,
        "inTemplate": false,
        "wrap": false,
        "stretch": true,
        "pin": 0,
        "selectedTheme": "White",
        "selectedGradientTheme": null,
        "mobileSettings": {"size": "cover"},
        "style": {
          "border": null,
          "background": {
            "colorData": {
              "color": ["HSL", 0.08, 0.15, 0.95, 1],
              "gradient": null
            }
          }
        }
      }
    },
    {
      "op": "CREATE",
      "alias": "hero-title",
      "payload": {
        "kind": "TEXT",
        "left": 100,
        "top": 850,
        "width": 600,
        "height": 100,
        "relIn": {"id": "hero", "left": 100, "top": 60, "bottom": -440},
        "relTo": null,
        "relPage": null,
        "relPara": null,
        "inTemplate": false,
        "wrap": false,
        "mobileDown": false,
        "mobileHide": false,
        "onHover": null,
        "content": "<h2>New Section Header</h2>",
        "text": "",
        "styles": [],
        "paras": [],
        "links": [],
        "verticalAlignment": "top",
        "mobileSettings": {"align": null, "font": 0},
        "globalStyleId": "GLOBAL_TEXT_STYLE_DEFAULT",
        "themeShadowBlurRadius": 3,
        "themeShadowOffsetX": 3,
        "themeShadowOffsetY": 3,
        "themeShadowColor": null
      }
    },
    {
      "op": "EDIT",
      "payload": {
        "component_id": "53CC0F05-26B3-4B79-B036-19460EA6F945",
        "text": "Updated Button"
      }
    }
  ]
}"""
