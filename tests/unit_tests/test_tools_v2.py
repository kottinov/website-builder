"""Tests for the v2 consolidated tools architecture."""

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from react_agent.tools_v2 import get_components, mutate_components


@pytest.fixture
def sample_page() -> Dict[str, Any]:
    """Create a sample page structure for testing."""
    return {
        "items": [
            {
                "id": "SECTION-001",
                "kind": "SECTION",
                "orderIndex": 0,
                "left": 0,
                "top": 90,
                "width": 1300,
                "height": 600,
                "relIn": None,
                "relTo": {"id": "HEADER-001", "below": 0},
                "title": "Hero Section",
                "stretch": True,
                "selectedTheme": "Main",
                "selectedGradientTheme": None,
            },
            {
                "id": "TEXT-001",
                "kind": "TEXT",
                "orderIndex": 1,
                "left": 100,
                "top": 150,
                "width": 500,
                "height": 100,
                "relIn": {
                    "id": "SECTION-001",
                    "left": 100,
                    "top": 60,
                    "right": -700,
                    "bottom": -440,
                },
                "relTo": None,
                "content": "<p>Welcome to our site</p>",
                "text": "Welcome to our site",
                "title": "Heading Text",
            },
        ]
    }


@pytest.fixture
def temp_page_file(tmp_path: Path, sample_page: Dict[str, Any]) -> Path:
    """Create a temporary page JSON file."""
    page_file = tmp_path / "page.json"
    page_file.write_text(json.dumps(sample_page, indent=2))
    return page_file


def test_get_components_all(temp_page_file: Path):
    """Test getting all components."""
    result = get_components.invoke({"file_path": str(temp_page_file)})

    assert len(result) == 2
    assert result[0]["id"] == "SECTION-001"
    assert result[0]["kind"] == "SECTION"
    assert result[1]["id"] == "TEXT-001"


def test_get_components_by_kind(temp_page_file: Path):
    """Test filtering by component kind."""
    result = get_components.invoke({
        "file_path": str(temp_page_file),
        "kinds": ["SECTION"]
    })

    assert len(result) == 1
    assert result[0]["kind"] == "SECTION"


def test_get_components_by_parent(temp_page_file: Path):
    """Test filtering by parent ID."""
    result = get_components.invoke({
        "file_path": str(temp_page_file),
        "parent_id": "SECTION-001"
    })

    assert len(result) == 1
    assert result[0]["id"] == "TEXT-001"


def test_get_components_text_search(temp_page_file: Path):
    """Test text search filtering."""
    result = get_components.invoke({
        "file_path": str(temp_page_file),
        "text_contains": "Welcome"
    })

    assert len(result) == 1
    assert result[0]["id"] == "TEXT-001"


def test_get_components_custom_fields(temp_page_file: Path):
    """Test custom field projection."""
    result = get_components.invoke({
        "file_path": str(temp_page_file),
        "fields": ["id", "kind"]
    })

    assert len(result) == 2
    assert set(result[0].keys()) == {"id", "kind"}


def test_get_components_detailed(temp_page_file: Path):
    """Test detailed response format."""
    result = get_components.invoke({
        "file_path": str(temp_page_file),
        "response_format": "detailed"
    })

    assert len(result) == 2
    assert "width" in result[0]
    assert "height" in result[0]
    assert "relIn" in result[0]


def test_mutate_remove(temp_page_file: Path):
    """Test remove operation."""
    result = mutate_components.invoke({
        "file_path": str(temp_page_file),
        "operations": [
            {"op": "remove", "id": "TEXT-001"}
        ]
    })

    assert len(result) == 1
    assert result[0]["success"] is True

    # Verify component was removed
    components = get_components.invoke({"file_path": str(temp_page_file)})
    assert len(components) == 1
    assert components[0]["id"] == "SECTION-001"


