"""ProcedureLog models for Open Dental SDK."""

from datetime import datetime, date
from typing import Optional, List, Union
from pydantic import Field

from ...base.models import BaseModel


class ProcedureLog(BaseModel):
    """
    ProcedureLog model matching Open Dental API specification.
    
    ProcedureLogs represent actual procedures performed or planned for patients.
    Note: These are complex - see the Procedure documentation for more details.
    
    Reference: https://www.opendental.com/site/apiprocedurelogs.html
    """
    
    # Primary key
    proc_num: int = Field(..., alias="ProcNum", description="Procedure number (primary key)")
    
    # Patient and appointment references
    pat_num: int = Field(..., alias="PatNum", description="FK to patient.PatNum")
    apt_num: int = Field(..., alias="AptNum", description="FK to appointment.AptNum")
    
    # Procedure dates
    proc_date: date = Field(..., alias="ProcDate", description="Procedure date")
    date_entry_c: Optional[date] = Field(None, alias="DateEntryC", description="Date the procedure was entered")
    date_tp: Optional[date] = Field(None, alias="DateTP", description="Date the procedure was treatment planned")
    sec_date_entry: Optional[datetime] = Field(None, alias="SecDateEntry", description="Secure date of entry")
    date_t_stamp: datetime = Field(..., alias="DateTStamp", description="Timestamp of last modification")
    
    # Financial
    proc_fee: str = Field(..., alias="ProcFee", description="Procedure fee")
    discount: Optional[float] = Field(None, alias="Discount", description="Discount amount")
    
    # Tooth information
    surf: str = Field(..., alias="Surf", description="Surface (e.g., MODL)")
    tooth_num: str = Field(..., alias="ToothNum", description="Tooth number")
    tooth_range: str = Field(..., alias="ToothRange", description="Tooth range")
    
    # Status and priority
    priority: int = Field(..., alias="Priority", description="Priority FK to definition.DefNum")
    priority_name: str = Field("", alias="priority", description="Priority name")
    proc_status: str = Field(..., alias="ProcStatus", description="Procedure status")
    
    # Provider and diagnosis
    prov_num: int = Field(..., alias="ProvNum", description="FK to provider.ProvNum")
    prov_abbr: str = Field("", alias="provAbbr", description="Provider abbreviation")
    dx: int = Field(..., alias="Dx", description="FK to definition.DefNum for diagnosis")
    dx_name: str = Field("", alias="dxName", description="Diagnosis name")
    
    # Appointment planning
    planned_apt_num: int = Field(..., alias="PlannedAptNum", description="FK to planned appointment")
    
    # Service location and prosthesis
    place_service: Optional[str] = Field(None, alias="PlaceService", description="Place of service")
    prosthesis: str = Field(..., alias="Prosthesis", description="Prosthesis code")
    date_original_prosth: date = Field(..., alias="DateOriginalProsth", description="Original prosthesis date")
    is_date_prosth_est: str = Field(..., alias="IsDateProsthEst", description="Either 'true' or 'false'")
    
    # Notes
    claim_note: Optional[str] = Field(None, alias="ClaimNote", description="Claim note")
    billing_note: Optional[str] = Field(None, alias="BillingNote", description="Billing note")
    
    # Clinic
    clinic_num: int = Field(..., alias="ClinicNum", description="FK to clinic.ClinicNum")
    
    # Procedure code information
    code_num: int = Field(..., alias="CodeNum", description="FK to procedurecode.CodeNum")
    proc_code: str = Field(..., alias="procCode", description="Procedure code (e.g., D0120)")
    descript: str = Field(..., alias="descript", description="Procedure description")
    
    # Units
    unit_qty: int = Field(..., alias="UnitQty", description="Unit quantity")
    base_units: float = Field(..., alias="BaseUnits", description="Base units")
    
    # Site
    site_num: Optional[int] = Field(None, alias="SiteNum", description="FK to site.SiteNum")
    
    # Graphics and Canadian
    hide_graphics: Optional[str] = Field(None, alias="HideGraphics", description="Either 'true' or 'false'")
    canadian_type_codes: Optional[str] = Field(None, alias="CanadianTypeCodes", description="Canadian type codes")
    
    # Timing
    proc_time: Optional[str] = Field(None, alias="ProcTime", description="Procedure start time (HH:mm:ss)")
    proc_time_end: Optional[str] = Field(None, alias="ProcTimeEnd", description="Procedure end time (HH:mm:ss)")
    
    # Prognosis and lock
    prognosis: Optional[int] = Field(None, alias="Prognosis", description="FK to definition.DefNum")
    is_locked: Optional[str] = Field(None, alias="IsLocked", description="Either 'true' or 'false'")
    
    # Server datetime
    server_date_time: Optional[str] = Field(None, alias="serverDateTime", description="Server date and time")


