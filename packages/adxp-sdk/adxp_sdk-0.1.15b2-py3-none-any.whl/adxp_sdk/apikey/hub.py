import requests
from typing import Dict, Any, Optional, Union
from requests.exceptions import RequestException
from adxp_sdk.auth import TokenCredentials
from adxp_sdk.auth.credentials import Credentials


class AXApiKeyHub:
    """
    A class for providing API Key hub-related functionality.

    How to use:
        >>> hub = AXApiKeyHub(TokenCredentials(base_url="https://api.sktaip.com", username="user", password="pw", client_id="cid"))
        >>> apikeys = hub.list_apikeys()
        >>> new_key = hub.create_apikey({"gateway_type": "model", "is_master": True})
    """

    def __init__(
        self,
        credentials: Union[TokenCredentials, Credentials, None] = None,
        headers: Optional[Dict[str, str]] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the API Key hub object.

        Args:
            credentials: Authentication information (TokenCredentials or Credentials)
            headers: HTTP headers for authentication
            base_url: Base URL of the API
        """
        if credentials is not None:
            # Use Credentials object
            self.credentials = credentials
            self.base_url = credentials.base_url
            self.headers = credentials.get_headers()
        elif headers is not None and base_url is not None:
            # New mode: use headers and base_url directly
            self.credentials = None
            self.base_url = base_url
            self.headers = headers
        else:
            raise ValueError("Either credentials or (headers and base_url) must be provided")

    def _get_headers(self):
        """Get headers for API requests."""
        return self.headers

    def list_apikeys(self, page: int = 1, size: int = 10, sort: Optional[str] = None, 
                    filter: Optional[str] = None, search: Optional[str] = None) -> Dict[str, Any]:
        """
        List API Keys via GET /api/v1/apikeys
        
        Args:
            page: Page number
            size: Page size
            sort: Sort condition
            filter: Filter condition
            search: Search keyword
            
        Returns:
            dict: The API response containing list of API keys
        """
        try:
            url = f"{self.base_url}/api/v1/apikeys"
            params = {
                "page": page,
                "size": size,
                "sort": sort,
                "filter": filter,
                "search": search,
            }
            params = {k: v for k, v in params.items() if v is not None}
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise Exception(f"Failed to list API keys: {str(e)}")

    def create_apikey(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create API Key via POST /api/v1/apikeys
        
        Args:
            data: API key creation data
            
        Required fields:
            - gateway_type: Gateway type (model, agent, mcp)
            - is_master: Whether this is a master key
            - project_id: Project ID
            
        Returns:
            dict: The API response
        """
        try:
            url = f"{self.base_url}/api/v1/apikeys"
            response = requests.post(url, headers=self._get_headers(), json=data)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise Exception(f"Failed to create API key: {str(e)}")

    def update_apikey(self, api_key_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update API Key via PUT /api/v1/apikeys/{api_key_id}
        
        Args:
            api_key_id: API Key ID
            data: Update data
            
        Returns:
            dict: The API response
        """
        try:
            url = f"{self.base_url}/api/v1/apikeys/{api_key_id}"
            response = requests.put(url, headers=self._get_headers(), json=data)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise Exception(f"Failed to update API key: {str(e)}")
    
    def delete_apikey(self, api_key_id: str) -> Dict[str, Any]:
        """
        Delete API Key via DELETE /api/v1/apikeys/{api_key_id}
        
        Args:
            api_key_id: API Key ID
            
        Returns:
            dict: The API response
        """
        try:
            url = f"{self.base_url}/api/v1/apikeys/{api_key_id}"
            response = requests.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json() if response.text else {"message": "Deleted successfully"}
        except RequestException as e:
            raise Exception(f"Failed to delete API key: {str(e)}")

