"""InsSub types and enums for Open Dental SDK."""

from enum import Enum


class AuthorizationType(str, Enum):
    """Authorization values for ReleaseInfo and AssignBen fields."""
    TRUE = "true"
    FALSE = "false"

