"""
Lineage SDK
Provides methods to query lineage relationships for any object (models, deployments, trainings, etc.)
"""

from typing import Dict, Any, List
import requests
from requests import RequestException
from adxp_sdk.auth.credentials import BaseCredentials


class LineageClient:
    """Client for querying lineage relationships"""
    
    def __init__(self, credentials: BaseCredentials, base_url: str):
        """
        Initialize LineageClient
        
        Args:
            credentials: Authentication credentials
            base_url: Base URL of the API
        """
        self.credentials = credentials
        self.base_url = base_url.rstrip('/')
        self.headers = credentials.get_headers()
    
    def get_lineage(
        self, 
        object_key: str, 
        direction: str, 
        action: str = "USE", 
        max_depth: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get lineage information for an object via GET /lineage/{object_key}/{direction}
        
        Args:
            object_key (str): The object key (UUID or name, e.g., model UUID, deployment name, training ID)
            direction (str): Traversal direction ('downstream' or 'upstream')
            action (str): Type of relationship to query ('USE' or 'CREATE') (default: "USE")
            max_depth (int): Maximum depth to traverse (default: 5, min: 1, max: 10)
            
        Returns:
            list: The API response containing lineage relationships (list of dicts)
                
        Example response:
            [
                {
                    "source_key": "0328b11c-291a-428b-b346-3c5a1c47c689",
                    "target_key": "66387e06-817b-4d4d-8ca1-e6b9383009f1",
                    "action": "USE",
                    "depth": 1,
                    "source_type": "KNOWLEDGE",
                    "target_type": "SERVING_MODEL"
                }
            ]
        
        Example usage:
            # Check downstream dependencies (what uses this object)
            downstream = client.get_lineage(
                object_key="model-uuid-123",
                direction="downstream",
                action="USE",
                max_depth=5
            )
            
            # Check upstream dependencies (what this object uses)
            upstream = client.get_lineage(
                object_key="model-uuid-123",
                direction="upstream",
                action="USE",
                max_depth=3
            )
        """
        # Validate direction
        if direction not in ["downstream", "upstream"]:
            raise ValueError(f"direction must be 'downstream' or 'upstream', got: {direction}")
        
        # Validate action
        if action not in ["USE", "CREATE"]:
            raise ValueError(f"action must be 'USE' or 'CREATE', got: {action}")
        
        # Validate max_depth
        if not isinstance(max_depth, int) or max_depth < 1 or max_depth > 10:
            raise ValueError(f"max_depth must be an integer between 1 and 10, got: {max_depth}")
        
        url = f"{self.base_url}/lineage/{object_key}/{direction}"
        params = {
            "action": action,
            "max_depth": max_depth
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise RequestException(f"Failed to get lineage: {str(e)}")

