"""PatPlan models for Open Dental SDK."""

from datetime import datetime, date
from typing import Optional, List
from pydantic import Field

from ...base.models import BaseModel


class PatPlan(BaseModel):
    """
    PatPlan model matching Open Dental API specification.
    
    A PatPlan row indicates coverage/eligibility. If there is no PatPlan row,
    the patient does not have coverage.
    """
    
    # Primary key
    pat_plan_num: int = Field(..., alias="PatPlanNum", description="PatPlan number (primary key)")
    
    # Required relationships
    pat_num: int = Field(..., alias="PatNum", description="FK to patient.PatNum")
    ins_sub_num: int = Field(..., alias="InsSubNum", description="FK to inssub.InsSubNum")
    
    # Ordinal (primary, secondary, etc.)
    ordinal: int = Field(1, alias="Ordinal", description="Single digit: 1 (primary), 2 (secondary), etc.")
    
    # Status
    is_pending: str = Field("false", alias="IsPending", description="Either 'true' or 'false'")
    
    # Relationship to subscriber
    relationship: str = Field("Self", alias="Relationship", description="Self, Spouse, Child, Employee, HandicapDep, SignifOther, InjuredPlantiff, LifePartner, or Dependent")
    
    # Patient ID override
    pat_id: str = Field("", alias="PatID", description="Patient ID which overrides subscriber ID on eclaims. Also used for Canada")
    
    # Orthodontic fields
    ortho_auto_fee_billed_override: float = Field(-1.0, alias="OrthoAutoFeeBilledOverride", description="Ortho auto fee billed override")
    ortho_auto_next_claim_date: date = Field(..., alias="OrthoAutoNextClaimDate", description="Ortho auto next claim date")
    
    # Timestamps
    sec_date_t_entry: datetime = Field(..., alias="SecDateTEntry", description="Date and time the record was created")
    sec_date_t_edit: datetime = Field(..., alias="SecDateTEdit", description="Date and time the record was last edited")


class CreatePatPlanRequest(BaseModel):
    """Request model for creating a new PatPlan."""
    
    # Required fields
    pat_num: int = Field(..., alias="PatNum", description="FK to patient.PatNum")
    ins_sub_num: int = Field(..., alias="InsSubNum", description="FK to inssub.InsSubNum (must exist)")
    
    # Optional fields
    ordinal: Optional[int] = Field(None, alias="Ordinal", description="1 (primary), 2 (secondary), etc. Default 1")
    relationship: Optional[str] = Field(None, alias="Relationship", description="Self, Spouse, Child, Employee, HandicapDep, SignifOther, InjuredPlantiff, LifePartner, or Dependent. Default Self")
    pat_id: Optional[str] = Field(None, alias="PatID", description="Patient ID override for eclaims. Also used for Canada")


class UpdatePatPlanRequest(BaseModel):
    """Request model for updating an existing PatPlan."""
    
    # All fields are optional for updates
    # Note: PatNum cannot be updated. Drop and recreate instead.
    ins_sub_num: Optional[int] = Field(None, alias="InsSubNum", description="FK to inssub.InsSubNum (corresponds to Change button in UI)")
    ordinal: Optional[int] = Field(None, alias="Ordinal", description="1 (primary), 2 (secondary), etc.")
    relationship: Optional[str] = Field(None, alias="Relationship", description="Self, Spouse, Child, Employee, HandicapDep, SignifOther, InjuredPlantiff, LifePartner, or Dependent")
    pat_id: Optional[str] = Field(None, alias="PatID", description="Patient ID override for eclaims. Also used for Canada")


class PatPlanListResponse(BaseModel):
    """Response model for PatPlan list operations (API returns a list directly)."""
    
    plans: List[PatPlan] = Field(default_factory=list, description="List of PatPlans")

