"""Insurance Plan models for Open Dental SDK."""

from datetime import datetime, date
from typing import Optional, List
from pydantic import Field

from ...base.models import BaseModel


class InsurancePlan(BaseModel):
    """Insurance plan model matching Open Dental API specification."""
    
    # Primary key
    plan_num: int = Field(..., alias="PlanNum", description="Plan number (primary key)")
    
    # Plan identification
    group_name: str = Field("", alias="GroupName", description="Typically the same as the employer. Used to identify difference in plans.")
    group_num: str = Field("", alias="GroupNum", description="The Plan Number in Canada")
    plan_note: str = Field("", alias="PlanNote", description="Note for this plan. Same for all subscribers.")
    
    # Fee schedules
    fee_sched: int = Field(0, alias="FeeSched", description="FK to feesched.FeeSchedNum")
    copay_fee_sched: int = Field(0, alias="CopayFeeSched", description="FK to feesched.FeeSchedNum when FeeSchedType is CoPay")
    manual_fee_sched_num: int = Field(0, alias="ManualFeeSchedNum", description="FK to feesched.FeeSchedNum when feesched.FeeSchedType is ManualBlueBook")
    
    # Plan type - "" (Percentage), "p" (PPO Percentage), "f" (Flat Copay), "c" (Capitation)
    plan_type: str = Field("", alias="PlanType", description="Plan type: '' (Percentage), 'p' (PPO), 'f' (Flat Copay), 'c' (Capitation)")
    
    # Claim settings
    claim_form_num: int = Field(1, alias="ClaimFormNum", description="FK to claimform.ClaimFormNum")
    claims_use_ucr: str = Field("false", alias="ClaimsUseUCR", description="Either 'true' or 'false'")
    
    # Related entities
    employer_num: int = Field(0, alias="EmployerNum", description="FK to employer.EmployerNum")
    carrier_num: int = Field(..., alias="CarrierNum", description="FK to carrier.CarrierNum")
    billing_type: int = Field(0, alias="BillingType", description="FK to definition.DefNum where definition.Category=4")
    
    # Medical and filing
    is_medical: str = Field("false", alias="IsMedical", description="Either 'true' or 'false'")
    filing_code: int = Field(0, alias="FilingCode", description="FK to insfilingcode.InsFilingCodeNum")
    filing_code_subtype: int = Field(0, alias="FilingCodeSubtype", description="FK to insfilingcodesubtype.InsFilingCodeSubtypeNum")
    
    # Display and substitution
    show_base_units: str = Field("false", alias="ShowBaseUnits", description="Either 'true' or 'false'")
    code_subst_none: str = Field("false", alias="CodeSubstNone", description="Set 'true' if plan should ignore any Substitution Codes")
    
    # Status
    is_hidden: str = Field("false", alias="IsHidden", description="Either 'true' or 'false'")
    
    # Renewal
    month_renew: int = Field(0, alias="MonthRenew", description="The month, 1-12, when plan renews. 0 indicates calendar year")
    
    # COB and exclusion rules
    cob_rule: str = Field("Standard", alias="CobRule", description="Either 'Basic', 'Standard', 'CarveOut' or 'SecondaryMedicaid'")
    exclusion_fee_rule: str = Field("PracticeDefault", alias="ExclusionFeeRule", description="Either 'PracticeDefault', 'DoNothing' or 'UseUcrFee'")
    
    # BlueBook
    is_blue_book_enabled: str = Field("false", alias="IsBlueBookEnabled", description="Either 'true' or 'false'")
    
    # Write-off overrides
    ins_plans_zero_write_offs_on_annual_max_override: str = Field("Default", alias="InsPlansZeroWriteOffsOnAnnualMaxOverride", description="Either 'Default', 'Yes' or 'No'")
    ins_plans_zero_write_offs_on_freq_or_aging_override: str = Field("Default", alias="InsPlansZeroWriteOffsOnFreqOrAgingOverride", description="Either 'Default', 'Yes' or 'No'")
    
    # Security and timestamps
    sec_user_num_entry: int = Field(0, alias="SecUserNumEntry", description="FK to userod.UserNum")
    sec_date_entry: Optional[date] = Field(None, alias="SecDateEntry", description="Date the plan was created")
    sec_date_t_edit: Optional[datetime] = Field(None, alias="SecDateTEdit", description="Last edit date and time")



