"""InsSubs client for Open Dental SDK."""

from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from ...base.resource import BaseResource
from .models import (
    InsSub,
    CreateInsSubRequest,
    UpdateInsSubRequest,
    InsSubListResponse
)


class InsSubsClient(BaseResource):
    """
    Client for managing insurance subscriptions in Open Dental.
    
    InsSubs link an InsPlan to a Subscriber (patient).
    Works together with PatPlans to indicate coverage.
    """
    
    def __init__(self, client):
        """Initialize the ins subs client."""
        super().__init__(client, "inssubs")
    
    def get(self, ins_sub_num: Union[int, str]) -> InsSub:
        """
        Get a single InsSub by InsSubNum.
        
        Version Added: 22.4.28
        
        Args:
            ins_sub_num: The InsSubNum
            
        Returns:
            InsSub: The insurance subscription object
        """
        ins_sub_num = self._validate_id(ins_sub_num)
        endpoint = self._build_endpoint(ins_sub_num)
        response = self._get(endpoint)
        return self._handle_response(response, InsSub)
    
    def list(
        self,
        plan_num: Optional[int] = None,
        subscriber: Optional[int] = None,
        sec_date_t_edit: Optional[Union[datetime, str]] = None
    ) -> InsSubListResponse:
        """
        Get all InsSubs based on provided parameters.
        
        Version Added: 22.4.28
        
        If no parameter is given, it will get all InsSubs ordered by InsSubNum.
        
        Args:
            plan_num: Optional. FK to insplan.PlanNum
            subscriber: Optional. FK to patient.PatNum (subscriber)
            sec_date_t_edit: Optional. Returns all InsSubs on or after this date
            
        Returns:
            InsSubListResponse: List of insurance subscriptions
        """
        params: Dict[str, Any] = {}
        
        if plan_num is not None:
            params["PlanNum"] = plan_num
        if subscriber is not None:
            params["Subscriber"] = subscriber
        if sec_date_t_edit is not None:
            # Format datetime as string if needed
            if isinstance(sec_date_t_edit, datetime):
                params["SecDateTEdit"] = sec_date_t_edit.strftime("%Y-%m-%d %H:%M:%S")
            else:
                params["SecDateTEdit"] = sec_date_t_edit
                
        endpoint = self._build_endpoint()
        response = self._get(endpoint, params=params)
        
        # API returns a list directly
        if isinstance(response, list):
            return InsSubListResponse(
                subs=[InsSub(**item) for item in response]
            )
        else:
            return InsSubListResponse(subs=[])
    
    def create(self, sub_data: Union[CreateInsSubRequest, dict]) -> InsSub:
        """
        Create a new InsSub (insurance subscription).
        
        Version Added: 21.1
        
        This does not create a new insurance plan or change benefits.
        
        Args:
            sub_data: The InsSub data to create
            
        Returns:
            InsSub: The created insurance subscription object
        """
        endpoint = self._build_endpoint()
        
        if isinstance(sub_data, dict):
            data = sub_data
        else:
            data = sub_data.model_dump(exclude_none=True, by_alias=True)
            
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, InsSub)
    
    def update(
        self,
        ins_sub_num: Union[int, str],
        sub_data: Union[UpdateInsSubRequest, dict]
    ) -> InsSub:
        """
        Update an existing InsSub.
        
        Version Added: 21.1
        
        Can be used to assign a different PlanNum or Subscriber to this InsSub.
        None of these changes affect the InsSubNum, so all PatPlans (coverage)
        for family members will continue to point to this InsSub.
        
        Note: SecDateTEdit is updated automatically and cannot be set by developers.
        
        Args:
            ins_sub_num: The InsSubNum
            sub_data: The InsSub data to update
            
        Returns:
            InsSub: The updated insurance subscription object
        """
        ins_sub_num = self._validate_id(ins_sub_num)
        endpoint = self._build_endpoint(ins_sub_num)
        
        if isinstance(sub_data, dict):
            data = sub_data
        else:
            data = sub_data.model_dump(exclude_none=True, by_alias=True)
            
        response = self._put(endpoint, json_data=data)
        return self._handle_response(response, InsSub)
    
    def delete(self, ins_sub_num: Union[int, str]) -> bool:
        """
        Delete an InsSub.
        
        Version Added: 21.1
        
        Will fail if any PatPlans exist that reference this InsSub.
        
        Args:
            ins_sub_num: The InsSubNum
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            OpenDentalAPIError: If PatPlans are still attached
        """
        ins_sub_num = self._validate_id(ins_sub_num)
        endpoint = self._build_endpoint(ins_sub_num)
        response = self._delete(endpoint)
        return response is None or response.get("success", True)
    
    def get_by_plan(self, plan_num: int) -> List[InsSub]:
        """
        Get all InsSubs for a specific insurance plan.
        
        Args:
            plan_num: Insurance plan number (FK to insplan.PlanNum)
            
        Returns:
            List[InsSub]: List of insurance subscriptions for the plan
        """
        result = self.list(plan_num=plan_num)
        return result.subs
    
    def get_by_subscriber(self, subscriber: int) -> List[InsSub]:
        """
        Get all InsSubs for a specific subscriber (patient).
        
        Args:
            subscriber: Patient number (FK to patient.PatNum)
            
        Returns:
            List[InsSub]: List of insurance subscriptions for the subscriber
        """
        result = self.list(subscriber=subscriber)
        return result.subs
    
    def get_modified_since(self, date: Union[datetime, str]) -> List[InsSub]:
        """
        Get all InsSubs modified on or after a specific date.
        
        Args:
            date: Date to filter by (datetime or string in format "YYYY-MM-DD HH:MM:SS")
            
        Returns:
            List[InsSub]: List of insurance subscriptions modified since the date
        """
        result = self.list(sec_date_t_edit=date)
        return result.subs
    
    def ins_sub_exists(self, ins_sub_num: Union[int, str]) -> bool:
        """
        Check if an InsSub exists.
        
        Args:
            ins_sub_num: The InsSubNum to check
            
        Returns:
            bool: True if the InsSub exists, False otherwise
        """
        try:
            self.get(ins_sub_num)
            return True
        except Exception:
            return False

