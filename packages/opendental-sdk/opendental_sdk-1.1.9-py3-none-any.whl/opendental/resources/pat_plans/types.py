"""PatPlan types and enums for Open Dental SDK."""

from enum import Enum


class RelationshipType(str, Enum):
    """Relationship to subscriber enum matching Open Dental API."""
    SELF = "Self"
    SPOUSE = "Spouse"
    CHILD = "Child"
    EMPLOYEE = "Employee"
    HANDICAP_DEP = "HandicapDep"
    SIGNIF_OTHER = "SignifOther"
    INJURED_PLANTIFF = "InjuredPlantiff"
    LIFE_PARTNER = "LifePartner"
    DEPENDENT = "Dependent"


class OrdinalType(int, Enum):
    """Insurance ordinal (priority) enum."""
    PRIMARY = 1
    SECONDARY = 2
    TERTIARY = 3

