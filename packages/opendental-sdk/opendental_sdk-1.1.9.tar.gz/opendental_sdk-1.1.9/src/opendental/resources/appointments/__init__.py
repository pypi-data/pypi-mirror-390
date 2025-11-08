"""Appointments resource module."""

from .client import AppointmentsClient
from .models import (
    Appointment,
    CreateAppointmentRequest,
    UpdateAppointmentRequest,
    AppendNoteRequest,
    ConfirmAppointmentRequest,
    BreakAppointmentRequest,
    CreatePlannedAppointmentRequest,
    SchedulePlannedAppointmentRequest
)
from .types import (
    AppointmentStatus,
    AppointmentPriority,
    ConfirmationStatus,
    BreakType,
    BooleanString
)

__all__ = [
    "AppointmentsClient",
    "Appointment",
    "CreateAppointmentRequest",
    "UpdateAppointmentRequest",
    "AppendNoteRequest",
    "ConfirmAppointmentRequest",
    "BreakAppointmentRequest",
    "CreatePlannedAppointmentRequest",
    "SchedulePlannedAppointmentRequest",
    "AppointmentStatus",
    "AppointmentPriority",
    "ConfirmationStatus",
    "BreakType",
    "BooleanString",
]
