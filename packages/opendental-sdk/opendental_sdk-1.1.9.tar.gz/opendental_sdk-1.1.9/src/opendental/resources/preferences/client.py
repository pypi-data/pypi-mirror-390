"""Preferences client for Open Dental SDK."""

import time
from typing import List, Optional, Union, Dict, Any
from ...base.resource import BaseResource
from .models import Preference, PreferenceListResponse


class PreferencesClient(BaseResource):
    """
    Client for managing system preferences in Open Dental.
    
    Preferences are system-wide settings (~1000 total) that control various
    aspects of Open Dental behavior. This API provides read-only access.
    
    Version Added: 21.1
    Reference: https://www.opendental.com/site/apipreferences.html
    """
    
    def __init__(self, client):
        """Initialize the preferences client."""
        super().__init__(client, "preferences")
    
    def get(self, pref_num: Union[int, str]) -> Preference:
        """
        Get a single preference by PrefNum.
        
        Args:
            pref_num: The preference number (primary key)
            
        Returns:
            Preference: The preference object
        """
        pref_num = self._validate_id(pref_num)
        endpoint = self._build_endpoint(pref_num)
        response = self._get(endpoint)
        return self._handle_response(response, Preference)
    
    def list(
        self, 
        pref_name: Optional[str] = None,
        offset: int = 0
    ) -> PreferenceListResponse:
        """
        List preferences with optional filtering.
        
        Without PrefName filter, returns all ~1000 preferences paginated.
        With PrefName filter, returns matching preferences.
        
        Args:
            pref_name: Optional. Filter by preference name
            offset: Starting record number (default 0)
            
        Returns:
            PreferenceListResponse: List of preferences
            
        Examples:
            # Get specific preference by name
            result = client.preferences.list(pref_name="RecallDaysPast")
            
            # Get preferences with pagination
            result = client.preferences.list(offset=200)
        """
        params: Dict[str, Any] = {}
        
        if pref_name is not None:
            params["PrefName"] = pref_name
        if offset > 0:
            params["Offset"] = offset
        
        endpoint = self._build_endpoint()
        response = self._get(endpoint, params=params)
        
        # API returns a list directly
        if isinstance(response, list):
            preferences = [Preference(**item) for item in response]
            return PreferenceListResponse(
                preferences=preferences,
                total=len(preferences),
                offset=offset
            )
        
        return PreferenceListResponse(preferences=[], total=0, offset=offset)
    
    def get_by_name(self, pref_name: str) -> Optional[Preference]:
        """
        Get a single preference by name.
        
        Args:
            pref_name: The preference name (e.g., "RecallDaysPast")
            
        Returns:
            Optional[Preference]: The preference if found, None otherwise
            
        Example:
            pref = client.preferences.get_by_name("RecallDaysPast")
            if pref:
                print(f"RecallDaysPast = {pref.value_string}")
        """
        result = self.list(pref_name=pref_name)
        if result.preferences:
            return result.preferences[0]
        return None
    
    def get_all(self, throttle_delay: float = 0.3) -> List[Preference]:
        """
        Get ALL preferences using Open Dental's pagination strategy.
        
        This retrieves all ~1000 system preferences by making multiple
        paginated requests.
        
        Strategy:
        1. First GET without offset (gets items 0-99)
        2. If exactly 100 items returned, continue with sequential GETs
        3. Stop when fewer than 100 items are returned
        
        Args:
            throttle_delay: Delay in seconds between requests (default 0.3s)
            
        Returns:
            List[Preference]: All preferences
            
        Example:
            all_prefs = client.preferences.get_all()
            print(f"Total preferences: {len(all_prefs)}")
        """
        all_preferences = []
        offset = 0
        
        while True:
            # Make request with current offset
            response = self.list(offset=offset)
            
            # Get preferences from response
            preferences = response.preferences
            
            # If no results returned, we're done
            if not preferences:
                break
            
            all_preferences.extend(preferences)
            
            # If we got fewer than 100 items, we've reached the end
            if len(preferences) < 100:
                break
            
            # Move to next batch (increment by 100)
            offset += 100
            
            # Throttle to prevent potential rate limiting
            if len(preferences) >= 100:  # Only delay if we're continuing
                time.sleep(throttle_delay)
            
            # Safety check to prevent infinite loops
            if offset > 10_000:  # Should have ~1000 prefs max
                break
        
        return all_preferences
    
    def search_by_pattern(self, pattern: str) -> List[Preference]:
        """
        Search for preferences by name pattern (case-insensitive).
        
        This is a client-side filter that fetches all preferences
        and filters by the pattern. Use sparingly as it fetches all ~1000.
        
        Args:
            pattern: Pattern to search for in preference names (case-insensitive)
            
        Returns:
            List[Preference]: Matching preferences
            
        Example:
            # Find all recall-related preferences
            recall_prefs = client.preferences.search_by_pattern("recall")
        """
        all_prefs = self.get_all()
        pattern_lower = pattern.lower()
        return [
            pref for pref in all_prefs 
            if pattern_lower in pref.pref_name.lower()
        ]
    
    def get_multiple_by_names(self, pref_names: List[str]) -> Dict[str, Optional[Preference]]:
        """
        Get multiple preferences by their names efficiently.
        
        Args:
            pref_names: List of preference names to retrieve
            
        Returns:
            Dict[str, Optional[Preference]]: Dictionary mapping names to preferences
            
        Example:
            prefs = client.preferences.get_multiple_by_names([
                "RecallDaysPast",
                "RecallDaysFuture",
                "PracticeDefaultBillType"
            ])
            print(prefs["RecallDaysPast"].value_string)
        """
        result = {}
        for pref_name in pref_names:
            result[pref_name] = self.get_by_name(pref_name)
        return result

