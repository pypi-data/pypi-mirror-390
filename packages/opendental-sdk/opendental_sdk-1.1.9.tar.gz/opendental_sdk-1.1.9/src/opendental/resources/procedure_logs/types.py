"""ProcedureLog types and enums for Open Dental SDK."""

from enum import Enum


class ProcedureStatus(str, Enum):
    """
    Procedure status enum matching Open Dental API.
    
    Reference: https://www.opendental.com/site/apiprocedurelogs.html
    """
    TREATMENT_PLAN = "TP"  # Treatment Plan
    COMPLETE = "C"  # Complete
    EXISTING_CURRENT_PROVIDER = "EC"  # Existing Current Provider
    EXISTING_OTHER_PROVIDER = "EO"  # Existing Other Provider
    REFERRED_OUT = "R"  # Referred Out
    DELETED = "D"  # Deleted
    CONDITION = "Cn"  # Condition
    TREATMENT_PLAN_INACTIVE = "TPi"  # Treatment Plan inactive


class PlaceOfService(str, Enum):
    """
    Place of service enum for procedure logs.
    
    Common values based on Open Dental documentation.
    """
    OFFICE = "Office"
    INPATIENT_HOSPITAL = "InpatHospital"
    OUTPATIENT_HOSPITAL = "OutpatHospital"
    PATIENTS_HOME = "PatientsHome"
    NURSING_HOME = "NursingHome"
    PUBLIC_HEALTH_CLINIC = "PublicHealthClinic"
    EMERGENCY_ROOM = "EmergencyRoom"
    SKILLED_NURSING_FACILITY = "SkilledNursingFacility"


class Prosthesis(str, Enum):
    """
    Prosthesis code enum for procedure logs.
    
    Common values based on Open Dental documentation.
    """
    INITIAL = "I"  # Initial placement
    REPLACEMENT = "R"  # Replacement


class BooleanString(str, Enum):
    """
    Boolean string values used in the API.
    
    Many Open Dental API fields use string "true"/"false" instead of boolean.
    """
    TRUE = "true"
    FALSE = "false"


class InsuranceHistoryCategory(str, Enum):
    """
    Insurance history category names (case sensitive).
    
    These correspond to preference names that store procedure codes
    for different insurance coverage categories.
    
    Used for both GET and POST InsuranceHistory endpoints.
    """
    # Common categories
    BITEWING_CODES = "InsHistBWCodes"  # Bitewing X-rays
    PANO_CODES = "InsHistPanoCodes"  # Panoramic X-rays
    EXAM_CODES = "InsHistExamCodes"  # Examinations
    PROPHY_CODES = "InsHistProphyCodes"  # Prophylaxis (cleanings)
    
    # Periodontal categories (quadrants)
    PERIO_UR_CODES = "InsHistPerioURCodes"  # Periodontal Upper Right
    PERIO_UL_CODES = "InsHistPerioULCodes"  # Periodontal Upper Left
    PERIO_LR_CODES = "InsHistPerioLRCodes"  # Periodontal Lower Right
    PERIO_LL_CODES = "InsHistPerioLLCodes"  # Periodontal Lower Left
    PERIO_MAINT_CODES = "InsHistPerioMaintCodes"  # Periodontal Maintenance
    
    # Other categories
    DEBRIDEMENT_CODES = "InsHistDebridementCodes"  # Debridement
    FLUORIDE_CODES = "InsHistFluorideCodes"  # Fluoride treatments
    FMX_CODES = "InsHistFMXCodes"  # Full mouth X-rays
    SEALANT_CODES = "InsHistSealantCodes"  # Sealants
    CROWN_CODES = "InsHistCrownCodes"  # Crowns
    DENTURE_CODES = "InsHistDentureCodes"  # Dentures
    IMPLANT_CODES = "InsHistImplantCodes"  # Implants
