"""Preference models for Open Dental SDK."""

from typing import List, Optional
from pydantic import Field

from ...base.models import BaseModel


class Preference(BaseModel):
    """
    Preference model matching Open Dental API specification.
    
    Preferences are system-wide settings that control various aspects
    of Open Dental behavior. Most preferences are read-only via the API.
    
    Reference: https://www.opendental.com/site/apipreferences.html
    """
    
    # Primary key
    pref_num: int = Field(..., alias="PrefNum", description="Preference number (primary key)")
    
    # Preference identification
    pref_name: str = Field(..., alias="PrefName", description="Name of the preference")
    
    # Preference value
    value_string: str = Field(..., alias="ValueString", description="Value of the preference as string")


class PreferenceListResponse(BaseModel):
    """Response model for preference list operations."""
    
    preferences: List[Preference] = Field(default_factory=list, description="List of preferences")
    total: int = Field(0, description="Total number of preferences returned")
    offset: Optional[int] = Field(None, description="Offset used for pagination")

