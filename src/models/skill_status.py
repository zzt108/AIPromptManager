"""Skill status enum for AI Prompt Manager."""

from enum import Enum


class SkillStatus(str, Enum):
    """Recognition status for skills in the registry.

    Inherits from str to allow direct JSON serialization.
    """

    VALID = "valid"
    UNRECOGNIZED = "unrecognized"
    PARSE_ERROR = "parse_error"