class CreateInsurancePlanRequest(BaseModel):
    """Request model for creating a new insurance plan."""
    
    # Required field
    carrier_num: int = Field(..., alias="CarrierNum", description="FK to carrier.CarrierNum")
    
    # Optional fields
    group_name: Optional[str] = Field(None, alias="GroupName", description="Typically the same as the employer")
    group_num: Optional[str] = Field(None, alias="GroupNum", description="The Plan Number in Canada")
    plan_note: Optional[str] = Field(None, alias="PlanNote", description="Note for this plan")
    fee_sched: Optional[int] = Field(None, alias="FeeSched", description="FK to feesched.FeeSchedNum")
    plan_type: Optional[str] = Field(None, alias="PlanType", description="'' (Percentage), 'p' (PPO), 'f' (Flat Copay), 'c' (Capitation)")
    claim_form_num: Optional[int] = Field(None, alias="ClaimFormNum", description="FK to claimform.ClaimFormNum")
    claims_use_ucr: Optional[str] = Field(None, alias="ClaimsUseUCR", description="Either 'true' or 'false'")
    copay_fee_sched: Optional[int] = Field(None, alias="CopayFeeSched", description="FK to feesched.FeeSchedNum when FeeSchedType is CoPay")
    employer_num: Optional[int] = Field(None, alias="EmployerNum", description="FK to employer.EmployerNum")
    is_medical: Optional[str] = Field(None, alias="IsMedical", description="Either 'true' or 'false'")
    filing_code: Optional[int] = Field(None, alias="FilingCode", description="FK to insfilingcode.InsFilingCodeNum")
    show_base_units: Optional[str] = Field(None, alias="ShowBaseUnits", description="Either 'true' or 'false'")
    code_subst_none: Optional[str] = Field(None, alias="CodeSubstNone", description="Set 'true' to ignore Substitution Codes")
    is_hidden: Optional[str] = Field(None, alias="IsHidden", description="Either 'true' or 'false'")
    month_renew: Optional[int] = Field(None, alias="MonthRenew", description="The month, 1-12, when plan renews. 0 for calendar year")
    filing_code_subtype: Optional[int] = Field(None, alias="FilingCodeSubtype", description="FK to insfilingcodesubtype.InsFilingCodeSubtypeNum")
    cob_rule: Optional[str] = Field(None, alias="CobRule", description="Either 'Basic', 'Standard', 'CarveOut' or 'SecondaryMedicaid'")
    billing_type: Optional[int] = Field(None, alias="BillingType", description="FK to definition.DefNum where definition.Category=4")
    exclusion_fee_rule: Optional[str] = Field(None, alias="ExclusionFeeRule", description="Either 'PracticeDefault', 'DoNothing' or 'UseUcrFee'")
    manual_fee_sched_num: Optional[int] = Field(None, alias="ManualFeeSchedNum", description="FK to feesched.FeeSchedNum when feesched.FeeSchedType is ManualBlueBook")
    is_blue_book_enabled: Optional[str] = Field(None, alias="IsBlueBookEnabled", description="Either 'true' or 'false'")
    ins_plans_zero_write_offs_on_annual_max_override: Optional[str] = Field(None, alias="InsPlansZeroWriteOffsOnAnnualMaxOverride", description="Either 'Default', 'Yes' or 'No'")
    ins_plans_zero_write_offs_on_freq_or_aging_override: Optional[str] = Field(None, alias="InsPlansZeroWriteOffsOnFreqOrAgingOverride", description="Either 'Default', 'Yes' or 'No'")


