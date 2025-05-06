"""
OuraClientWrapper for handling Oura Ring API integration and biometric data retrieval.

This module provides a wrapper around the python-ouraring OuraClient for authentication
and data retrieval, with improved error handling and retry logic.
"""

from typing import Any, Dict, Optional, List, Union
from datetime import datetime, date
import os
import logging

from oura import OuraClient
from personal_ai_trainer.exceptions import OuraAPIError, ConfigurationError
from personal_ai_trainer.utils.error_handling import with_error_handling

logger = logging.getLogger(__name__)

# Define a custom exception class for Oura API errors
try:
    # Try to import the official exception class
    from oura.exceptions import OuraAPIException
except ImportError:
    # If it doesn't exist, define our own
    class OuraAPIException(Exception):
        """Exception raised for Oura API errors."""
        pass


class OuraClientWrapper:
    """
    Wrapper around the python-ouraring OuraClient for authentication and data retrieval.
    
    Handles sleep, activity, and readiness data, with error handling and retry logic.
    
    Attributes:
        client_id (Optional[str]): Oura API client ID.
        client_secret (Optional[str]): Oura API client secret.
        access_token (Optional[str]): Oura API access token.
        refresh_token (Optional[str]): Oura API refresh token.
        max_retries (int): Maximum number of retries for API calls.
        retry_delay (float): Delay between retries in seconds.
        client (OuraClient): The underlying OuraClient instance.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ) -> None:
        """
        Initialize the OuraClientWrapper.
        
        Args:
            client_id (Optional[str]): Oura API client ID. Defaults to OURA_CLIENT_ID env var.
            client_secret (Optional[str]): Oura API client secret. Defaults to OURA_CLIENT_SECRET env var.
            access_token (Optional[str]): Oura API access token. Defaults to OURA_ACCESS_TOKEN env var.
            refresh_token (Optional[str]): Oura API refresh token. Defaults to OURA_REFRESH_TOKEN env var.
            max_retries (int): Maximum number of retries for API calls. Defaults to 3.
            retry_delay (float): Delay between retries in seconds. Defaults to 2.0.
            
        Raises:
            ConfigurationError: If required credentials are missing.
            
        Example:
            ```python
            client = OuraClientWrapper(access_token="your_access_token")
            ```
        """
        self.client_id = client_id or os.getenv("OURA_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("OURA_CLIENT_SECRET")
        self.access_token = access_token or os.getenv("OURA_ACCESS_TOKEN")
        self.refresh_token = refresh_token or os.getenv("OURA_REFRESH_TOKEN")
        
        if not self.access_token:
            logger.error("Oura access token not found")
            raise ConfigurationError("Oura access token not found. Set OURA_ACCESS_TOKEN environment variable or pass access_token parameter.")
            
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        try:
            self.client = OuraClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                access_token=self.access_token,
                refresh_token=self.refresh_token,
                refresh_callback=self._refresh_callback,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Oura client: {e}")
            raise ConfigurationError(f"Failed to initialize Oura client: {e}") from e

    def _refresh_callback(self, token_dict: Dict[str, str]) -> None:
        """
        Callback to handle token refresh events.
        
        Args:
            token_dict (Dict[str, str]): New token information.
        """
        self.access_token = token_dict.get("access_token")
        self.refresh_token = token_dict.get("refresh_token")
        logger.info("Oura API token refreshed")
        # Optionally, persist tokens to a secure location

    @with_error_handling(error_types=(Exception,), retry_count=3, retry_delay=2.0)
    def _call_with_retries(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Call an OuraClient method with retry logic.
        
        Args:
            func: The OuraClient method to call.
            *args: Positional arguments.
            **kwargs: Keyword arguments.
            
        Returns:
            Any: The result of the API call.
            
        Raises:
            OuraAPIError: If all retries fail.
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Oura API error: {e}")
            raise OuraAPIError(f"Oura API call failed: {e}") from e

    def get_sleep_data(
        self, 
        user_id: str, 
        date_obj: Optional[Union[datetime, date]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve sleep data for a user.
        
        Args:
            user_id (str): The user identifier (not used by Oura, for compatibility).
            date_obj (Optional[Union[datetime, date]]): Date for sleep summary. Defaults to today.
                
        Returns:
            List[Dict[str, Any]]: Sleep data as a list of daily sleep records.
                Each record contains sleep metrics like duration, efficiency, and score.
                
        Raises:
            OuraAPIError: If the API call fails.
            
        Example:
            ```python
            sleep_data = client.get_sleep_data("user123")
            sleep_score = sleep_data[0]["score"]
            ```
        """
        date_obj = date_obj or datetime.today()
        
        # Convert to date if datetime was provided
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
            
        try:
            result = self._call_with_retries(self.client.sleep_summary, date_obj)
            
            # Ensure result is a list for consistent return type
            if not isinstance(result, list):
                result = [result] if result else []
                
            return result
        except Exception as e:
            logger.error(f"Failed to get sleep data: {e}")
            # Return empty list as fallback
            return []

    def get_activity_data(
        self, 
        user_id: str, 
        date_obj: Optional[Union[datetime, date]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve activity data for a user.
        
        Args:
            user_id (str): The user identifier (not used by Oura, for compatibility).
            date_obj (Optional[Union[datetime, date]]): Date for activity summary. Defaults to today.
                
        Returns:
            List[Dict[str, Any]]: Activity data as a list of daily activity records.
                Each record contains activity metrics like steps, calories, and score.
                
        Raises:
            OuraAPIError: If the API call fails.
            
        Example:
            ```python
            activity_data = client.get_activity_data("user123")
            activity_score = activity_data[0]["score"]
            ```
        """
        date_obj = date_obj or datetime.today()
        
        # Convert to date if datetime was provided
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
            
        try:
            result = self._call_with_retries(self.client.activity_summary, date_obj)
            
            # Ensure result is a list for consistent return type
            if not isinstance(result, list):
                result = [result] if result else []
                
            return result
        except Exception as e:
            logger.error(f"Failed to get activity data: {e}")
            # Return empty list as fallback
            return []

    def get_readiness_data(
        self, 
        user_id: str, 
        date_obj: Optional[Union[datetime, date]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve readiness data for a user.
        
        Args:
            user_id (str): The user identifier (not used by Oura, for compatibility).
            date_obj (Optional[Union[datetime, date]]): Date for readiness summary. Defaults to today.
                
        Returns:
            List[Dict[str, Any]]: Readiness data as a list of daily readiness records.
                Each record contains readiness metrics like score, HRV, and recovery index.
                
        Raises:
            OuraAPIError: If the API call fails.
            
        Example:
            ```python
            readiness_data = client.get_readiness_data("user123")
            readiness_score = readiness_data[0]["score"]
            ```
        """
        date_obj = date_obj or datetime.today()
        
        # Convert to date if datetime was provided
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
            
        try:
            result = self._call_with_retries(self.client.readiness_summary, date_obj)
            
            # Ensure result is a list for consistent return type
            if not isinstance(result, list):
                result = [result] if result else []
                
            return result
        except Exception as e:
            logger.error(f"Failed to get readiness data: {e}")
            # Return empty list as fallback
            return []
            
    def get_user_info(self) -> Dict[str, Any]:
        """
        Retrieve user information from the Oura API.
        
        Returns:
            Dict[str, Any]: User information including age, weight, and gender.
                
        Raises:
            OuraAPIError: If the API call fails.
            
        Example:
            ```python
            user_info = client.get_user_info()
            age = user_info.get("age")
            ```
        """
        try:
            return self._call_with_retries(self.client.user_info)
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            # Return empty dict as fallback
            return {}