class CreateProcedureLogRequest(BaseModel):
    """Request model for creating a new procedure log."""
    
    # Required fields
    pat_num: int = Field(..., alias="PatNum", description="FK to patient.PatNum")
    proc_date: Union[date, str] = Field(..., alias="ProcDate", description="Procedure date (yyyy-MM-dd)")
    prov_num: int = Field(..., alias="ProvNum", description="FK to provider.ProvNum")
    
    # Either CodeNum or procCode is required (mutually exclusive)
    code_num: Optional[int] = Field(None, alias="CodeNum", description="FK to procedurecode.CodeNum")
    proc_code: Optional[str] = Field(None, alias="procCode", description="Procedure code")
    
    # Optional fields
    apt_num: Optional[int] = Field(None, alias="AptNum", description="FK to appointment.AptNum")
    proc_fee: Optional[Union[str, float]] = Field(None, alias="ProcFee", description="Procedure fee")
    surf: Optional[str] = Field(None, alias="Surf", description="Surface")
    tooth_num: Optional[str] = Field(None, alias="ToothNum", description="Tooth number")
    tooth_range: Optional[str] = Field(None, alias="ToothRange", description="Tooth range")
    priority: Optional[int] = Field(None, alias="Priority", description="FK to definition.DefNum")
    proc_status: Optional[str] = Field(None, alias="ProcStatus", description="Procedure status")
    dx: Optional[int] = Field(None, alias="Dx", description="FK to definition.DefNum for diagnosis")
    planned_apt_num: Optional[int] = Field(None, alias="PlannedAptNum", description="FK to planned appointment")
    place_service: Optional[str] = Field(None, alias="PlaceService", description="Place of service")
    prosthesis: Optional[str] = Field(None, alias="Prosthesis", description="Prosthesis code")
    date_original_prosth: Optional[Union[date, str]] = Field(None, alias="DateOriginalProsth", description="Original prosthesis date")
    claim_note: Optional[str] = Field(None, alias="ClaimNote", description="Claim note")
    clinic_num: Optional[int] = Field(None, alias="ClinicNum", description="FK to clinic.ClinicNum")
    unit_qty: Optional[int] = Field(None, alias="UnitQty", description="Unit quantity")
    base_units: Optional[float] = Field(None, alias="BaseUnits", description="Base units")
    date_tp: Optional[Union[date, str]] = Field(None, alias="DateTP", description="Treatment plan date")
    site_num: Optional[int] = Field(None, alias="SiteNum", description="FK to site.SiteNum")
    proc_time: Optional[str] = Field(None, alias="ProcTime", description="Start time (HH:mm:ss)")
    proc_time_end: Optional[str] = Field(None, alias="ProcTimeEnd", description="End time (HH:mm:ss)")
    prognosis: Optional[int] = Field(None, alias="Prognosis", description="FK to definition.DefNum")
    billing_note: Optional[str] = Field(None, alias="BillingNote", description="Billing note")
    discount: Optional[float] = Field(None, alias="Discount", description="Discount amount")
    is_date_prosth_est: Optional[str] = Field(None, alias="IsDateProsthEst", description="Either 'true' or 'false'")