class UpdateInsurancePlanRequest(BaseModel):
    """Request model for updating an existing insurance plan."""
    
    # All fields are optional for updates
    group_name: Optional[str] = Field(None, alias="GroupName", description="Typically the same as the employer")
    group_num: Optional[str] = Field(None, alias="GroupNum", description="The Plan Number in Canada")
    plan_note: Optional[str] = Field(None, alias="PlanNote", description="Note for this plan")
    fee_sched: Optional[int] = Field(None, alias="FeeSched", description="FK to feesched.FeeSchedNum")
    plan_type: Optional[str] = Field(None, alias="PlanType", description="'' (Percentage), 'p' (PPO), 'f' (Flat Copay), 'c' (Capitation)")
    claim_form_num: Optional[int] = Field(None, alias="ClaimFormNum", description="FK to claimform.ClaimFormNum")
    claims_use_ucr: Optional[str] = Field(None, alias="ClaimsUseUCR", description="Either 'true' or 'false'")
    copay_fee_sched: Optional[int] = Field(None, alias="CopayFeeSched", description="FK to feesched.FeeSchedNum when FeeSchedType is CoPay")
    employer_num: Optional[int] = Field(None, alias="EmployerNum", description="FK to employer.EmployerNum")
    carrier_num: Optional[int] = Field(None, alias="CarrierNum", description="FK to carrier.CarrierNum")
    is_medical: Optional[str] = Field(None, alias="IsMedical", description="Either 'true' or 'false'")
    filing_code: Optional[int] = Field(None, alias="FilingCode", description="FK to insfilingcode.InsFilingCodeNum")
    show_base_units: Optional[str] = Field(None, alias="ShowBaseUnits", description="Either 'true' or 'false'")
    code_subst_none: Optional[str] = Field(None, alias="CodeSubstNone", description="Set 'true' to ignore Substitution Codes")
    is_hidden: Optional[str] = Field(None, alias="IsHidden", description="Either 'true' or 'false'")
    month_renew: Optional[int] = Field(None, alias="MonthRenew", description="The month, 1-12, when plan renews. 0 for calendar year")
    filing_code_subtype: Optional[int] = Field(None, alias="FilingCodeSubtype", description="FK to insfilingcodesubtype.InsFilingCodeSubtypeNum")
    cob_rule: Optional[str] = Field(None, alias="CobRule", description="Either 'Basic', 'Standard', 'CarveOut' or 'SecondaryMedicaid'")
    billing_type: Optional[int] = Field(None, alias="BillingType", description="FK to definition.DefNum where definition.Category=4")
    exclusion_fee_rule: Optional[str] = Field(None, alias="ExclusionFeeRule", description="Either 'PracticeDefault', 'DoNothing' or 'UseUcrFee'")
    manual_fee_sched_num: Optional[int] = Field(None, alias="ManualFeeSchedNum", description="FK to feesched.FeeSchedNum when feesched.FeeSchedType is ManualBlueBook")
    is_blue_book_enabled: Optional[str] = Field(None, alias="IsBlueBookEnabled", description="Either 'true' or 'false'")
    ins_plans_zero_write_offs_on_annual_max_override: Optional[str] = Field(None, alias="InsPlansZeroWriteOffsOnAnnualMaxOverride", description="Either 'Default', 'Yes' or 'No'")
    ins_plans_zero_write_offs_on_freq_or_aging_override: Optional[str] = Field(None, alias="InsPlansZeroWriteOffsOnFreqOrAgingOverride", description="Either 'Default', 'Yes' or 'No'")


class InsurancePlanListResponse(BaseModel):
    """Response model for insurance plan list operations (API returns a list directly)."""
    
    plans: List[InsurancePlan] = Field(default_factory=list, description="List of insurance plans")