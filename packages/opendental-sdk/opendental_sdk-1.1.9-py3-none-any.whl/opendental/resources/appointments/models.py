"""Appointment models for Open Dental SDK."""

from datetime import datetime, date
from typing import Optional, Union
from pydantic import Field

from ...base.models import BaseModel


class Appointment(BaseModel):
    """Appointment model matching Open Dental API specification."""
    
    server_date_time: Optional[datetime] = Field(None, alias="serverDateTime", description="Server date and time")
    apt_num: int = Field(..., alias="AptNum", description="Primary key")
    pat_num: int = Field(..., alias="PatNum", description="FK to patient.PatNum")
    apt_status: str = Field(..., alias="AptStatus", description="Either 'Scheduled', 'Complete', 'UnschedList', 'ASAP', 'Broken', 'Planned', 'PtNote', or 'PtNoteCompleted'")
    pattern: str = Field("", alias="Pattern", description="Time pattern in 5 minute increments. String of 'X' and '/' characters")
    confirmed: int = Field(0, alias="Confirmed", description="FK to definition.DefNum where definition.Category=2")
    confirmed_str: str = Field("", alias="confirmed", description="Confirmed status string")
    time_locked: str = Field("false", alias="TimeLocked", description="Either 'true' or 'false'")
    op: int = Field(0, alias="Op", description="FK to operatory.OperatoryNum")
    note: str = Field("", alias="Note", description="Appointment note")
    prov_num: int = Field(0, alias="ProvNum", description="FK to provider.ProvNum")
    prov_abbr: str = Field("", alias="provAbbr", description="Provider abbreviation")
    prov_hyg: int = Field(0, alias="ProvHyg", description="FK to provider.ProvNum for hygienist")
    apt_date_time: datetime = Field(..., alias="AptDateTime", description="Appointment date and time")
    next_apt_num: int = Field(0, alias="NextAptNum", description="FK to appointment.AptNum")
    unsched_status: int = Field(0, alias="UnschedStatus", description="FK to definition.DefNum where definition.Category=13")
    unsched_status_str: str = Field("", alias="unschedStatus", description="Unscheduled status string")
    is_new_patient: str = Field("false", alias="IsNewPatient", description="Either 'true' or 'false'")
    proc_descript: str = Field("", alias="ProcDescript", description="Procedure descriptions")
    clinic_num: int = Field(0, alias="ClinicNum", description="FK to clinic.ClinicNum")
    is_hygiene: str = Field("false", alias="IsHygiene", description="Either 'true' or 'false'")
    date_t_stamp: datetime = Field(..., alias="DateTStamp", description="Date and time stamp")
    date_time_arrived: datetime = Field(datetime(1, 1, 1), alias="DateTimeArrived", description="Time patient arrived")
    date_time_seated: datetime = Field(datetime(1, 1, 1), alias="DateTimeSeated", description="Time patient was seated")
    date_time_dismissed: datetime = Field(datetime(1, 1, 1), alias="DateTimeDismissed", description="Time patient was dismissed")
    ins_plan_1: int = Field(0, alias="InsPlan1", description="FK to insplan.PlanNum")
    ins_plan_2: int = Field(0, alias="InsPlan2", description="FK to insplan.PlanNum")
    date_time_asked_to_arrive: datetime = Field(datetime(1, 1, 1), alias="DateTimeAskedToArrive", description="Time patient was asked to arrive")
    color_override: str = Field("0,0,0", alias="colorOverride", description="Comma delimited RGB color values")
    appointment_type_num: int = Field(0, alias="AppointmentTypeNum", description="FK to appointmenttype.AppointmentTypeNum")
    sec_user_num_entry: int = Field(0, alias="SecUserNumEntry", description="FK to userod.UserNum")
    sec_date_t_entry: datetime = Field(datetime(1, 1, 1), alias="SecDateTEntry", description="Date and time of entry")
    priority: str = Field("Normal", alias="Priority", description="Either 'Normal' or 'ASAP'")
    pattern_secondary: str = Field("", alias="PatternSecondary", description="Secondary time pattern")
    item_order_planned: int = Field(0, alias="ItemOrderPlanned", description="Item order for planned appointments")


class CreateAppointmentRequest(BaseModel):
    """Request model for creating a new appointment."""
    
    pat_num: int = Field(..., alias="PatNum", description="FK to patient.PatNum")
    apt_date_time: datetime = Field(..., alias="AptDateTime", description="Appointment date and time (yyyy-MM-dd HH:mm:ss)")
    op: int = Field(..., alias="Op", description="FK to operatory.OperatoryNum")
    prov_num: int = Field(..., alias="ProvNum", description="FK to provider.ProvNum")
    pattern: str = Field(..., alias="Pattern", description="Time pattern in 5 minute increments")
    apt_status: Optional[str] = Field(None, alias="AptStatus", description="Either 'Scheduled', 'Complete', 'UnschedList', 'ASAP', 'Broken', 'Planned', 'PtNote', or 'PtNoteCompleted'")
    confirmed: Optional[int] = Field(None, alias="Confirmed", description="FK to definition.DefNum where definition.Category=2")
    time_locked: Optional[str] = Field(None, alias="TimeLocked", description="Either 'true' or 'false'")
    note: Optional[str] = Field(None, alias="Note", description="Appointment note")
    prov_hyg: Optional[int] = Field(None, alias="ProvHyg", description="FK to provider.ProvNum for hygienist")
    is_new_patient: Optional[str] = Field(None, alias="IsNewPatient", description="Either 'true' or 'false'")
    clinic_num: Optional[int] = Field(None, alias="ClinicNum", description="FK to clinic.ClinicNum")
    is_hygiene: Optional[str] = Field(None, alias="IsHygiene", description="Either 'true' or 'false'")
    priority: Optional[str] = Field(None, alias="Priority", description="Either 'Normal' or 'ASAP'")
    appointment_type_num: Optional[int] = Field(None, alias="AppointmentTypeNum", description="FK to appointmenttype.AppointmentTypeNum")
    color_override: Optional[str] = Field(None, alias="colorOverride", description="Comma delimited RGB color values")
    pattern_secondary: Optional[str] = Field(None, alias="PatternSecondary", description="Secondary time pattern")