def test_mutate_edit(temp_page_file: Path):
    """Test edit operation."""
    result = mutate_components.invoke({
        "file_path": str(temp_page_file),
        "operations": [
            {
                "op": "edit",
                "id": "TEXT-001",
                "payload": {"width": 600, "height": 150}
            }
        ]
    })

    assert len(result) == 1
    assert result[0]["id"] == "TEXT-001"

    # Verify changes
    components = get_components.invoke({
        "file_path": str(temp_page_file),
        "ids": ["TEXT-001"],
        "response_format": "detailed"
    })
    assert components[0]["width"] == 600
    assert components[0]["height"] == 150


def test_mutate_batch_operations(temp_page_file: Path):
    """Test multiple operations in one call."""
    result = mutate_components.invoke({
        "file_path": str(temp_page_file),
        "operations": [
            {
                "op": "edit",
                "id": "TEXT-001",
                "payload": {"width": 700}
            },
            {
                "op": "edit",
                "id": "SECTION-001",
                "payload": {"height": 800}
            }
        ]
    })

    assert len(result) == 2
    assert result[0]["id"] == "TEXT-001"
    assert result[1]["id"] == "SECTION-001"

    # Verify both changes
    components = get_components.invoke({
        "file_path": str(temp_page_file),
        "response_format": "detailed"
    })

    text_comp = next(c for c in components if c["id"] == "TEXT-001")
    section_comp = next(c for c in components if c["id"] == "SECTION-001")

    assert text_comp["width"] == 700
    assert section_comp["height"] == 800


def test_mutate_create_with_manual_position(temp_page_file: Path):
    """Test create operation with manual positioning."""
    result = mutate_components.invoke({
        "file_path": str(temp_page_file),
        "operations": [
            {
                "op": "create",
                "payload": {
                    "kind": "BUTTON",
                    "left": 100,
                    "top": 300,
                    "width": 200,
                    "height": 50,
                    "text": "Click me",
                    "relIn": {
                        "id": "SECTION-001",
                        "left": 100,
                        "top": 210,
                        "right": -1000,
                        "bottom": -240
                    },
                    "relTo": {"id": "TEXT-001", "below": 50},
                    "style": {
                        "globalId": "BTN-001",
                        "globalName": "[button.default]",
                        "type": "web.data.styles.StyleButton",
                        "text": {"size": None}
                    },
                    "buttonThemeSelected": "primary"
                }
            }
        ]
    })

    assert len(result) == 1
    if "error" in result[0]:
        pytest.fail(f"Create operation failed: {result[0]['error']}")
    assert result[0]["kind"] == "BUTTON"

    # Verify component was created
    components = get_components.invoke({
        "file_path": str(temp_page_file),
        "kinds": ["BUTTON"]
    })
    assert len(components) == 1
    assert components[0]["title"] == "Click me"


def test_error_handling_invalid_operation(temp_page_file: Path):
    """Test error handling for invalid operations."""
    result = mutate_components.invoke({
        "file_path": str(temp_page_file),
        "operations": [
            {
                "op": "edit",
                "id": "NONEXISTENT-ID",
                "payload": {"width": 500}
            }
        ]
    })

    assert len(result) == 1
    assert "error" in result[0]


def test_error_handling_missing_required_field(temp_page_file: Path):
    """Test error handling for missing required fields."""
    result = mutate_components.invoke({
        "file_path": str(temp_page_file),
        "operations": [
            {
                "op": "remove"
                # Missing required 'id' field
            }
        ]
    })

    assert len(result) == 1
    assert "error" in result[0]


def test_failed_edit_does_not_mutate_page(temp_page_file: Path):
    """Failed edits should not persist invalid changes to disk."""
    before = json.loads(temp_page_file.read_text())

    result = mutate_components.invoke({
        "file_path": str(temp_page_file),
        "operations": [
            {
                "op": "edit",
                "id": "TEXT-001",
                "payload": {"relIn": {"id": "BAD-PARENT"}},  # missing offsets triggers validation
            }
        ],
    })

    after = json.loads(temp_page_file.read_text())

    assert len(result) == 1
    assert "error" in result[0]
    assert after == before
