"""Tests for ConventionsSchema and FileNaming models."""

from __future__ import annotations

import pytest

from models.conventions_schema import ConventionsSchema, FileNaming


class TestFileNaming:
    """Tests for FileNaming dataclass."""

    def test_default_values(self) -> None:
        """Test FileNaming has correct defaults."""
        naming = FileNaming()
        assert naming.pattern == "{TYPE}-{VERSION}-{DESCRIPTION}"
        assert naming.version_format == "X-Y"
        assert naming.output_pattern == "{TYPE}--{DESCRIPTION}"
        assert naming.type_separator == "_"
        assert "GUIDE" in naming.supported_types

    def test_from_dict_with_values(self) -> None:
        """Test from_dict populates all fields."""
        data = {
            "pattern": "{TYPE}_{VERSION}_{DESCRIPTION}",
            "version_format": "X.Y",
            "supported_types": ["CUSTOM", "TYPE"],
            "output_pattern": "{TYPE}_{DESCRIPTION}",
            "type_separator": "-",
        }
        naming = FileNaming.from_dict(data)
        assert naming.pattern == "{TYPE}_{VERSION}_{DESCRIPTION}"
        assert naming.version_format == "X.Y"
        assert naming.supported_types == ["CUSTOM", "TYPE"]
        assert naming.output_pattern == "{TYPE}_{DESCRIPTION}"
        assert naming.type_separator == "-"

    def test_from_dict_uses_defaults_for_missing(self) -> None:
        """Test from_dict uses defaults for missing keys."""
        naming = FileNaming.from_dict({})
        assert naming.pattern == "{TYPE}-{VERSION}-{DESCRIPTION}"
        assert naming.type_separator == "_"

    def test_to_dict_round_trip(self) -> None:
        """Test to_dict produces data that from_dict can read."""
        original = FileNaming(
            pattern="custom",
            version_format="X.Y.Z",
            supported_types=["A", "B"],
            output_pattern="out",
            type_separator=".",
        )
        data = original.to_dict()
        restored = FileNaming.from_dict(data)
        assert restored.pattern == original.pattern
        assert restored.type_separator == original.type_separator


class TestConventionsSchema:
    """Tests for ConventionsSchema dataclass."""

    def test_default_creates_file_naming(self) -> None:
        """Test default ConventionsSchema has FileNaming."""
        schema = ConventionsSchema()
        assert schema.file_naming is not None
        assert schema.file_naming.pattern == "{TYPE}-{VERSION}-{DESCRIPTION}"

    def test_get_default_returns_valid_schema(self) -> None:
        """Test get_default() returns a working schema."""
        schema = ConventionsSchema.get_default()
        assert schema.file_naming.pattern == "{TYPE}-{VERSION}-{DESCRIPTION}"
        assert "GUIDE" in schema.file_naming.supported_types

    def test_from_dict_with_file_naming(self) -> None:
        """Test from_dict parses file_naming section."""
        data = {
            "file_naming": {
                "pattern": "custom",
                "type_separator": ".",
            }
        }
        schema = ConventionsSchema.from_dict(data)
        assert schema.file_naming.pattern == "custom"
        assert schema.file_naming.type_separator == "."

    def test_to_dict_round_trip(self) -> None:
        """Test to_dict produces valid JSON structure."""
        original = ConventionsSchema.get_default()
        data = original.to_dict()
        restored = ConventionsSchema.from_dict(data)
        assert restored.file_naming.pattern == original.file_naming.pattern

    def test_extract_parent_type_simple(self) -> None:
        """Test extract_parent_type with simple type."""
        schema = ConventionsSchema.get_default()
        assert schema.extract_parent_type("GUIDE") == "GUIDE"

    def test_extract_parent_type_with_subtype(self) -> None:
        """Test extract_parent_type extracts parent from subtype."""
        schema = ConventionsSchema.get_default()
        assert schema.extract_parent_type("GUIDE_CC") == "GUIDE"
        assert schema.extract_parent_type("SPACE_WEB") == "SPACE"

    def test_extract_parent_type_custom_separator(self) -> None:
        """Test extract_parent_type with custom separator."""
        schema = ConventionsSchema(file_naming=FileNaming(type_separator="-"))
        assert schema.extract_parent_type("GUIDE-CC") == "GUIDE"

    def test_is_known_type_simple(self) -> None:
        """Test is_known_type recognizes supported types."""
        schema = ConventionsSchema.get_default()
        assert schema.is_known_type("GUIDE") is True
        assert schema.is_known_type("SPACE") is True
        assert schema.is_known_type("UNKNOWN") is False

    def test_is_known_type_subtype(self) -> None:
        """Test is_known_type recognizes subtypes of known types."""
        schema = ConventionsSchema.get_default()
        assert schema.is_known_type("GUIDE_CC") is True
        assert schema.is_known_type("SPACE_WEB") is True
        assert schema.is_known_type("UNKNOWN_SUB") is False
