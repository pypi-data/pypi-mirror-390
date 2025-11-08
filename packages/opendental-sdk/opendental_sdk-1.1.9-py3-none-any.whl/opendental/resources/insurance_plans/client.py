"""Insurance Plans client for Open Dental SDK."""

from typing import List, Optional, Union, Dict, Any
from ...base.resource import BaseResource
from .models import (
    InsurancePlan,
    CreateInsurancePlanRequest,
    UpdateInsurancePlanRequest,
    InsurancePlanListResponse
)


class InsurancePlansClient(BaseResource):
    """Client for managing insurance plans in Open Dental."""
    
    def __init__(self, client):
        """Initialize the insurance plans client."""
        super().__init__(client, "insplans")
    
    def get(self, plan_num: Union[int, str]) -> InsurancePlan:
        """
        Get a single insurance plan by PlanNum.
        
        Version Added: 24.2.11
        
        Args:
            plan_num: The plan number (PlanNum)
            
        Returns:
            InsurancePlan: The insurance plan object
        """
        plan_num = self._validate_id(plan_num)
        endpoint = self._build_endpoint(plan_num)
        response = self._get(endpoint)
        return self._handle_response(response, InsurancePlan)
    
    def list(
        self, 
        plan_type: Optional[str] = None,
        carrier_num: Optional[int] = None
    ) -> InsurancePlanListResponse:
        """
        Get a list of insurance plans with optional filters.
        
        Version Added: 22.3.30
        
        Args:
            plan_type: Optional. Must be one of: "percentage", "p" (PPO), "f" (Flat Copay), or "c" (Capitation)
            carrier_num: Optional. FK to carrier.CarrierNum
            
        Returns:
            InsurancePlanListResponse: List of insurance plans
        """
        params: Dict[str, Any] = {}
        
        if plan_type is not None:
            params["PlanType"] = plan_type
        if carrier_num is not None:
            params["CarrierNum"] = carrier_num
            
        endpoint = self._build_endpoint()
        response = self._get(endpoint, params=params)
        
        # API returns a list directly
        if isinstance(response, list):
            return InsurancePlanListResponse(
                plans=[InsurancePlan(**item) for item in response]
            )
        else:
            return InsurancePlanListResponse(plans=[])
    
    def create(self, plan_data: Union[CreateInsurancePlanRequest, dict]) -> InsurancePlan:
        """
        Create a new insurance plan.
        
        Version Added: 22.4.24
        
        Args:
            plan_data: The insurance plan data to create
            
        Returns:
            InsurancePlan: The created insurance plan object
        """
        endpoint = self._build_endpoint()
        
        if isinstance(plan_data, dict):
            data = plan_data
        else:
            data = plan_data.model_dump(exclude_none=True, by_alias=True)
            
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, InsurancePlan)
    
    def update(
        self, 
        plan_num: Union[int, str], 
        plan_data: Union[UpdateInsurancePlanRequest, dict]
    ) -> InsurancePlan:
        """
        Update an existing insurance plan.
        
        Version Added: 22.3.30
        
        Args:
            plan_num: The plan number (PlanNum)
            plan_data: The insurance plan data to update
            
        Returns:
            InsurancePlan: The updated insurance plan object
        """
        plan_num = self._validate_id(plan_num)
        endpoint = self._build_endpoint(plan_num)
        
        if isinstance(plan_data, dict):
            data = plan_data
        else:
            data = plan_data.model_dump(exclude_none=True, by_alias=True)
            
        response = self._put(endpoint, json_data=data)
        return self._handle_response(response, InsurancePlan)
    
    def delete(self, plan_num: Union[int, str]) -> bool:
        """
        Delete an insurance plan.
        
        Note: The API documentation does not explicitly define a DELETE endpoint.
        This method is included for completeness but may not be supported.
        
        Args:
            plan_num: The plan number (PlanNum)
            
        Returns:
            bool: True if deletion was successful
        """
        plan_num = self._validate_id(plan_num)
        endpoint = self._build_endpoint(plan_num)
        response = self._delete(endpoint)
        return response is None or response.get("success", True)
    
    def get_by_carrier(self, carrier_num: int) -> List[InsurancePlan]:
        """
        Get insurance plans for a specific carrier.
        
        Args:
            carrier_num: Carrier number (FK to carrier.CarrierNum)
            
        Returns:
            List[InsurancePlan]: List of insurance plans for the carrier
        """
        result = self.list(carrier_num=carrier_num)
        return result.plans
    
    def get_by_plan_type(self, plan_type: str) -> List[InsurancePlan]:
        """
        Get insurance plans by plan type.
        
        Args:
            plan_type: Plan type. One of: "" (Percentage), "p" (PPO), "f" (Flat Copay), "c" (Capitation)
            
        Returns:
            List[InsurancePlan]: List of insurance plans with matching type
        """
        result = self.list(plan_type=plan_type)
        return result.plans
    
    def hide_plan(self, plan_num: Union[int, str]) -> InsurancePlan:
        """
        Hide an insurance plan.
        
        Args:
            plan_num: The plan number (PlanNum)
            
        Returns:
            InsurancePlan: The updated insurance plan object
        """
        update_data = UpdateInsurancePlanRequest(is_hidden="true")
        return self.update(plan_num, update_data)
    
    def unhide_plan(self, plan_num: Union[int, str]) -> InsurancePlan:
        """
        Unhide an insurance plan.
        
        Args:
            plan_num: The plan number (PlanNum)
            
        Returns:
            InsurancePlan: The updated insurance plan object
        """
        update_data = UpdateInsurancePlanRequest(is_hidden="false")
        return self.update(plan_num, update_data)
    
    def update_plan_note(self, plan_num: Union[int, str], note: str) -> InsurancePlan:
        """
        Update the plan note for an insurance plan.
        
        Args:
            plan_num: The plan number (PlanNum)
            note: The new plan note text
            
        Returns:
            InsurancePlan: The updated insurance plan object
        """
        update_data = UpdateInsurancePlanRequest(plan_note=note)
        return self.update(plan_num, update_data)