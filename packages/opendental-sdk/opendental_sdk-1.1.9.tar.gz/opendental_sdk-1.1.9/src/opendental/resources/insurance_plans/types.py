"""Insurance Plan types and enums for Open Dental SDK."""

from enum import Enum


class PlanType(str, Enum):
    """
    Insurance plan type enum matching Open Dental API.
    
    Percentage PlanTypes are stored as blank in the database.
    """
    PERCENTAGE = ""  # Percentage
    PPO_PERCENTAGE = "p"  # PPO Percentage
    FLAT_COPAY = "f"  # Flat Copay
    CAPITATION = "c"  # Capitation


class CobRule(str, Enum):
    """Coordination of Benefits (COB) rule enum."""
    BASIC = "Basic"
    STANDARD = "Standard"
    CARVE_OUT = "CarveOut"
    SECONDARY_MEDICAID = "SecondaryMedicaid"


class ExclusionFeeRule(str, Enum):
    """Exclusion fee rule enum."""
    PRACTICE_DEFAULT = "PracticeDefault"
    DO_NOTHING = "DoNothing"
    USE_UCR_FEE = "UseUcrFee"


class WriteOffOverride(str, Enum):
    """Write-off override enum."""
    DEFAULT = "Default"
    YES = "Yes"
    NO = "No"