class UpdateProcedureLogRequest(BaseModel):
    """Request model for updating an existing procedure log."""
    
    # All fields are optional for updates
    apt_num: Optional[int] = Field(None, alias="AptNum", description="FK to appointment.AptNum")
    proc_date: Optional[Union[date, str]] = Field(None, alias="ProcDate", description="Procedure date (yyyy-MM-dd)")
    proc_fee: Optional[Union[str, float]] = Field(None, alias="ProcFee", description="Procedure fee")
    surf: Optional[str] = Field(None, alias="Surf", description="Surface")
    tooth_num: Optional[str] = Field(None, alias="ToothNum", description="Tooth number")
    tooth_range: Optional[str] = Field(None, alias="ToothRange", description="Tooth range")
    priority: Optional[int] = Field(None, alias="Priority", description="FK to definition.DefNum")
    proc_status: Optional[str] = Field(None, alias="ProcStatus", description="Procedure status")
    prov_num: Optional[int] = Field(None, alias="ProvNum", description="FK to provider.ProvNum")
    dx: Optional[int] = Field(None, alias="Dx", description="FK to definition.DefNum for diagnosis")
    planned_apt_num: Optional[int] = Field(None, alias="PlannedAptNum", description="FK to planned appointment")
    place_service: Optional[str] = Field(None, alias="PlaceService", description="Place of service")
    prosthesis: Optional[str] = Field(None, alias="Prosthesis", description="Prosthesis code")
    date_original_prosth: Optional[Union[date, str]] = Field(None, alias="DateOriginalProsth", description="Original prosthesis date")
    claim_note: Optional[str] = Field(None, alias="ClaimNote", description="Claim note")
    clinic_num: Optional[int] = Field(None, alias="ClinicNum", description="FK to clinic.ClinicNum")
    code_num: Optional[int] = Field(None, alias="CodeNum", description="FK to procedurecode.CodeNum")
    proc_code: Optional[str] = Field(None, alias="procCode", description="Procedure code")
    unit_qty: Optional[int] = Field(None, alias="UnitQty", description="Unit quantity")
    base_units: Optional[float] = Field(None, alias="BaseUnits", description="Base units")
    date_tp: Optional[Union[date, str]] = Field(None, alias="DateTP", description="Treatment plan date")
    site_num: Optional[int] = Field(None, alias="SiteNum", description="FK to site.SiteNum")
    proc_time: Optional[str] = Field(None, alias="ProcTime", description="Start time (HH:mm:ss)")
    proc_time_end: Optional[str] = Field(None, alias="ProcTimeEnd", description="End time (HH:mm:ss)")
    prognosis: Optional[int] = Field(None, alias="Prognosis", description="FK to definition.DefNum")
    billing_note: Optional[str] = Field(None, alias="BillingNote", description="Billing note")
    discount: Optional[float] = Field(None, alias="Discount", description="Discount amount")
    is_date_prosth_est: Optional[str] = Field(None, alias="IsDateProsthEst", description="Either 'true' or 'false'")


class ProcedureLogListResponse(BaseModel):
    """Response model for procedure log list operations."""
    
    procedure_logs: List[ProcedureLog] = Field(default_factory=list, description="List of procedure logs")
    total: int = Field(0, description="Total number of procedure logs")
    offset: Optional[int] = Field(None, description="Offset used for pagination")


class InsuranceHistoryItem(BaseModel):
    """Insurance history item for a patient's insurance plan."""
    
    ins_hist_pref_name: str = Field(..., alias="insHistPrefName", description="Preference name storing procedure codes")
    proc_date: str = Field(..., alias="procDate", description="Previous treatment date or 'No History' or 'Not Set'")
    proc_num: int = Field(..., alias="ProcNum", description="FK to most recent procedure (0 if no history)")


class InsuranceHistoryResponse(BaseModel):
    """Response model for insurance history."""
    
    history: List[InsuranceHistoryItem] = Field(default_factory=list, description="Insurance history items")


class GroupNote(BaseModel):
    """Group Note model for procedure group notes."""
    
    proc_num: int = Field(..., alias="ProcNum", description="FK to procedurelog (must be ~GRP~ code)")
    proc_nums: List[int] = Field(..., alias="ProcNums", description="Array of FKs to procedures in the group")
    pat_num: int = Field(..., alias="PatNum", description="FK to patient.PatNum")
    note: str = Field(..., alias="Note", description="Group note text")
    is_signed: str = Field(..., alias="isSigned", description="Either 'true' or 'false'")


class UpdateGroupNoteRequest(BaseModel):
    """Request model for updating a group note."""
    
    pat_num: int = Field(..., alias="PatNum", description="FK to patient.PatNum")
    note: str = Field(..., alias="Note", description="Group note text")
    do_append_note: Optional[str] = Field(None, alias="doAppendNote", description="Either 'true' or 'false'")
    is_signed: Optional[str] = Field(None, alias="isSigned", description="Either 'true' or 'false'")


class CreateInsuranceHistoryRequest(BaseModel):
    """
    Request model for creating insurance history entry.
    
    This creates a new Existing Other Provider (EO) procedure and Insurance History
    (InsHist) claimproc for a given patient.
    """
    
    pat_num: int = Field(..., alias="PatNum", description="FK to patient.PatNum")
    ins_sub_num: int = Field(..., alias="InsSubNum", description="FK to inssub.InsSubNum")
    ins_hist_pref_name: str = Field(..., alias="insHistPrefName", description="Insurance history category name (case sensitive)")
    proc_date: Union[date, str] = Field(..., alias="ProcDate", description="Procedure date (yyyy-MM-dd)")
