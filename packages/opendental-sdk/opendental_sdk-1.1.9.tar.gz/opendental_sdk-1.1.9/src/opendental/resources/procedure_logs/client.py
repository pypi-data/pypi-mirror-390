"""ProcedureLogs client for Open Dental SDK."""

import time
from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from ...base.resource import BaseResource
from .models import (
    ProcedureLog,
    CreateProcedureLogRequest,
    UpdateProcedureLogRequest,
    ProcedureLogListResponse,
    InsuranceHistoryItem,
    InsuranceHistoryResponse,
    GroupNote,
    UpdateGroupNoteRequest,
    CreateInsuranceHistoryRequest
)


class ProcedureLogsClient(BaseResource):
    """
    Client for managing procedure logs in Open Dental.
    
    ProcedureLogs represent actual procedures performed or planned for patients.
    These are complex - see the Procedure documentation for more details.
    
    Reference: https://www.opendental.com/site/apiprocedurelogs.html
    """
    
    def __init__(self, client):
        """Initialize the procedure logs client."""
        super().__init__(client, "procedurelogs")
    
    def get(self, proc_num: Union[int, str]) -> ProcedureLog:
        """
        Get a single procedure log by ProcNum.
        
        Version Added: 23.3.13
        
        Args:
            proc_num: The procedure number (ProcNum)
            
        Returns:
            ProcedureLog: The procedure log object
            
        Example:
            proc = client.procedure_logs.get(proc_num=20)
        """
        proc_num = self._validate_id(proc_num)
        endpoint = self._build_endpoint(proc_num)
        response = self._get(endpoint)
        return self._handle_response(response, ProcedureLog)
    
    def list(
        self,
        pat_num: Optional[int] = None,
        apt_num: Optional[int] = None,
        proc_status: Optional[str] = None,
        planned_apt_num: Optional[int] = None,
        clinic_num: Optional[int] = None,
        code_num: Optional[int] = None,
        date_t_stamp: Optional[Union[datetime, str]] = None,
        offset: int = 0
    ) -> ProcedureLogListResponse:
        """
        Get a list of procedure logs that meet search criteria.
        
        Version Added: 21.1
        
        Args:
            pat_num: Optional. FK to patient.PatNum
            apt_num: Optional. FK to appointment.AptNum (Added in version 22.3.32)
            proc_status: Optional. Procedure status (Added in version 25.2.21)
                         Either "TP", "C", "EC", "EO", "R", "D", "Cn", or "TPi"
            planned_apt_num: Optional. FK to planned appointment (Added in version 24.4.5)
            clinic_num: Optional. FK to clinic.ClinicNum (Added in version 23.3.13)
            code_num: Optional. FK to procedurecode.CodeNum (Added in version 25.2.21)
            date_t_stamp: Optional. Get procedures created on or after this date
                         (datetime object or string in "yyyy-MM-dd HH:mm:ss" format)
            offset: Starting record number (default 0)
            
        Returns:
            ProcedureLogListResponse: List of procedure logs
            
        Examples:
            # Get by patient
            result = client.procedure_logs.list(pat_num=261)
            
            # Get by appointment
            result = client.procedure_logs.list(apt_num=202)
            
            # Get by date with pagination
            result = client.procedure_logs.list(
                date_t_stamp="2020-07-30 08:00:00",
                offset=400
            )
        """
        params: Dict[str, Any] = {}
        
        if pat_num is not None:
            params["PatNum"] = pat_num
        if apt_num is not None:
            params["AptNum"] = apt_num
        if proc_status is not None:
            params["ProcStatus"] = proc_status
        if planned_apt_num is not None:
            params["PlannedAptNum"] = planned_apt_num
        if clinic_num is not None:
            params["ClinicNum"] = clinic_num
        if code_num is not None:
            params["CodeNum"] = code_num
        if date_t_stamp is not None:
            # Format datetime as string if needed
            if isinstance(date_t_stamp, datetime):
                params["DateTStamp"] = date_t_stamp.strftime("%Y-%m-%d %H:%M:%S")
            else:
                params["DateTStamp"] = date_t_stamp
        if offset > 0:
            params["Offset"] = offset
        
        endpoint = self._build_endpoint()
        response = self._get(endpoint, params=params)
        
        # API returns a list directly
        if isinstance(response, list):
            procedure_logs = [ProcedureLog(**item) for item in response]
            return ProcedureLogListResponse(
                procedure_logs=procedure_logs,
                total=len(procedure_logs),
                offset=offset
            )
        
        return ProcedureLogListResponse(procedure_logs=[], total=0, offset=offset)
    
    def get_insurance_history(
        self,
        pat_num: int,
        ins_sub_num: int
    ) -> InsuranceHistoryResponse:
        """
        Get insurance history for a patient's insurance plan.
        
        Version Added: 22.4.31
        
        Gets the previous treatment dates of procedures for a patient's
        insurance plan, similar to the Insurance History form.
        
        Args:
            pat_num: Required. FK to patient.PatNum
            ins_sub_num: Required. FK to inssub.InsSubNum
            
        Returns:
            InsuranceHistoryResponse: Insurance history items
            
        Example:
            history = client.procedure_logs.get_insurance_history(
                pat_num=2617,
                ins_sub_num=2046
            )
        """
        params = {
            "PatNum": pat_num,
            "InsSubNum": ins_sub_num
        }
        
        endpoint = self._build_endpoint("InsuranceHistory")
        response = self._get(endpoint, params=params)
        
        # API returns a list directly
        if isinstance(response, list):
            history = [InsuranceHistoryItem(**item) for item in response]
            return InsuranceHistoryResponse(history=history)
        
        return InsuranceHistoryResponse(history=[])
    
    def list_insurance_history(
        self,
        pat_num: int,
        ins_sub_num: int
    ) -> List[InsuranceHistoryItem]:
        """
        Get insurance history as a list for easier iteration.
        
        Args:
            pat_num: Required. FK to patient.PatNum
            ins_sub_num: Required. FK to inssub.InsSubNum
            
        Returns:
            List[InsuranceHistoryItem]: List of insurance history items
            
        Example:
            history_items = client.procedure_logs.list_insurance_history(
                pat_num=2617,
                ins_sub_num=2046
            )
            for item in history_items:
                print(f"{item.ins_hist_pref_name}: {item.proc_date}")
        """
        response = self.get_insurance_history(pat_num, ins_sub_num)
        return response.history
    
    def get_insurance_history_by_category(
        self,
        pat_num: int,
        ins_sub_num: int,
        category: str
    ) -> Optional[InsuranceHistoryItem]:
        """
        Get a specific insurance history category.
        
        Args:
            pat_num: Required. FK to patient.PatNum
            ins_sub_num: Required. FK to inssub.InsSubNum
            category: Category name (e.g., "InsHistBWCodes", "InsHistExamCodes")
            
        Returns:
            Optional[InsuranceHistoryItem]: History item if found, None otherwise
            
        Example:
            # Get bitewing history
            bw_history = client.procedure_logs.get_insurance_history_by_category(
                pat_num=2617,
                ins_sub_num=2046,
                category="InsHistBWCodes"
            )
            if bw_history:
                print(f"Last bitewing: {bw_history.proc_date}")
        """
        history = self.list_insurance_history(pat_num, ins_sub_num)
        for item in history:
            if item.ins_hist_pref_name == category:
                return item
        return None
    
    def get_insurance_history_dict(
        self,
        pat_num: int,
        ins_sub_num: int
    ) -> Dict[str, InsuranceHistoryItem]:
        """
        Get insurance history as a dictionary keyed by category name.
        
        Args:
            pat_num: Required. FK to patient.PatNum
            ins_sub_num: Required. FK to inssub.InsSubNum
            
        Returns:
            Dict[str, InsuranceHistoryItem]: Dictionary of category to history item
            
        Example:
            history_dict = client.procedure_logs.get_insurance_history_dict(
                pat_num=2617,
                ins_sub_num=2046
            )
            
            if "InsHistBWCodes" in history_dict:
                print(f"Bitewing: {history_dict['InsHistBWCodes'].proc_date}")
            if "InsHistExamCodes" in history_dict:
                print(f"Exam: {history_dict['InsHistExamCodes'].proc_date}")
        """
        history = self.list_insurance_history(pat_num, ins_sub_num)
        return {item.ins_hist_pref_name: item for item in history}
    
    def has_insurance_history(
        self,
        pat_num: int,
        ins_sub_num: int,
        category: str
    ) -> bool:
        """
        Check if a patient has history for a specific insurance category.
        
        Args:
            pat_num: Required. FK to patient.PatNum
            ins_sub_num: Required. FK to inssub.InsSubNum
            category: Category name (e.g., "InsHistBWCodes")
            
        Returns:
            bool: True if history exists (not "No History" or "Not Set"), False otherwise
            
        Example:
            has_bw = client.procedure_logs.has_insurance_history(
                pat_num=2617,
                ins_sub_num=2046,
                category="InsHistBWCodes"
            )
            if has_bw:
                print("Patient has bitewing history")
        """
        item = self.get_insurance_history_by_category(pat_num, ins_sub_num, category)
        if item is None:
            return False
        return item.proc_date not in ("No History", "Not Set")
    
    def get_recent_insurance_procedures(
        self,
        pat_num: int,
        ins_sub_num: int,
        exclude_no_history: bool = True
    ) -> List[InsuranceHistoryItem]:
        """
        Get insurance history items that have actual procedure dates.
        
        Args:
            pat_num: Required. FK to patient.PatNum
            ins_sub_num: Required. FK to inssub.InsSubNum
            exclude_no_history: If True, exclude items with "No History" or "Not Set"
            
        Returns:
            List[InsuranceHistoryItem]: History items with actual dates
            
        Example:
            recent = client.procedure_logs.get_recent_insurance_procedures(
                pat_num=2617,
                ins_sub_num=2046
            )
            for item in recent:
                print(f"{item.ins_hist_pref_name}: {item.proc_date}")
        """
        history = self.list_insurance_history(pat_num, ins_sub_num)
        
        if exclude_no_history:
            return [
                item for item in history
                if item.proc_date not in ("No History", "Not Set")
            ]
        return history
    
    def create_insurance_history(
        self,
        history_data: Union[CreateInsuranceHistoryRequest, Dict[str, Any]]
    ) -> ProcedureLog:
        """
        Create an insurance history entry for a patient.
        
        Version Added: 22.4.31
        
        This functions similarly to entering a date in the Insurance History form
        for a single category. Creates a new Existing Other Provider (EO) procedure
        and Insurance History (InsHist) claimproc for a given patient.
        
        The new procedure will use:
        - Patient's default clinic
        - Patient's default provider
        - First alphanumeric procedure code in the category for the insHistPrefName
        
        Args:
            history_data: Insurance history data
                - PatNum: Required. FK to patient.PatNum
                - InsSubNum: Required. FK to inssub.InsSubNum
                - insHistPrefName: Required. Category name (case sensitive)
                - ProcDate: Required. Date the procedure was completed (yyyy-MM-dd)
                
        Returns:
            ProcedureLog: The created procedure log (with ProcStatus="EO")
            
        Example:
            # Create exam history
            proc = client.procedure_logs.create_insurance_history({
                "PatNum": 572,
                "InsSubNum": 49,
                "insHistPrefName": "InsHistExamCodes",
                "ProcDate": "2023-01-23"
            })
            
            # Using enum for category
            from opendental.resources.procedure_logs import InsuranceHistoryCategory
            
            proc = client.procedure_logs.create_insurance_history({
                "PatNum": 572,
                "InsSubNum": 49,
                "insHistPrefName": InsuranceHistoryCategory.BITEWING_CODES.value,
                "ProcDate": "2023-01-23"
            })
        """
        endpoint = self._build_endpoint("InsuranceHistory")
        
        if isinstance(history_data, dict):
            data = history_data
        else:
            data = history_data.model_dump(exclude_none=True, by_alias=True)
        
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, ProcedureLog)
    
    def create(
        self,
        proc_data: Union[CreateProcedureLogRequest, Dict[str, Any]]
    ) -> ProcedureLog:
        """
        Create a new procedure log.
        
        Version Added: 21.1
        
        Args:
            proc_data: The procedure data to create
            
        Returns:
            ProcedureLog: The created procedure log object
            
        Example:
            proc = client.procedure_logs.create({
                "PatNum": 52,
                "ProcDate": "2022-08-09",
                "ProvNum": 1,
                "CodeNum": 2,
                "ProcFee": "50.00",
                "ProcStatus": "C"
            })
        """
        endpoint = self._build_endpoint()
        
        if isinstance(proc_data, dict):
            data = proc_data
        else:
            data = proc_data.model_dump(exclude_none=True, by_alias=True)
        
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, ProcedureLog)
    
    def update(
        self,
        proc_num: Union[int, str],
        proc_data: Union[UpdateProcedureLogRequest, Dict[str, Any]]
    ) -> ProcedureLog:
        """
        Update an existing procedure log.
        
        Version Added: 21.1
        
        Args:
            proc_num: The procedure number (ProcNum)
            proc_data: The procedure data to update
            
        Returns:
            ProcedureLog: The updated procedure log object
            
        Example:
            proc = client.procedure_logs.update(100, {
                "ProcFee": "250",
                "ProcStatus": "TP",
                "ToothNum": "14",
                "Surf": "MO"
            })
        """
        proc_num = self._validate_id(proc_num)
        endpoint = self._build_endpoint(proc_num)
        
        if isinstance(proc_data, dict):
            data = proc_data
        else:
            data = proc_data.model_dump(exclude_none=True, by_alias=True)
        
        response = self._put(endpoint, json_data=data)
        return self._handle_response(response, ProcedureLog)
    
    def delete(self, proc_num: Union[int, str]) -> bool:
        """
        Delete a procedure log.
        
        Version Added: 22.1
        
        Can only delete procedures with ProcStatus of TP, TPi, or C (added in 23.1.11).
        Cannot delete if attached to claim, insurance payment, patient payment,
        adjustment, prescription, payment plan, has referrals, linked to ortho case,
        or is the last procedure from a preauthorization claim.
        
        Args:
            proc_num: The procedure number (ProcNum)
            
        Returns:
            bool: True if deletion was successful
            
        Example:
            success = client.procedure_logs.delete(proc_num=25)
        """
        proc_num = self._validate_id(proc_num)
        endpoint = self._build_endpoint(proc_num)
        response = self._delete(endpoint)
        return response is None or response.get("success", True)
    
    def update_group_note(
        self,
        proc_num: Union[int, str],
        note_data: Union[UpdateGroupNoteRequest, Dict[str, Any]]
    ) -> GroupNote:
        """
        Update a Group Note procedure.
        
        Version Added: 22.2.29
        
        For more information about Group Notes see Procedure Group Note.
        To update a Note for a single procedure see API ProcNotes.
        
        Args:
            proc_num: Required. Must be a procedure with procCode "~GRP~"
            note_data: The group note data to update
            
        Returns:
            GroupNote: The updated group note object
            
        Example:
            group_note = client.procedure_logs.update_group_note(1473, {
                "PatNum": 30,
                "Note": "Dental exam"
            })
        """
        proc_num = self._validate_id(proc_num)
        endpoint = self._build_endpoint(proc_num, "GroupNote")
        
        if isinstance(note_data, dict):
            data = note_data
        else:
            data = note_data.model_dump(exclude_none=True, by_alias=True)
        
        response = self._put(endpoint, json_data=data)
        return self._handle_response(response, GroupNote)
    
    def delete_group_note(self, proc_num: Union[int, str]) -> bool:
        """
        Delete a GroupNote procedure.
        
        Version Added: 22.3.8
        
        Args:
            proc_num: Required. Must be a procedure with procCode "~GRP~"
            
        Returns:
            bool: True if deletion was successful
            
        Example:
            success = client.procedure_logs.delete_group_note(proc_num=144)
        """
        proc_num = self._validate_id(proc_num)
        endpoint = self._build_endpoint(proc_num, "GroupNote")
        response = self._delete(endpoint)
        return response is None or response.get("success", True)
    
    # Helper methods
    
    def get_by_patient(self, pat_num: int) -> List[ProcedureLog]:
        """
        Get all procedure logs for a specific patient.
        
        Args:
            pat_num: Patient number (FK to patient.PatNum)
            
        Returns:
            List[ProcedureLog]: List of procedure logs for the patient
        """
        result = self.list(pat_num=pat_num)
        return result.procedure_logs
    
    def get_by_appointment(self, apt_num: int) -> List[ProcedureLog]:
        """
        Get all procedure logs for a specific appointment.
        
        Args:
            apt_num: Appointment number (FK to appointment.AptNum)
            
        Returns:
            List[ProcedureLog]: List of procedure logs for the appointment
        """
        result = self.list(apt_num=apt_num)
        return result.procedure_logs
    
    def get_by_status(
        self,
        proc_status: str,
        pat_num: Optional[int] = None
    ) -> List[ProcedureLog]:
        """
        Get procedure logs by status, optionally filtered by patient.
        
        Args:
            proc_status: Procedure status (TP, C, EC, EO, R, D, Cn, TPi)
            pat_num: Optional. Filter by patient number
            
        Returns:
            List[ProcedureLog]: List of matching procedure logs
        """
        result = self.list(proc_status=proc_status, pat_num=pat_num)
        return result.procedure_logs
    
    def get_treatment_planned(self, pat_num: int) -> List[ProcedureLog]:
        """
        Get all treatment planned procedures for a patient.
        
        Args:
            pat_num: Patient number (FK to patient.PatNum)
            
        Returns:
            List[ProcedureLog]: List of treatment planned procedures
        """
        return self.get_by_status(proc_status="TP", pat_num=pat_num)
    
    def get_completed(self, pat_num: int) -> List[ProcedureLog]:
        """
        Get all completed procedures for a patient.
        
        Args:
            pat_num: Patient number (FK to patient.PatNum)
            
        Returns:
            List[ProcedureLog]: List of completed procedures
        """
        return self.get_by_status(proc_status="C", pat_num=pat_num)
    
    def get_modified_since(
        self,
        date: Union[datetime, str],
        offset: int = 0
    ) -> ProcedureLogListResponse:
        """
        Get procedure logs modified on or after a specific date.
        
        Args:
            date: Date to filter by (datetime or string in format "yyyy-MM-dd HH:mm:ss")
            offset: Starting record number (default 0)
            
        Returns:
            ProcedureLogListResponse: Procedure logs modified since the date
        """
        return self.list(date_t_stamp=date, offset=offset)
    
    def get_all(
        self,
        pat_num: Optional[int] = None,
        throttle_delay: float = 0.3
    ) -> List[ProcedureLog]:
        """
        Get ALL procedure logs using pagination strategy.
        
        Args:
            pat_num: Optional. Filter by patient number
            throttle_delay: Delay in seconds between requests (default 0.3s)
            
        Returns:
            List[ProcedureLog]: All procedure logs
        """
        all_procs = []
        offset = 0
        
        while True:
            # Make request with current offset
            response = self.list(pat_num=pat_num, offset=offset)
            
            # Get procedures from response
            procedures = response.procedure_logs
            
            # If no results returned, we're done
            if not procedures:
                break
            
            all_procs.extend(procedures)
            
            # If we got fewer than 100 items, we've reached the end
            if len(procedures) < 100:
                break
            
            # Move to next batch
            offset += 100
            
            # Throttle to prevent rate limiting
            if len(procedures) >= 100:
                time.sleep(throttle_delay)
            
            # Safety check
            if offset > 1_000_000:
                break
        
        return all_procs
