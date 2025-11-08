"""InsSub models for Open Dental SDK."""

from datetime import datetime, date
from typing import Optional, List
from pydantic import Field

from ...base.models import BaseModel


class InsSub(BaseModel):
    """
    InsSub model matching Open Dental API specification.
    
    Links an InsPlan to a Subscriber (patient.PatNum).
    Works together with PatPlans to indicate coverage.
    """
    
    # Primary key
    ins_sub_num: int = Field(..., alias="InsSubNum", description="InsSub number (primary key)")
    
    # Required relationships
    plan_num: int = Field(..., alias="PlanNum", description="FK to insplan.PlanNum")
    subscriber: int = Field(..., alias="Subscriber", description="FK to patient.PatNum (subscriber)")
    
    # Subscriber identification
    subscriber_id: str = Field(..., alias="SubscriberID", description="Number assigned by insurance company")
    
    # Effective dates
    date_effective: date = Field(..., alias="DateEffective", description="Date this InsPlan became effective")
    date_term: date = Field(..., alias="DateTerm", description="Date this InsPlan was terminated (not usually used)")
    
    # Notes and authorization
    benefit_notes: str = Field("", alias="BenefitNotes", description="Automated notes (e.g., from Trojan). Subscriber-specific.")
    subsc_note: str = Field("", alias="SubscNote", description="Any other info that affects coverage")
    
    # Authorization flags
    release_info: str = Field("true", alias="ReleaseInfo", description="Either 'true' or 'false'. Authorizes release of information")
    assign_ben: str = Field("true", alias="AssignBen", description="Either 'true' or 'false'. Authorizes assignment of benefits")
    
    # Timestamp (auto-updated, cannot be set by developers)
    sec_date_t_edit: datetime = Field(..., alias="SecDateTEdit", description="Last edit date and time (auto-updated)")


class CreateInsSubRequest(BaseModel):
    """Request model for creating a new InsSub."""
    
    # Required fields
    plan_num: int = Field(..., alias="PlanNum", description="FK to insplan.PlanNum")
    subscriber: int = Field(..., alias="Subscriber", description="FK to patient.PatNum (subscriber)")
    subscriber_id: str = Field(..., alias="SubscriberID", description="Number assigned by insurance company")
    
    # Optional fields
    date_effective: Optional[date] = Field(None, alias="DateEffective", description="Date this InsPlan became effective")
    date_term: Optional[date] = Field(None, alias="DateTerm", description="Date this InsPlan was terminated")
    benefit_notes: Optional[str] = Field(None, alias="BenefitNotes", description="Automated notes. Subscriber-specific.")
    release_info: Optional[str] = Field(None, alias="ReleaseInfo", description="Either 'true' or 'false'. Default 'true'")
    assign_ben: Optional[str] = Field(None, alias="AssignBen", description="Either 'true' or 'false'. Default per global preference")
    subsc_note: Optional[str] = Field(None, alias="SubscNote", description="Any other info that affects coverage")


class UpdateInsSubRequest(BaseModel):
    """
    Request model for updating an existing InsSub.
    
    Note: SecDateTEdit is updated automatically and cannot be set by developers.
    """
    
    # All fields are optional for updates
    plan_num: Optional[int] = Field(None, alias="PlanNum", description="FK to insplan.PlanNum")
    subscriber: Optional[int] = Field(None, alias="Subscriber", description="FK to patient.PatNum (subscriber)")
    subscriber_id: Optional[str] = Field(None, alias="SubscriberID", description="Number assigned by insurance company")
    date_effective: Optional[date] = Field(None, alias="DateEffective", description="Date this InsPlan became effective")
    date_term: Optional[date] = Field(None, alias="DateTerm", description="Date this InsPlan was terminated")
    benefit_notes: Optional[str] = Field(None, alias="BenefitNotes", description="Automated notes. Subscriber-specific.")
    release_info: Optional[str] = Field(None, alias="ReleaseInfo", description="Either 'true' or 'false'")
    assign_ben: Optional[str] = Field(None, alias="AssignBen", description="Either 'true' or 'false'")
    subsc_note: Optional[str] = Field(None, alias="SubscNote", description="Any other info that affects coverage")


class InsSubListResponse(BaseModel):
    """Response model for InsSub list operations (API returns a list directly)."""
    
    subs: List[InsSub] = Field(default_factory=list, description="List of InsSubs")

