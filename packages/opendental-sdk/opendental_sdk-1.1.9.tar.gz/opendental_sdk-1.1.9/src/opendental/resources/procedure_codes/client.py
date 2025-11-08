"""procedurecodes client for Open Dental SDK."""

import time
from typing import List, Optional, Union, Dict, Any
from ...base.resource import BaseResource
from .models import (
    ProcedureCode,
    CreateProcedureCodeRequest,
    UpdateProcedureCodeRequest,
    ProcedureCodeListResponse,
    ProcedureCodeSearchRequest
)


class ProcedureCodesClient(BaseResource):
    """Client for managing procedure codes in Open Dental."""
    
    def __init__(self, client):
        """Initialize the procedure codes client."""
        super().__init__(client, "procedurecodes")
    
    def get(self, item_id: Union[int, str]) -> ProcedureCode:
        """Get a procedure code by ID."""
        item_id = self._validate_id(item_id)
        endpoint = self._build_endpoint(item_id)
        response = self._get(endpoint)
        return self._handle_response(response, ProcedureCode)
    
    def list(self, offset: int = 0, limit: Optional[int] = None) -> ProcedureCodeListResponse:
        """List procedure codes using offset-based pagination.
        
        Args:
            offset: Starting record number (default 0)
            limit: Maximum records to return (default None, API uses 100 max)
        """
        params = {"Offset": offset}
        if limit is not None:
            params["Limit"] = limit
        endpoint = self._build_endpoint()
        response = self._get(endpoint, params=params)
        
        if isinstance(response, dict):
            return ProcedureCodeListResponse(**response)
        elif isinstance(response, list):
            procedure_codes = [ProcedureCode(**item) for item in response]
            # Calculate page number from offset for backward compatibility
            page = (offset // 100) + 1
            return ProcedureCodeListResponse(
                procedure_codes=procedure_codes,
                total=len(procedure_codes), 
                page=page, 
                per_page=limit or 100
            )
        return ProcedureCodeListResponse(procedure_codes=[], total=0, page=1, per_page=limit or 100)
    
    def create(self, item_data: Union[CreateProcedureCodeRequest, Dict[str, Any]]) -> ProcedureCode:
        """Create a new procedure code."""
        endpoint = self._build_endpoint()
        if isinstance(item_data, CreateProcedureCodeRequest):
            data = item_data.model_dump()
        else:
            data = item_data
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, ProcedureCode)
    
    def update(self, item_id: Union[int, str], item_data: Union[UpdateProcedureCodeRequest, Dict[str, Any]]) -> ProcedureCode:
        """Update an existing procedure code."""
        item_id = self._validate_id(item_id)
        endpoint = self._build_endpoint(item_id)
        if isinstance(item_data, UpdateProcedureCodeRequest):
            data = item_data.model_dump()
        else:
            data = item_data
        response = self._put(endpoint, json_data=data)
        return self._handle_response(response, ProcedureCode)
    
    def delete(self, item_id: Union[int, str]) -> bool:
        """Delete a procedure code."""
        item_id = self._validate_id(item_id)
        endpoint = self._build_endpoint(item_id)
        response = self._delete(endpoint)
        return response is None or response.get("success", True)
    
    def get_all(self, throttle_delay: float = 0.3) -> List[ProcedureCode]:
        """Get ALL procedure codes using Open Dental's pagination strategy.
        
        Strategy:
        1. First GET without offset/limit (gets items 0-99)
        2. If exactly 100 items returned, continue with sequential GETs using offsets
        3. Stop when fewer than 100 items are returned
        
        Args:
            throttle_delay: Delay in seconds between requests to prevent rate limiting (default 0.1s)
        """
        all_procedure_codes = []
        offset = 0
        
        while True:
            # Make request with current offset (no limit = API default 100)
            response = self.list(offset=offset)
            
            # Get procedure codes from response
            procedure_codes = response.procedure_codes
            
            # If no results returned, we're done
            if not procedure_codes:
                break
            
            all_procedure_codes.extend(procedure_codes)
            
            # If we got fewer than 100 items, we've reached the end
            if len(procedure_codes) < 100:
                break
            
            # Move to next batch (increment by 100)
            offset += 100
            
            # Throttle to prevent potential rate limiting (skip delay on last request)
            if len(procedure_codes) >= 100:  # Only delay if we're continuing
                time.sleep(throttle_delay)
            
            # Safety check to prevent infinite loops
            if offset > 1_000_000:  # 1 million records max
                break
        
        return all_procedure_codes
    
    def search(self, search_params: Union[ProcedureCodeSearchRequest, Dict[str, Any]]) -> ProcedureCodeListResponse:
        """Search for procedure codes."""
        endpoint = self._build_endpoint("search")
        if isinstance(search_params, ProcedureCodeSearchRequest):
            params = search_params.model_dump()
        else:
            params = search_params
        response = self._get(endpoint, params=params)
        
        if isinstance(response, dict):
            return ProcedureCodeListResponse(**response)
        elif isinstance(response, list):
            return ProcedureCodeListResponse(
                procedure_codes=[ProcedureCode(**item) for item in response],
                total=len(response), 
                page=params.get('page', 1), 
                per_page=params.get('per_page', 100)
            )
        return ProcedureCodeListResponse(procedure_codes=[], total=0, page=1, per_page=100)
