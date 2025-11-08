"""Appointment types and enums for Open Dental SDK."""

from enum import Enum


class AppointmentStatus(str, Enum):
    """
    Appointment status enum matching Open Dental API.
    
    These are the valid AptStatus values.
    """
    SCHEDULED = "Scheduled"
    COMPLETE = "Complete"
    UNSCHED_LIST = "UnschedList"
    ASAP = "ASAP"
    BROKEN = "Broken"
    PLANNED = "Planned"
    PT_NOTE = "PtNote"
    PT_NOTE_COMPLETED = "PtNoteCompleted"


class AppointmentPriority(str, Enum):
    """Appointment priority enum."""
    NORMAL = "Normal"
    ASAP = "ASAP"


class ConfirmationStatus(str, Enum):
    """
    Confirmation status enum for confirmVal field.
    
    These correspond to automated messaging statuses.
    """
    NONE = "None"  # Default status for new appointments
    SENT = "Sent"
    CONFIRMED = "Confirmed"
    NOT_ACCEPTED = "Not Accepted"
    FAILED = "Failed"


class BreakType(str, Enum):
    """Break type enum for breaking appointments."""
    MISSED = "Missed"  # Missed without notice (adds D9986 procedure)
    CANCELLED = "Cancelled"  # Less than 24hrs notice (adds D9987 procedure)


class BooleanString(str, Enum):
    """Boolean string enum for Open Dental API."""
    TRUE = "true"
    FALSE = "false"
