"""Preference types and enums for Open Dental SDK."""

from enum import Enum


class CommonPreferenceNames(str, Enum):
    """
    Common preference names for easy reference.
    
    This is not an exhaustive list (~1000 preferences exist).
    These are just commonly used preferences.
    """
    
    # Recall preferences
    RECALL_DAYS_PAST = "RecallDaysPast"
    RECALL_DAYS_FUTURE = "RecallDaysFuture"
    
    # Practice defaults
    PRACTICE_DEFAULT_BILL_TYPE = "PracticeDefaultBillType"
    PRACTICE_TITLE = "PracticeTitle"
    PRACTICE_PHONE = "PracticePhone"
    
    # Appointment preferences
    APPOINTMENT_TIME_ARRIVED_TRIGGER = "AppointmentTimeArrivedTrigger"
    APPOINTMENT_TIME_SEATED_TRIGGER = "AppointmentTimeSeatedTrigger"
    APPOINTMENT_TIME_DISMISSED_TRIGGER = "AppointmentTimeDismissedTrigger"

