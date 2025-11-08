"""procedurecodes models for Open Dental SDK."""

from typing import Optional, List, Union
from pydantic import Field

from ...base.models import BaseModel


class ProcedureCode(BaseModel):
    """ProcedureCode model."""
    
    # Primary identifiers
    id: int = Field(..., alias="CodeNum", description="Procedure code number (primary key)")
    
    # Basic information (required for POST)
    proc_code: str = Field(..., alias="ProcCode", description="Procedure code")
    descript: str = Field(..., alias="Descript", description="Procedure description")
    abbr_desc: str = Field(..., alias="AbbrDesc", description="Abbreviated description")
    proc_cat: Union[int, str] = Field(..., alias="ProcCat", description="Procedure category")
    
    # Optional basic information
    proc_time: Optional[str] = Field(None, alias="ProcTime", description="Procedure time pattern")
    layman_term: Optional[str] = Field(None, alias="LaymanTerm", description="Patient-friendly description")
    default_note: Optional[str] = Field(None, alias="DefaultNote", description="Default procedure note")
    default_claim_note: Optional[str] = Field(None, alias="DefaultClaimNote", description="Default claim note")
    default_tp_note: Optional[str] = Field(None, alias="DefaultTPNote", description="Default treatment plan note")
    
    # Coding and references
    alternate_code1: Optional[str] = Field(None, alias="AlternateCode1", description="Medicaid code")
    medical_code: Optional[str] = Field(None, alias="MedicalCode", description="Referenced medical code")
    substitution_code: Optional[str] = Field(None, alias="SubstitutionCode", description="Substitution procedure code")
    subst_only_if: Optional[str] = Field(None, alias="SubstOnlyIf", description="Substitution conditions")
    
    # Classification flags
    is_hygiene: Optional[bool] = Field(None, alias="IsHygiene", description="Hygiene procedure flag")
    is_prosth: Optional[bool] = Field(None, alias="IsProsth", description="Prosthetic procedure flag")
    is_canadian_lab: Optional[bool] = Field(None, alias="IsCanadianLab", description="Lab fee tracking flag")
    is_radiology: Optional[bool] = Field(None, alias="IsRadiology", description="Radiology procedure flag")
    no_bill_ins: Optional[bool] = Field(None, alias="NoBillIns", description="Billing exclusion flag")
    is_taxed: Optional[bool] = Field(None, alias="IsTaxed", description="Sales tax application flag")
    
    # Treatment area and visualization
    treat_area: Optional[str] = Field(None, alias="TreatArea", description="Treatment area type")
    paint_type: Optional[str] = Field(None, alias="PaintType", description="Visualization type")
    paint_text: Optional[str] = Field(None, alias="PaintText", description="Tooth annotation text")
    
    # Billing and units
    base_units: Optional[float] = Field(None, alias="BaseUnits", description="Procedure base units")
    canada_time_units: Optional[float] = Field(None, alias="CanadaTimeUnits", description="Insurance scaling units")
    
    # Additional codes
    drug_ndc: Optional[str] = Field(None, alias="DrugNDC", description="National Drug Code")
    revenue_code_default: Optional[str] = Field(None, alias="RevenueCodeDefault", description="Institutional claim code")
    diagnostic_codes: Optional[str] = Field(None, alias="DiagnosticCodes", description="ICD-10 codes")
    
    # Provider information
    prov_num_default: Optional[int] = Field(None, alias="ProvNumDefault", description="Default provider ID")