class UpdateAppointmentRequest(BaseModel):
    """Request model for updating an appointment."""
    
    apt_status: Optional[str] = Field(None, alias="AptStatus", description="Either 'Scheduled', 'Complete', 'UnschedList', 'Broken', 'Planned', 'PtNote', or 'PtNoteCompleted'")
    pattern: Optional[str] = Field(None, alias="Pattern", description="Time pattern in 5 minute increments")
    confirmed: Optional[int] = Field(None, alias="Confirmed", description="FK to definition.DefNum where definition.Category=2")
    op: Optional[int] = Field(None, alias="Op", description="FK to operatory.OperatoryNum")
    note: Optional[str] = Field(None, alias="Note", description="Overwrites existing note")
    prov_num: Optional[int] = Field(None, alias="ProvNum", description="FK to provider.ProvNum")
    prov_hyg: Optional[int] = Field(None, alias="ProvHyg", description="FK to provider.ProvNum for hygienist")
    apt_date_time: Optional[Union[datetime, str]] = Field(None, alias="AptDateTime", description="Appointment date and time (yyyy-MM-dd HH:mm:ss)")
    clinic_num: Optional[int] = Field(None, alias="ClinicNum", description="FK to clinic.ClinicNum")
    is_hygiene: Optional[str] = Field(None, alias="IsHygiene", description="Either 'true' or 'false'")
    date_time_arrived: Optional[str] = Field(None, alias="DateTimeArrived", description="Time patient checked in (HH:mm:ss)")
    date_time_seated: Optional[str] = Field(None, alias="DateTimeSeated", description="Time patient was seated (HH:mm:ss)")
    date_time_dismissed: Optional[str] = Field(None, alias="DateTimeDismissed", description="Time patient got up (HH:mm:ss)")
    is_new_patient: Optional[str] = Field(None, alias="IsNewPatient", description="Either 'true' or 'false'")
    priority: Optional[str] = Field(None, alias="Priority", description="Either 'Normal' or 'ASAP'")
    appointment_type_num: Optional[int] = Field(None, alias="AppointmentTypeNum", description="FK to appointmenttype.AppointmentTypeNum")
    unsched_status: Optional[int] = Field(None, alias="UnschedStatus", description="FK to definition.DefNum where definition.Category=13")
    color_override: Optional[str] = Field(None, alias="colorOverride", description="Comma delimited RGB color values")
    pattern_secondary: Optional[str] = Field(None, alias="PatternSecondary", description="Secondary time pattern")


class AppendNoteRequest(BaseModel):
    """Request model for appending a note to an appointment."""
    
    note: str = Field(..., alias="Note", description="Note text to append")


class ConfirmAppointmentRequest(BaseModel):
    """Request model for confirming an appointment."""
    
    # Either confirmVal or defNum, not both
    confirm_val: Optional[str] = Field(None, alias="confirmVal", description="Either 'None', 'Sent', 'Confirmed', 'Not Accepted', or 'Failed'")
    def_num: Optional[int] = Field(None, alias="defNum", description="FK to definition.DefNum where definition.Category=2")


class BreakAppointmentRequest(BaseModel):
    """Request model for breaking an appointment."""
    
    send_to_unscheduled_list: str = Field(..., alias="sendToUnscheduledList", description="Either 'true' or 'false'")
    break_type: Optional[str] = Field(None, alias="breakType", description="Either 'Missed' or 'Cancelled'")


class CreatePlannedAppointmentRequest(BaseModel):
    """Request model for creating a planned appointment."""
    
    pat_num: int = Field(..., alias="PatNum", description="FK to patient.PatNum")
    pattern: str = Field(..., alias="Pattern", description="Time pattern in 5 minute increments")
    prov_num: int = Field(..., alias="ProvNum", description="FK to provider.ProvNum")
    op: Optional[int] = Field(None, alias="Op", description="FK to operatory.OperatoryNum")
    note: Optional[str] = Field(None, alias="Note", description="Appointment note")
    prov_hyg: Optional[int] = Field(None, alias="ProvHyg", description="FK to provider.ProvNum for hygienist")
    clinic_num: Optional[int] = Field(None, alias="ClinicNum", description="FK to clinic.ClinicNum")
    is_hygiene: Optional[str] = Field(None, alias="IsHygiene", description="Either 'true' or 'false'")
    appointment_type_num: Optional[int] = Field(None, alias="AppointmentTypeNum", description="FK to appointmenttype.AppointmentTypeNum")


class SchedulePlannedAppointmentRequest(BaseModel):
    """Request model for scheduling a planned appointment."""
    
    planned_apt_num: int = Field(..., alias="plannedAptNum", description="FK to appointment.AptNum where AptStatus=Planned")
    apt_date_time: datetime = Field(..., alias="AptDateTime", description="Appointment date and time (yyyy-MM-dd HH:mm:ss)")
    op: int = Field(..., alias="Op", description="FK to operatory.OperatoryNum")
