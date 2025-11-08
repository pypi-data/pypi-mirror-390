"""Appointments client for Open Dental SDK."""

from typing import List, Optional, Union, Dict, Any
from datetime import datetime, date
from ...base.resource import BaseResource
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


class AppointmentsClient(BaseResource):
    """
    Client for managing appointments in Open Dental.
    
    Provides access to all appointment-related operations including:
    - CRUD operations for appointments
    - Planned appointments
    - Web scheduling
    - Appointment confirmation and breaking
    - ASAP and slot management
    """
    
    def __init__(self, client):
        """Initialize the appointments client."""
        super().__init__(client, "appointments")
    
    def get(self, apt_num: Union[int, str]) -> Appointment:
        """
        Get a single appointment by AptNum.
        
        Version Added: 21.1
        
        Args:
            apt_num: The appointment number (AptNum)
            
        Returns:
            Appointment: The appointment object
            
        Example:
            apt = client.appointments.get(18)
            print(f"Patient: {apt.pat_num}, Provider: {apt.prov_abbr}")
        """
        apt_num = self._validate_id(apt_num)
        endpoint = self._build_endpoint(apt_num)
        response = self._get(endpoint)
        return self._handle_response(response, Appointment)
    
    def list(
        self,
        pat_num: Optional[int] = None,
        apt_status: Optional[str] = None,
        op: Optional[int] = None,
        date: Optional[Union[date, str]] = None,
        date_start: Optional[Union[date, str]] = None,
        date_end: Optional[Union[date, str]] = None,
        clinic_num: Optional[int] = None,
        date_t_stamp: Optional[Union[datetime, str]] = None,
        appointment_type_num: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Appointment]:
        """
        Get multiple appointments with optional filters.
        
        Version Added: 21.1
        
        Args:
            pat_num: Filter by patient number (Added in 21.4)
            apt_status: Filter by status: 'Scheduled', 'Complete', 'UnschedList', 'ASAP', 'Broken', 'Planned', 'PtNote', 'PtNoteCompleted' (Added in 22.4.28)
            op: Filter by operatory (Added in 23.2.27)
            date: Search for a single day (yyyy-MM-dd)
            date_start: Search range start date (yyyy-MM-dd)
            date_end: Search range end date (yyyy-MM-dd)
            clinic_num: Filter by clinic number
            date_t_stamp: Only include appointments altered after this date (yyyy-MM-dd HH:mm:ss)
            appointment_type_num: Filter by appointment type (Added in 24.4.22)
            offset: Pagination offset
            
        Returns:
            List[Appointment]: List of matching appointments
            
        Example:
            # Get all scheduled appointments for a patient
            apts = client.appointments.list(
                pat_num=20,
                apt_status="Scheduled"
            )
            
            # Get appointments for a date range
            apts = client.appointments.list(
                date_start="2020-07-30",
                date_end="2020-08-02"
            )
            
            # Sync appointments (use stored serverDateTime)
            apts = client.appointments.list(
                date_t_stamp="2021-05-03 08:30:12",
                clinic_num=3
            )
        """
        params: Dict[str, Any] = {}
        
        if pat_num is not None:
            params["PatNum"] = pat_num
        if apt_status is not None:
            params["AptStatus"] = apt_status
        if op is not None:
            params["Op"] = op
        if date is not None:
            params["date"] = date if isinstance(date, str) else date.strftime("%Y-%m-%d")
        if date_start is not None:
            params["dateStart"] = date_start if isinstance(date_start, str) else date_start.strftime("%Y-%m-%d")
        if date_end is not None:
            params["dateEnd"] = date_end if isinstance(date_end, str) else date_end.strftime("%Y-%m-%d")
        if clinic_num is not None:
            params["ClinicNum"] = clinic_num
        if date_t_stamp is not None:
            params["DateTStamp"] = date_t_stamp if isinstance(date_t_stamp, str) else date_t_stamp.strftime("%Y-%m-%d %H:%M:%S")
        if appointment_type_num is not None:
            params["AppointmentTypeNum"] = appointment_type_num
        if offset is not None:
            params["Offset"] = offset
        
        endpoint = self._build_endpoint()
        response = self._get(endpoint, params=params)
        return self._handle_list_response(response, Appointment)
    
    def create(
        self,
        apt_data: Union[CreateAppointmentRequest, Dict[str, Any]]
    ) -> Appointment:
        """
        Create a new appointment.
        
        Version Added: 21.1
        
        Args:
            apt_data: Appointment data
                - PatNum: Required. FK to patient.PatNum
                - AptDateTime: Required. Appointment date and time (yyyy-MM-dd HH:mm:ss)
                - Op: Required. FK to operatory.OperatoryNum
                - ProvNum: Required. FK to provider.ProvNum
                - Pattern: Required. Time pattern ('X' and '/' characters)
                - Plus optional fields
                
        Returns:
            Appointment: The created appointment object
            
        Example:
            apt = client.appointments.create({
                "PatNum": 52,
                "AptDateTime": "2022-08-09 09:00:00",
                "Op": 1,
                "ProvNum": 1,
                "Pattern": "//XX//",
                "Note": "Patient prefers morning appointments"
            })
        """
        endpoint = self._build_endpoint()
        
        if isinstance(apt_data, dict):
            data = apt_data
        else:
            data = apt_data.model_dump(exclude_none=True, by_alias=True)
        
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, Appointment)
    
    def update(
        self,
        apt_num: Union[int, str],
        apt_data: Union[UpdateAppointmentRequest, Dict[str, Any]]
    ) -> Appointment:
        """
        Update an existing appointment.
        
        All fields are optional. Note will overwrite any existing note.
        Use append_note() to add to existing note instead.
        
        Args:
            apt_num: The appointment number (AptNum)
            apt_data: Appointment data to update (all fields optional)
                
        Returns:
            Appointment: The updated appointment object
            
        Example:
            apt = client.appointments.update(34, {
                "Note": "Patient called to reschedule"
            })
        """
        apt_num = self._validate_id(apt_num)
        endpoint = self._build_endpoint(apt_num)
        
        if isinstance(apt_data, dict):
            data = apt_data
        else:
            data = apt_data.model_dump(exclude_none=True, by_alias=True)
        
        response = self._put(endpoint, json_data=data)
        return self._handle_response(response, Appointment)
    
    def update_note(
        self,
        apt_num: Union[int, str],
        note: str
    ) -> Appointment:
        """
        Update (overwrite) the appointment note completely.
        
        This REPLACES any existing note with the new text.
        Use append_note() if you want to add to the existing note instead.
        
        Args:
            apt_num: The appointment number (AptNum)
            note: New note text (overwrites existing note)
            
        Returns:
            Appointment: The updated appointment object
            
        Example:
            # This will replace the entire note
            apt = client.appointments.update_note(34, "Patient confirmed via phone")
        """
        return self.update(apt_num, {"Note": note})
    
    def append_note(
        self,
        apt_num: Union[int, str],
        note: str
    ) -> None:
        """
        Append a new line of text to an appointment's existing note.
        
        Version Added: 21.1
        
        This ADDS to the existing note without overwriting it.
        If a note already exists, a carriage return is included before the new note.
        Use update_note() if you want to replace the entire note instead.
        
        Args:
            apt_num: The appointment number (AptNum)
            note: Note text to append (adds to bottom of existing note)
            
        Example:
            # This will add to the existing note
            client.appointments.append_note(34, "Requests reschedule")
            # Existing note: "Patient prefers morning"
            # After append: "Patient prefers morning\nRequests reschedule"
        """
        apt_num = self._validate_id(apt_num)
        endpoint = self._build_endpoint(f"{apt_num}/Note")
        
        data = {"Note": note}
        self._put(endpoint, json_data=data)
    
    def confirm(
        self,
        apt_num: Union[int, str],
        confirm_val: Optional[str] = None,
        def_num: Optional[int] = None
    ) -> None:
        """
        Update appointment.Confirmed for a specified appointment.
        
        Version Added: 21.1
        
        Only one parameter is allowed: either confirm_val or def_num.
        
        Args:
            apt_num: The appointment number (AptNum)
            confirm_val: Either 'None', 'Sent', 'Confirmed', 'Not Accepted', or 'Failed'
            def_num: FK to definition.DefNum where definition.Category=2 (Added in 21.2)
            
        Example:
            # Using confirm value
            client.appointments.confirm(34, confirm_val="Confirmed")
            
            # Using definition number
            client.appointments.confirm(34, def_num=209)
        """
        if confirm_val is None and def_num is None:
            raise ValueError("Either confirm_val or def_num must be provided")
        if confirm_val is not None and def_num is not None:
            raise ValueError("Only one of confirm_val or def_num can be provided")
        
        apt_num = self._validate_id(apt_num)
        endpoint = self._build_endpoint(f"{apt_num}/Confirm")
        
        data = {}
        if confirm_val is not None:
            data["confirmVal"] = confirm_val
        if def_num is not None:
            data["defNum"] = def_num
        
        self._put(endpoint, json_data=data)
    
    def break_appointment(
        self,
        apt_num: Union[int, str],
        send_to_unscheduled_list: bool = True,
        break_type: Optional[str] = None
    ) -> None:
        """
        Break an appointment.
        
        Version Added: 21.3
        
        Only appointments with AptStatus='Scheduled' can be broken.
        Creates a CommLog entry if office has that preference turned on.
        
        To reschedule a broken appointment, use update() to change the
        Status, AptDateTime, and Op.
        
        Args:
            apt_num: The appointment number (AptNum)
            send_to_unscheduled_list: Usually true. False only if using break_type='Missed' or 'Cancelled'
            break_type: Optional. Either 'Missed' (adds D9986 procedure) or 'Cancelled' (adds D9987 procedure)
            
        Example:
            # Break and send to unscheduled list
            client.appointments.break_appointment(5, send_to_unscheduled_list=True)
            
            # Break for missed appointment (adds fee)
            client.appointments.break_appointment(5, break_type="Missed")
        """
        apt_num = self._validate_id(apt_num)
        endpoint = self._build_endpoint(f"{apt_num}/Break")
        
        data = {
            "sendToUnscheduledList": "true" if send_to_unscheduled_list else "false"
        }
        if break_type is not None:
            data["breakType"] = break_type
        
        self._put(endpoint, json_data=data)
    
    def create_planned(
        self,
        apt_data: Union[CreatePlannedAppointmentRequest, Dict[str, Any]]
    ) -> Appointment:
        """
        Create a planned appointment.
        
        Version Added: 21.2
        
        Args:
            apt_data: Planned appointment data
                - PatNum: Required. FK to patient.PatNum
                - Pattern: Required. Time pattern
                - ProvNum: Required. FK to provider.ProvNum
                - Plus optional fields
                
        Returns:
            Appointment: The created planned appointment
            
        Example:
            planned = client.appointments.create_planned({
                "PatNum": 52,
                "Pattern": "//XX//",
                "ProvNum": 1,
                "Note": "Crown prep"
            })
        """
        endpoint = self._build_endpoint("Planned")
        
        if isinstance(apt_data, dict):
            data = apt_data
        else:
            data = apt_data.model_dump(exclude_none=True, by_alias=True)
        
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, Appointment)
    
    def schedule_planned(
        self,
        planned_apt_num: int,
        apt_date_time: Union[datetime, str],
        op: int
    ) -> Appointment:
        """
        Schedule a planned appointment.
        
        Version Added: 21.2
        
        Args:
            planned_apt_num: FK to appointment.AptNum where AptStatus='Planned'
            apt_date_time: Appointment date and time (yyyy-MM-dd HH:mm:ss)
            op: FK to operatory.OperatoryNum
            
        Returns:
            Appointment: The scheduled appointment
            
        Example:
            apt = client.appointments.schedule_planned(
                planned_apt_num=123,
                apt_date_time="2022-09-15 10:00:00",
                op=2
            )
        """
        endpoint = self._build_endpoint("SchedulePlanned")
        
        data = {
            "plannedAptNum": planned_apt_num,
            "AptDateTime": apt_date_time if isinstance(apt_date_time, str) else apt_date_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Op": op
        }
        
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, Appointment)
    
    # Helper methods
    
    def get_by_patient(
        self,
        pat_num: int,
        apt_status: Optional[str] = None
    ) -> List[Appointment]:
        """
        Get all appointments for a specific patient.
        
        Args:
            pat_num: Patient number
            apt_status: Optional status filter
            
        Returns:
            List[Appointment]: List of patient's appointments
            
        Example:
            apts = client.appointments.get_by_patient(20, apt_status="Scheduled")
        """
        return self.list(pat_num=pat_num, apt_status=apt_status)
    
    def get_by_date(
        self,
        target_date: Union[date, str],
        clinic_num: Optional[int] = None
    ) -> List[Appointment]:
        """
        Get all appointments for a specific date.
        
        Args:
            target_date: Target date (yyyy-MM-dd)
            clinic_num: Optional clinic filter
            
        Returns:
            List[Appointment]: List of appointments for that date
            
        Example:
            apts = client.appointments.get_by_date("2020-07-31")
        """
        return self.list(date=target_date, clinic_num=clinic_num)
    
    def get_by_date_range(
        self,
        date_start: Union[date, str],
        date_end: Union[date, str],
        clinic_num: Optional[int] = None,
        apt_status: Optional[str] = None
    ) -> List[Appointment]:
        """
        Get appointments within a date range.
        
        Args:
            date_start: Start date (yyyy-MM-dd)
            date_end: End date (yyyy-MM-dd)
            clinic_num: Optional clinic filter
            apt_status: Optional status filter
            
        Returns:
            List[Appointment]: List of appointments in date range
            
        Example:
            apts = client.appointments.get_by_date_range(
                date_start="2020-07-30",
                date_end="2020-08-02",
                apt_status="Scheduled"
            )
        """
        return self.list(
            date_start=date_start,
            date_end=date_end,
            clinic_num=clinic_num,
            apt_status=apt_status
        )
    
    def get_by_operatory(
        self,
        op: int,
        date: Optional[Union[date, str]] = None
    ) -> List[Appointment]:
        """
        Get appointments for a specific operatory.
        
        Version Added: 23.2.27 (Op filter)
        
        Args:
            op: Operatory number
            date: Optional date filter
            
        Returns:
            List[Appointment]: List of appointments for that operatory
            
        Example:
            apts = client.appointments.get_by_operatory(op=3, date="2020-07-31")
        """
        return self.list(op=op, date=date)
    
    def get_modified_since(
        self,
        date_t_stamp: Union[datetime, str],
        clinic_num: Optional[int] = None
    ) -> List[Appointment]:
        """
        Get appointments modified after a specific date/time.
        
        Useful for synchronization - store the serverDateTime from
        the response and use it for the next call.
        
        Args:
            date_t_stamp: Date and time stamp (yyyy-MM-dd HH:mm:ss)
            clinic_num: Optional clinic filter
            
        Returns:
            List[Appointment]: List of modified appointments
            
        Example:
            # Initial sync
            apts = client.appointments.get_modified_since("2021-05-03 08:30:12")
            # Store apts[0].server_date_time for next sync
        """
        return self.list(date_t_stamp=date_t_stamp, clinic_num=clinic_num)
    
    def reschedule(
        self,
        apt_num: Union[int, str],
        apt_date_time: Union[datetime, str],
        op: int
    ) -> Appointment:
        """
        Reschedule an appointment to a new date/time and operatory.
        
        Args:
            apt_num: Appointment number
            apt_date_time: New date and time
            op: New operatory
            
        Returns:
            Appointment: The rescheduled appointment
            
        Example:
            apt = client.appointments.reschedule(
                apt_num=34,
                apt_date_time="2022-08-15 14:00:00",
                op=2
            )
        """
        return self.update(apt_num, {
            "AptDateTime": apt_date_time if isinstance(apt_date_time, str) else apt_date_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Op": op
        })
    
    def complete(self, apt_num: Union[int, str]) -> Appointment:
        """
        Mark an appointment as complete.
        
        Args:
            apt_num: Appointment number
            
        Returns:
            Appointment: The completed appointment
            
        Example:
            apt = client.appointments.complete(34)
        """
        return self.update(apt_num, {"AptStatus": "Complete"})
    
    def set_arrived(
        self,
        apt_num: Union[int, str],
        time_arrived: Optional[str] = None
    ) -> Appointment:
        """
        Set the arrival time for an appointment.
        
        Version Added: 25.2.10
        
        Args:
            apt_num: Appointment number
            time_arrived: Time in HH:mm:ss format (defaults to current time)
            
        Returns:
            Appointment: The updated appointment
            
        Example:
            apt = client.appointments.set_arrived(34, "09:15:00")
        """
        data: Dict[str, Any] = {}
        if time_arrived:
            data["DateTimeArrived"] = time_arrived
        else:
            from datetime import datetime
            data["DateTimeArrived"] = datetime.now().strftime("%H:%M:%S")
        
        return self.update(apt_num, data)
    
    def set_seated(
        self,
        apt_num: Union[int, str],
        time_seated: Optional[str] = None
    ) -> Appointment:
        """
        Set the seated time for an appointment.
        
        Version Added: 25.2.10
        
        Args:
            apt_num: Appointment number
            time_seated: Time in HH:mm:ss format (defaults to current time)
            
        Returns:
            Appointment: The updated appointment
            
        Example:
            apt = client.appointments.set_seated(34, "09:20:00")
        """
        data: Dict[str, Any] = {}
        if time_seated:
            data["DateTimeSeated"] = time_seated
        else:
            from datetime import datetime
            data["DateTimeSeated"] = datetime.now().strftime("%H:%M:%S")
        
        return self.update(apt_num, data)
    
    def set_dismissed(
        self,
        apt_num: Union[int, str],
        time_dismissed: Optional[str] = None
    ) -> Appointment:
        """
        Set the dismissed time for an appointment.
        
        Version Added: 25.2.10
        
        Args:
            apt_num: Appointment number
            time_dismissed: Time in HH:mm:ss format (defaults to current time)
            
        Returns:
            Appointment: The updated appointment
            
        Example:
            apt = client.appointments.set_dismissed(34, "10:45:00")
        """
        data: Dict[str, Any] = {}
        if time_dismissed:
            data["DateTimeDismissed"] = time_dismissed
        else:
            from datetime import datetime
            data["DateTimeDismissed"] = datetime.now().strftime("%H:%M:%S")
        
        return self.update(apt_num, data)