class CreateProcedureCodeRequest(BaseModel):
    """Request model for creating a new procedure code."""
    
    # Required fields for POST
    proc_code: str = Field(..., alias="ProcCode", description="Procedure code")
    descript: str = Field(..., alias="Descript", description="Procedure description")
    abbr_desc: str = Field(..., alias="AbbrDesc", description="Abbreviated description")
    proc_cat: Union[int, str] = Field(..., alias="ProcCat", description="Procedure category")
    
    # Optional fields
    proc_time: Optional[str] = Field(None, alias="ProcTime", description="Procedure time pattern")
    layman_term: Optional[str] = Field(None, alias="LaymanTerm", description="Patient-friendly description")
    default_note: Optional[str] = Field(None, alias="DefaultNote", description="Default procedure note")
    default_claim_note: Optional[str] = Field(None, alias="DefaultClaimNote", description="Default claim note")
    default_tp_note: Optional[str] = Field(None, alias="DefaultTPNote", description="Default treatment plan note")
    
    # Coding and references
    alternate_code1: Optional[str] = Field(None, alias="AlternateCode1", description="Medicaid code")
    medical_code: Optional[str] = Field(None, alias="MedicalCode", description="Referenced medical code")
    substitution_code: Optional[str] = Field(None, alias="SubstitutionCode", description="Substitution procedure code")
    subst_only_if: Optional[str] = Field(None, alias="SubstOnlyIf", description="Substitution conditions")
    
    # Classification flags
    is_hygiene: Optional[bool] = Field(None, alias="IsHygiene", description="Hygiene procedure flag")
    is_prosth: Optional[bool] = Field(None, alias="IsProsth", description="Prosthetic procedure flag")
    is_canadian_lab: Optional[bool] = Field(None, alias="IsCanadianLab", description="Lab fee tracking flag")
    is_radiology: Optional[bool] = Field(None, alias="IsRadiology", description="Radiology procedure flag")
    no_bill_ins: Optional[bool] = Field(None, alias="NoBillIns", description="Billing exclusion flag")
    is_taxed: Optional[bool] = Field(None, alias="IsTaxed", description="Sales tax application flag")
    
    # Treatment area and visualization
    treat_area: Optional[str] = Field(None, alias="TreatArea", description="Treatment area type")
    paint_type: Optional[str] = Field(None, alias="PaintType", description="Visualization type")
    paint_text: Optional[str] = Field(None, alias="PaintText", description="Tooth annotation text")
    
    # Billing and units
    base_units: Optional[float] = Field(None, alias="BaseUnits", description="Procedure base units")
    canada_time_units: Optional[float] = Field(None, alias="CanadaTimeUnits", description="Insurance scaling units")
    
    # Additional codes
    drug_ndc: Optional[str] = Field(None, alias="DrugNDC", description="National Drug Code")
    revenue_code_default: Optional[str] = Field(None, alias="RevenueCodeDefault", description="Institutional claim code")
    diagnostic_codes: Optional[str] = Field(None, alias="DiagnosticCodes", description="ICD-10 codes")
    
    # Provider information
    prov_num_default: Optional[int] = Field(None, alias="ProvNumDefault", description="Default provider ID")


