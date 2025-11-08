"""PatPlans client for Open Dental SDK."""

from typing import List, Optional, Union, Dict, Any
from ...base.resource import BaseResource
from .models import (
    PatPlan,
    CreatePatPlanRequest,
    UpdatePatPlanRequest,
    PatPlanListResponse
)


class PatPlansClient(BaseResource):
    """Client for managing patient insurance plans in Open Dental."""
    
    def __init__(self, client):
        """Initialize the pat plans client."""
        super().__init__(client, "patplans")
    
    def get(
        self,
        pat_num: Optional[int] = None,
        ins_sub_num: Optional[int] = None
    ) -> PatPlanListResponse:
        """
        Get a list of PatPlans that meet search criteria.
        
        Version Added: 22.4.27
        
        Args:
            pat_num: Optional. FK to patient.PatNum
            ins_sub_num: Optional. FK to inssub.InsSubNum
            
        Returns:
            PatPlanListResponse: List of PatPlans matching criteria
        """
        params: Dict[str, Any] = {}
        
        if pat_num is not None:
            params["PatNum"] = pat_num
        if ins_sub_num is not None:
            params["InsSubNum"] = ins_sub_num
            
        endpoint = self._build_endpoint()
        response = self._get(endpoint, params=params)
        
        # API returns a list directly
        if isinstance(response, list):
            return PatPlanListResponse(
                plans=[PatPlan(**item) for item in response]
            )
        else:
            return PatPlanListResponse(plans=[])
    
    def list(
        self,
        pat_num: Optional[int] = None,
        ins_sub_num: Optional[int] = None
    ) -> List[PatPlan]:
        """
        Get a list of PatPlans as a simple list.
        
        Args:
            pat_num: Optional. FK to patient.PatNum
            ins_sub_num: Optional. FK to inssub.InsSubNum
            
        Returns:
            List[PatPlan]: List of PatPlans matching criteria
        """
        result = self.get(pat_num=pat_num, ins_sub_num=ins_sub_num)
        return result.plans
    
    def create(self, plan_data: Union[CreatePatPlanRequest, dict]) -> PatPlan:
        """
        Create a new PatPlan (adds insurance coverage for a patient).
        
        Version Added: 21.1
        
        Args:
            plan_data: The PatPlan data to create
            
        Returns:
            PatPlan: The created PatPlan object
            
        Raises:
            OpenDentalAPIError: If plan is already linked to the InsSub
        """
        endpoint = self._build_endpoint()
        
        if isinstance(plan_data, dict):
            data = plan_data
        else:
            data = plan_data.model_dump(exclude_none=True, by_alias=True)
            
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, PatPlan)
    
    def update(
        self,
        pat_plan_num: Union[int, str],
        plan_data: Union[UpdatePatPlanRequest, dict]
    ) -> PatPlan:
        """
        Update an existing PatPlan.
        
        Version Added: 21.4
        
        Note: PatNum cannot be updated. Drop the PatPlan and recreate it instead.
        
        Args:
            pat_plan_num: The PatPlanNum
            plan_data: The PatPlan data to update
            
        Returns:
            PatPlan: The updated PatPlan object
        """
        pat_plan_num = self._validate_id(pat_plan_num)
        endpoint = self._build_endpoint(pat_plan_num)
        
        if isinstance(plan_data, dict):
            data = plan_data
        else:
            data = plan_data.model_dump(exclude_none=True, by_alias=True)
            
        response = self._put(endpoint, json_data=data)
        return self._handle_response(response, PatPlan)
    
    def delete(self, pat_plan_num: Union[int, str]) -> bool:
        """
        Delete a PatPlan ("Drop" in Open Dental UI).
        
        Version Added: 21.1
        
        This removes a PatPlan row from the database, indicating no coverage,
        but does not affect the InsPlan itself.
        
        Args:
            pat_plan_num: The PatPlanNum
            
        Returns:
            bool: True if deletion was successful
        """
        pat_plan_num = self._validate_id(pat_plan_num)
        endpoint = self._build_endpoint(pat_plan_num)
        response = self._delete(endpoint)
        return response is None or response.get("success", True)
    
    def get_by_patient(self, pat_num: int) -> List[PatPlan]:
        """
        Get all PatPlans for a specific patient.
        
        Args:
            pat_num: Patient number (FK to patient.PatNum)
            
        Returns:
            List[PatPlan]: List of PatPlans for the patient
        """
        return self.list(pat_num=pat_num)
    
    def get_by_ins_sub(self, ins_sub_num: int) -> List[PatPlan]:
        """
        Get all PatPlans for a specific insurance subscription.
        
        Args:
            ins_sub_num: Insurance subscription number (FK to inssub.InsSubNum)
            
        Returns:
            List[PatPlan]: List of PatPlans for the subscription
        """
        return self.list(ins_sub_num=ins_sub_num)
    
    def drop_coverage(self, pat_plan_num: Union[int, str]) -> bool:
        """
        Drop insurance coverage for a patient (alias for delete).
        
        This is the terminology used in the Open Dental UI.
        
        Args:
            pat_plan_num: The PatPlanNum
            
        Returns:
            bool: True if coverage was dropped successfully
        """
        return self.delete(pat_plan_num)
    
    def pat_plan_exists(self, pat_plan_num: Union[int, str]) -> bool:
        """
        Check if a PatPlan exists by attempting an empty update.
        
        This is a workaround for the API limitation where there's no GET endpoint
        for individual PatPlans by PatPlanNum.
        
        Args:
            pat_plan_num: The PatPlanNum to check
            
        Returns:
            bool: True if the PatPlan exists, False otherwise
        """
        try:
            # Attempt an empty update - if it succeeds, the PatPlan exists
            self.update(pat_plan_num, {})
            return True
        except Exception:
            # If update fails (404 or other error), PatPlan doesn't exist
            return False

