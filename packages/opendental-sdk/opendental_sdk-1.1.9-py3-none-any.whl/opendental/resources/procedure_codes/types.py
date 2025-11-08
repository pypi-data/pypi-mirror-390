"""procedurecode types and enums for Open Dental SDK."""

from enum import Enum


class TreatmentArea(str, Enum):
    """Treatment area types for procedures."""
    SURFACE = "Surface"
    TOOTH = "Tooth"
    MOUTH = "Mouth"
    ARCH = "Arch"
    QUADRANT = "Quadrant"
    SEXTANT = "Sextant"
    TOOTHRANGE = "ToothRange"


class PaintType(str, Enum):
    """Paint types for procedure visualization."""
    EXTRACTED = "Extracted"
    CROWN = "Crown"
    FILLINGDARK = "FillingDark"
    FILLINGLIGHT = "FillingLight"
    CROWN_PORCELAIN = "CrownPorcelain"
    SEALANT = "Sealant"
    VENEER = "Veneer"
    WATCH = "Watch"
    RCT = "RCT"
    POSTBUILDUP = "PostBuildUp"
    MISSING = "Missing"
    RETAINER = "Retainer"
    CANTILEVER = "Cantilever"
    PONTIC = "Pontic"
    IMPLANT = "Implant"
    ABUTMENT = "Abutment"