class UpdateProcedureCodeRequest(BaseModel):
    """Request model for updating an existing procedure code."""
    
    # All fields are optional for updates
    proc_code: Optional[str] = Field(None, alias="ProcCode", description="Procedure code")
    descript: Optional[str] = Field(None, alias="Descript", description="Procedure description")
    abbr_desc: Optional[str] = Field(None, alias="AbbrDesc", description="Abbreviated description")
    proc_cat: Optional[Union[int, str]] = Field(None, alias="ProcCat", description="Procedure category")
    
    # Optional fields
    proc_time: Optional[str] = Field(None, alias="ProcTime", description="Procedure time pattern")
    layman_term: Optional[str] = Field(None, alias="LaymanTerm", description="Patient-friendly description")
    default_note: Optional[str] = Field(None, alias="DefaultNote", description="Default procedure note")
    default_claim_note: Optional[str] = Field(None, alias="DefaultClaimNote", description="Default claim note")
    default_tp_note: Optional[str] = Field(None, alias="DefaultTPNote", description="Default treatment plan note")
    
    # Coding and references
    alternate_code1: Optional[str] = Field(None, alias="AlternateCode1", description="Medicaid code")
    medical_code: Optional[str] = Field(None, alias="MedicalCode", description="Referenced medical code")
    substitution_code: Optional[str] = Field(None, alias="SubstitutionCode", description="Substitution procedure code")
    subst_only_if: Optional[str] = Field(None, alias="SubstOnlyIf", description="Substitution conditions")
    
    # Classification flags
    is_hygiene: Optional[bool] = Field(None, alias="IsHygiene", description="Hygiene procedure flag")
    is_prosth: Optional[bool] = Field(None, alias="IsProsth", description="Prosthetic procedure flag")
    is_canadian_lab: Optional[bool] = Field(None, alias="IsCanadianLab", description="Lab fee tracking flag")
    is_radiology: Optional[bool] = Field(None, alias="IsRadiology", description="Radiology procedure flag")
    no_bill_ins: Optional[bool] = Field(None, alias="NoBillIns", description="Billing exclusion flag")
    is_taxed: Optional[bool] = Field(None, alias="IsTaxed", description="Sales tax application flag")
    
    # Treatment area and visualization
    treat_area: Optional[str] = Field(None, alias="TreatArea", description="Treatment area type")
    paint_type: Optional[str] = Field(None, alias="PaintType", description="Visualization type")
    paint_text: Optional[str] = Field(None, alias="PaintText", description="Tooth annotation text")
    
    # Billing and units
    base_units: Optional[float] = Field(None, alias="BaseUnits", description="Procedure base units")
    canada_time_units: Optional[float] = Field(None, alias="CanadaTimeUnits", description="Insurance scaling units")
    
    # Additional codes
    drug_ndc: Optional[str] = Field(None, alias="DrugNDC", description="National Drug Code")
    revenue_code_default: Optional[str] = Field(None, alias="RevenueCodeDefault", description="Institutional claim code")
    diagnostic_codes: Optional[str] = Field(None, alias="DiagnosticCodes", description="ICD-10 codes")
    
    # Provider information
    prov_num_default: Optional[int] = Field(None, alias="ProvNumDefault", description="Default provider ID")


class ProcedureCodeListResponse(BaseModel):
    """Response model for procedure code list operations."""
    
    procedure_codes: List[ProcedureCode]
    total: int
    page: Optional[int] = None
    per_page: Optional[int] = None


class ProcedureCodeSearchRequest(BaseModel):
    """Request model for searching procedure codes."""
    
    proc_code: Optional[str] = Field(None, alias="ProcCode", description="Procedure code to search for")
    descript: Optional[str] = Field(None, alias="Descript", description="Procedure description to search for")
    abbr_desc: Optional[str] = Field(None, alias="AbbrDesc", description="Abbreviated description to search for")
    proc_cat: Optional[Union[int, str]] = Field(None, alias="ProcCat", description="Procedure category to filter by")
    is_hygiene: Optional[bool] = Field(None, alias="IsHygiene", description="Whether to filter by hygiene procedures")
    is_prosth: Optional[bool] = Field(None, alias="IsProsth", description="Whether to filter by prosthetic procedures")
    is_canadian_lab: Optional[bool] = Field(None, alias="IsCanadianLab", description="Whether to filter by lab fee tracking")
    is_radiology: Optional[bool] = Field(None, alias="IsRadiology", description="Whether to filter by radiology procedures")
    no_bill_ins: Optional[bool] = Field(None, alias="NoBillIns", description="Whether to filter by billing exclusion")
    is_taxed: Optional[bool] = Field(None, alias="IsTaxed", description="Whether to filter by sales tax application")
    treat_area: Optional[str] = Field(None, alias="TreatArea", description="Treatment area to filter by")
    paint_type: Optional[str] = Field(None, alias="PaintType", description="Paint type to filter by")
    
    # Pagination
    page: Optional[int] = Field(1, description="Page number for pagination")
    per_page: Optional[int] = Field(50, description="Number of items per page")
