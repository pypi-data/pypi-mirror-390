import requests
from typing import Dict, Any, Optional, Union
from requests.exceptions import RequestException
from adxp_sdk.auth import BaseCredentials


class BaseFineTuningHub:
    """
    Base class for fine-tuning functionality with common authentication and HTTP handling.
    """

    def __init__(self, credentials: BaseCredentials, use_backend_ai: bool = False):
        """
        Initialize the finetuning hub object.

        Args:
            credentials: Authentication credentials (BaseCredentials)
            use_backend_ai: If True, use backend-ai endpoints (api/v1/backend-ai/finetuning/...)
                          If False, use standard endpoints (api/v1/finetuning/...)
        """
        self.credentials = credentials
        self.base_url = credentials.base_url
        self.headers = credentials.get_headers()
        self.use_backend_ai = use_backend_ai    
        
    def _get_endpoint(self, path: str) -> str:
        """
        Get the full endpoint URL based on use_backend_ai setting.
        
        Args:
            path: The API path (e.g., "trainings", "trainings/{id}/status")
            
        Returns:
            str: Full endpoint URL
        """
        if self.use_backend_ai:
            return f"{self.base_url}/api/v1/backend-ai/finetuning/{path}"
        else:
            return f"{self.base_url}/api/v1/finetuning/{path}"

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Form data for the request
            params: Query parameters
            json_data: JSON data for the request

        Returns:
            dict: API response data

        Raises:
            RequestException: If the API request fails
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method.upper() == "POST":
                if json_data:
                    response = requests.post(url, headers=self.headers, json=json_data, params=params)
                else:
                    response = requests.post(url, headers=self.headers, data=data, params=params)
            elif method.upper() == "PUT":
                if json_data:
                    response = requests.put(url, headers=self.headers, json=json_data, params=params)
                else:
                    response = requests.put(url, headers=self.headers, data=data, params=params)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise RequestException(f"API request failed: {str(e)}")

    def _validate_uuid(self, value: str, field_name: str) -> None:
        """
        Validate UUID format.

        Args:
            value: Value to validate
            field_name: Name of the field for error message

        Raises:
            ValueError: If value is not a valid UUID
        """
        from .utils import is_valid_uuid
        if not is_valid_uuid(value):
            raise ValueError(f"{field_name} must be a valid UUID")

    def _validate_required_fields(self, data: Dict[str, Any], required_fields: list) -> None:
        """
        Validate that all required fields are present in data.

        Args:
            data: Data dictionary to validate
            required_fields: List of required field names

        Raises:
            ValueError: If any required fields are missing
        """
        if not data or not isinstance(data, dict):
            raise ValueError("data must be a non-empty dictionary")
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

    def _validate_pagination_params(self, page: int = 1, size: int = 10) -> None:
        """
        Validate pagination parameters.

        Args:
            page: Page number
            size: Page size

        Raises:
            ValueError: If pagination parameters are invalid
        """
        if not isinstance(page, int) or page < 1:
            raise ValueError("page must be a positive integer")
        if not isinstance(size, int) or size < 1 or size > 100:
            raise ValueError("size must be a positive integer between 1 and 100")
