"""Tests for NamingService."""

from __future__ import annotations

from pathlib import Path

import pytest

from models.conventions_schema import ConventionsSchema, FileNaming
from services.naming_service import NamingService


@pytest.fixture
def default_naming_service() -> NamingService:
    """Create NamingService with default conventions."""
    return NamingService(ConventionsSchema.get_default())


class TestParseFilename:
    """Tests for parse_filename method."""

    def test_parse_versioned_filename(
        self, default_naming_service: NamingService
    ) -> None:
        """Test parsing a versioned filename."""
        result = default_naming_service.parse_filename("GUIDE-1-2-General.md")
        assert result["type"] == "GUIDE"
        assert result["major"] == 1
        assert result["minor"] == 2
        assert result["basename"] == "General"
        assert result["is_versionless"] is False

    def test_parse_versionless_filename(
        self, default_naming_service: NamingService
    ) -> None:
        """Test parsing a version-less filename."""
        result = default_naming_service.parse_filename("GUIDE--General.md")
        assert result["type"] == "GUIDE"
        assert result["major"] == 0
        assert result["minor"] == 0
        assert result["basename"] == "General"
        assert result["is_versionless"] is True

    def test_parse_subtype_filename(
        self, default_naming_service: NamingService
    ) -> None:
        """Test parsing filename with subtype in type."""
        result = default_naming_service.parse_filename("GUIDE_CC-1-0-CodingConvention.md")
        assert result["type"] == "GUIDE_CC"
        assert result["major"] == 1
        assert result["minor"] == 0
        assert result["basename"] == "CodingConvention"

    def test_parse_invalid_filename_raises_error(
        self, default_naming_service: NamingService
    ) -> None:
        """Test parsing invalid filename raises ValueError."""
        with pytest.raises(ValueError, match="doesn't match expected pattern"):
            default_naming_service.parse_filename("invalid-file.txt")

    def test_parse_no_extension_raises_error(
        self, default_naming_service: NamingService
    ) -> None:
        """Test parsing filename without .md raises error."""
        with pytest.raises(ValueError):
            default_naming_service.parse_filename("GUIDE-1-0-Test")


class TestExtractMetadata:
    """Tests for extract_metadata method."""

    def test_extract_metadata_versioned(
        self, default_naming_service: NamingService
    ) -> None:
        """Test extract_metadata returns correct tuple."""
        path = Path("prompts/GUIDE-1-2-General.md")
        type_str, major, minor, basename = default_naming_service.extract_metadata(path)
        assert type_str == "GUIDE"
        assert major == 1
        assert minor == 2
        assert basename == "General"

    def test_extract_metadata_versionless(
        self, default_naming_service: NamingService
    ) -> None:
        """Test extract_metadata for version-less file."""
        path = Path("prompts/SPACE--WebDev.md")
        type_str, major, minor, basename = default_naming_service.extract_metadata(path)
        assert type_str == "SPACE"
        assert major == 0
        assert minor == 0
        assert basename == "WebDev"


class TestMakeVersionless:
    """Tests for make_versionless method."""

    def test_make_versionless_from_versioned(
        self, default_naming_service: NamingService
    ) -> None:
        """Test converting versioned to version-less."""
        result = default_naming_service.make_versionless("GUIDE-1-2-General.md")
        assert result == "GUIDE--General.md"

    def test_make_versionless_already_versionless(
        self, default_naming_service: NamingService
    ) -> None:
        """Test version-less filename returns unchanged."""
        result = default_naming_service.make_versionless("GUIDE--General.md")
        assert result == "GUIDE--General.md"

    def test_make_versionless_with_subtype(
        self, default_naming_service: NamingService
    ) -> None:
        """Test make_versionless preserves subtype."""
        result = default_naming_service.make_versionless("GUIDE_CC-1-0-CodingConvention.md")
        assert result == "GUIDE_CC--CodingConvention.md"

    def test_make_versionless_unknown_format_unchanged(
        self, default_naming_service: NamingService
    ) -> None:
        """Test unknown format returns unchanged."""
        result = default_naming_service.make_versionless("random-file.txt")
        assert result == "random-file.txt"


class TestMakeVersioned:
    """Tests for make_versioned method."""

    def test_make_versioned_simple(
        self, default_naming_service: NamingService
    ) -> None:
        """Test creating versioned filename."""
        result = default_naming_service.make_versioned(
            basename="General",
            major=1,
            minor=3,
            type_str="GUIDE",
        )
        assert result == "GUIDE-1-3-General.md"

    def test_make_versioned_with_subtype(
        self, default_naming_service: NamingService
    ) -> None:
        """Test creating versioned filename with subtype."""
        result = default_naming_service.make_versioned(
            basename="CodingConvention",
            major=2,
            minor=0,
            type_str="GUIDE_CC",
        )
        assert result == "GUIDE_CC-2-0-CodingConvention.md"


class TestValidateFilename:
    """Tests for validate_filename method."""

    def test_validate_versioned_filename(
        self, default_naming_service: NamingService
    ) -> None:
        """Test valid versioned filename returns True."""
        assert default_naming_service.validate_filename("GUIDE-1-0-Test.md") is True

    def test_validate_versionless_filename(
        self, default_naming_service: NamingService
    ) -> None:
        """Test valid version-less filename returns True."""
        assert default_naming_service.validate_filename("GUIDE--Test.md") is True

    def test_validate_invalid_filename(
        self, default_naming_service: NamingService
    ) -> None:
        """Test invalid filename returns False."""
        assert default_naming_service.validate_filename("invalid.txt") is False


class TestTypeOperations:
    """Tests for type-related operations."""

    def test_get_parent_type_simple(
        self, default_naming_service: NamingService
    ) -> None:
        """Test get_parent_type with simple type."""
        assert default_naming_service.get_parent_type("GUIDE") == "GUIDE"

    def test_get_parent_type_subtype(
        self, default_naming_service: NamingService
    ) -> None:
        """Test get_parent_type extracts parent."""
        assert default_naming_service.get_parent_type("GUIDE_CC") == "GUIDE"

    def test_is_known_type_recognized(
        self, default_naming_service: NamingService
    ) -> None:
        """Test is_known_type returns True for known types."""
        assert default_naming_service.is_known_type("GUIDE") is True
        assert default_naming_service.is_known_type("GUIDE_CC") is True

    def test_is_known_type_unrecognized(
        self, default_naming_service: NamingService
    ) -> None:
        """Test is_known_type returns False for unknown types."""
        assert default_naming_service.is_known_type("UNKNOWN") is False
