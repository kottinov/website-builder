"""Constants used across the react_agent module."""

from react_agent.signatures import CreateInput

DEFAULT_HEADER_ID = "22FC8C5B-CD71-42B7-9DF2-486F577581A9"
EDIT_EXCLUDE_FIELDS = {"component_id", "file_path", "kind", "response_format"}

EDIT_VALIDATION_FIELDS = {
    name
    for name in CreateInput.model_fields
    if name
    not in {
        "file_path",
        "parent_id",
        "before_id",
        "after_id",
        "kind",
        "response_format",
    }
}

FAKE_ID_PATTERNS = [
    "temp",
    "anchor",
    "placeholder",
    "dummy",
    "fake",
    "mock",
]

CACHEABLE_TOOL_NAMES = {"mutate_components"}