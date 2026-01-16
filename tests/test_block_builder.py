"""Tests for BlockBuilder domain class."""

import sys
from pathlib import Path

import pytest

# Add spotify_api to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "spotify_api"))

from domain.slack.block_builder import BlockBuilder


class TestBlockBuilder:
    """Test cases for BlockBuilder."""

    def test_initial_state_is_empty(self) -> None:
        """Test that BlockBuilder starts with empty blocks."""
        builder = BlockBuilder()
        assert builder.blocks == []
        assert builder.build() == []

    def test_add_section(self) -> None:
        """Test adding a section block."""
        builder = BlockBuilder().add_section(text="Hello World")
        blocks = builder.build()

        assert len(blocks) == 1
        assert blocks[0]["type"] == "section"
        assert blocks[0]["text"]["type"] == "mrkdwn"
        assert blocks[0]["text"]["text"] == "Hello World"

    def test_add_divider(self) -> None:
        """Test adding a divider block."""
        builder = BlockBuilder().add_divider()
        blocks = builder.build()

        assert len(blocks) == 1
        assert blocks[0]["type"] == "divider"

    def test_add_button_action(self) -> None:
        """Test adding a button action block."""
        builder = BlockBuilder().add_button_action(
            action_id="test_action",
            text="Click Me",
            value="button_value",
            style="primary",
        )
        blocks = builder.build()

        assert len(blocks) == 1
        assert blocks[0]["type"] == "actions"
        element = blocks[0]["elements"][0]
        assert element["type"] == "button"
        assert element["text"]["text"] == "Click Me"
        assert element["value"] == "button_value"
        assert element["style"] == "primary"
        assert element["action_id"] == "test_action"

    def test_add_context_with_string(self) -> None:
        """Test adding a context block with string."""
        builder = BlockBuilder().add_context(text="Context info")
        blocks = builder.build()

        assert len(blocks) == 1
        assert blocks[0]["type"] == "context"
        assert blocks[0]["elements"][0]["type"] == "plain_text"
        assert blocks[0]["elements"][0]["text"] == "Context info"

    def test_add_context_with_dict(self) -> None:
        """Test adding a context block with dict (serialized to JSON)."""
        builder = BlockBuilder().add_context(text={"key": "value"})
        blocks = builder.build()

        assert len(blocks) == 1
        assert blocks[0]["type"] == "context"
        assert blocks[0]["elements"][0]["text"] == '{"key": "value"}'

    def test_add_mrkdwn_section(self) -> None:
        """Test adding a markdown section block."""
        builder = BlockBuilder().add_mrkdwn_section(text="*Bold* _italic_")
        blocks = builder.build()

        assert len(blocks) == 1
        assert blocks[0]["type"] == "section"
        assert blocks[0]["block_id"] == "mrkdwn-section"
        assert blocks[0]["text"]["type"] == "mrkdwn"
        assert blocks[0]["text"]["text"] == "*Bold* _italic_"

    def test_add_checkboxes(self) -> None:
        """Test adding checkboxes section block."""
        options = [
            {"text": "Option 1", "value": "opt1"},
            {"text": "Option 2", "value": "opt2"},
        ]
        builder = BlockBuilder().add_checkboxes(
            action_id="checkbox_action",
            header="Select options",
            options=options,
        )
        blocks = builder.build()

        assert len(blocks) == 1
        assert blocks[0]["type"] == "section"
        assert blocks[0]["text"]["text"] == "Select options"
        accessory = blocks[0]["accessory"]
        assert accessory["type"] == "checkboxes"
        assert accessory["action_id"] == "checkbox_action"
        assert len(accessory["options"]) == 2

    def test_add_checkboxes_action(self) -> None:
        """Test adding checkboxes action block."""
        options = [
            {"text": "Option 1", "value": "opt1", "description": "First option"},
            {"text": "Option 2", "value": "opt2"},
        ]
        builder = BlockBuilder().add_checkboxes_action(
            action_id="checkbox_action",
            options=options,
        )
        blocks = builder.build()

        assert len(blocks) == 1
        assert blocks[0]["type"] == "actions"
        element = blocks[0]["elements"][0]
        assert element["type"] == "checkboxes"
        assert len(element["options"]) == 2
        # First option has description
        assert "description" in element["options"][0]
        # Second option has no description
        assert "description" not in element["options"][1]

    def test_add_plain_text_input(self) -> None:
        """Test adding plain text input block."""
        builder = BlockBuilder().add_plain_text_input(
            action_id="input_action",
            label="Enter text",
            multiline=True,
            optional=True,
        )
        blocks = builder.build()

        assert len(blocks) == 1
        assert blocks[0]["type"] == "input"
        assert blocks[0]["label"]["text"] == "Enter text"
        assert blocks[0]["optional"] is True
        element = blocks[0]["element"]
        assert element["type"] == "plain_text_input"
        assert element["multiline"] is True
        assert element["action_id"] == "input_action"

    def test_add_static_select(self) -> None:
        """Test adding static select block."""
        options = [
            {"text": "Option 1", "value": "opt1"},
            {"text": "Option 2", "value": "opt2"},
        ]
        builder = BlockBuilder().add_static_select(
            action_id="select_action",
            options=options,
            label="Select one",
            placeholder="Choose...",
        )
        blocks = builder.build()

        assert len(blocks) == 1
        assert blocks[0]["type"] == "input"
        assert blocks[0]["label"]["text"] == "Select one"
        element = blocks[0]["element"]
        assert element["type"] == "static_select"
        assert element["placeholder"]["text"] == "Choose..."
        assert len(element["options"]) == 2

    def test_add_multi_static_select(self) -> None:
        """Test adding multi static select block."""
        options = [
            {"text": "Option 1", "value": "opt1"},
            {"text": "Option 2", "value": "opt2"},
        ]
        builder = BlockBuilder().add_multi_static_select(
            action_id="multi_select_action",
            options=options,
        )
        blocks = builder.build()

        assert len(blocks) == 1
        element = blocks[0]["element"]
        assert element["type"] == "multi_static_select"

    def test_add_datepicker(self) -> None:
        """Test adding datepicker block."""
        builder = BlockBuilder().add_datepicker(
            action_id="date_action",
            header="Select date",
            placeholder="Pick a date",
            initial_date="2024-01-01",
        )
        blocks = builder.build()

        assert len(blocks) == 1
        assert blocks[0]["type"] == "section"
        assert blocks[0]["text"]["text"] == "Select date"
        accessory = blocks[0]["accessory"]
        assert accessory["type"] == "datepicker"
        assert accessory["initial_date"] == "2024-01-01"
        assert accessory["placeholder"]["text"] == "Pick a date"

    def test_add_timepicker(self) -> None:
        """Test adding timepicker block."""
        builder = BlockBuilder().add_timepicker(
            action_id="time_action",
            placeholder="Select time",
            initial_time="09:00",
            label="Time",
        )
        blocks = builder.build()

        assert len(blocks) == 1
        assert blocks[0]["type"] == "input"
        assert blocks[0]["label"]["text"] == "Time"
        element = blocks[0]["element"]
        assert element["type"] == "timepicker"
        assert element["initial_time"] == "09:00"

    def test_chaining_multiple_blocks(self) -> None:
        """Test chaining multiple blocks together."""
        builder = (
            BlockBuilder()
            .add_section(text="Header")
            .add_divider()
            .add_button_action(action_id="btn", text="Button", value="val")
            .add_context(text="Footer")
        )
        blocks = builder.build()

        assert len(blocks) == 4
        assert blocks[0]["type"] == "section"
        assert blocks[1]["type"] == "divider"
        assert blocks[2]["type"] == "actions"
        assert blocks[3]["type"] == "context"

    def test_builder_is_immutable(self) -> None:
        """Test that BlockBuilder is immutable (frozen dataclass)."""
        from dataclasses import FrozenInstanceError

        builder = BlockBuilder()

        with pytest.raises(FrozenInstanceError):
            builder.blocks = [{"type": "section"}]

    def test_original_builder_unchanged_after_add(self) -> None:
        """Test that adding blocks returns a new instance."""
        original = BlockBuilder()
        modified = original.add_section(text="Test")

        assert original.blocks == []
        assert len(modified.blocks) == 1
        assert original is not modified
