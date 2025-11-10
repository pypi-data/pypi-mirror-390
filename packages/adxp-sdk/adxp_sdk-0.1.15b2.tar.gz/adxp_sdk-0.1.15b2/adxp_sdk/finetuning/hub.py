import requests
from typing import Dict, Any, Optional, Union, List
from requests.exceptions import RequestException
from adxp_sdk.auth import BaseCredentials
from .utils import is_valid_uuid
from .base_hub import BaseFineTuningHub
import os


class AXFineTuningHub(BaseFineTuningHub):
    """
    A class for providing fine-tuning-related functionality (job creation, monitoring, dataset management, etc).

    How to use:
        >>> hub = AXFineTuningHub(TokenCredentials(base_url="https://api.sktai.io", username="user", password="pw", project="project_name"))
        >>> response = hub.create_finetuning_job({"name": "my-job", ...})
        >>> all_jobs = hub.get_finetuning_jobs()
        >>> one_job = hub.get_finetuning_job_by_id("job_id")
        >>> hub.cancel_finetuning_job("job_id")
    """


    # ====================================================================
    # Fine-tuning Job
    # ====================================================================

    # [Fine-tuning Job] Create a new fine-tuning training
    def create_training(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new fine-tuning training via POST /api/v1/finetuning/trainings
        
        Args:
            training_data (Dict[str, Any]): Training creation data (TrainingCreate schema)
                Required fields:
                - name (str): Training name
                - dataset_ids (List[str]): List of dataset IDs(uuids) for training
                - base_model_id (str): Base model ID(uuid) for fine-tuning (You can get model_id from get_models())
                - trainer_id (str): Trainer ID(uuid) for the training
                - resource (Dict[str, Any]): Resource configuration (e.g., {"cpu_quota": 2, "mem_quota": 8, "gpu_quota": 1.0})
                    Note: cpu_quota, mem_quota must be integers; gpu_quota supports both int and float values
                - params (str): Training parameters in string format
                
                Optional fields:
                - id (str, optional): Training ID (UUID, auto-generated if not provided)
                - description (str, optional): Training description
                - envs (Dict[str, Any], optional): Environment variables
                - is_auto_model_creation (bool, optional): Auto model creation after training (default: false)
                - type (str, optional): Training type (e.g., "sft"(default), "dpo")
                - project_id (str, optional): Project ID(uuid)
                - policy (List[Dict], optional): Access policy configuration
                
                Example (Basic):
                {
                    "name": "My Custom Training",
                    "dataset_ids": ["55826063-33a9-4b69-aa2b-bba656d80e07"],
                    "base_model_id": "85d6295e-f02c-42ea-a55f-b298124ada01",
                    "trainer_id": "77a85f64-5717-4562-b3fc-2c963f66afa6",
                    "resource": {"cpu_quota": 2, "mem_quota": 8, "gpu_quota": 1.0},
                    "params": "use_lora = true\nnum_train_epochs = 1\nlearning_rate = 0.0001"
                }
                
                Example (Advanced with all options):
                {
                    "id": "custom-training-uuid",
                    "name": "Advanced Training",
                    "description": "Custom fine-tuning for specific use case",
                    "dataset_ids": ["55826063-33a9-4b69-aa2b-bba656d80e07", "012e3456-e89b-12d3-a456-426614174003"],
                    "base_model_id": "85d6295e-f02c-42ea-a55f-b298124ada01",
                    "trainer_id": "77a85f64-5717-4562-b3fc-2c963f66afa6",
                    "resource": {"cpu_quota": 4, "mem_quota": 16, "gpu_quota": 2.0},
                    "params": "use_lora = true\nnum_train_epochs = 3\nlearning_rate = 0.0001\nbatch_size = 4",
                    "is_auto_model_creation": true,
                    "type": "sft",
                    "project_id": "55826063-33a9-4b69-aa2b-bba656d80e07",
                    "policy": [{"scopes": ["GET", "POST", "PUT", "DELETE"], "policies": [{"type": "user", "logic": "POSITIVE", "names": ["admin", "trainer_user"]}], "logic": "POSITIVE", "decision_strategy": "UNANIMOUS", "cascade": false}]
                }

        Returns:
            dict: The API response containing created training data (TrainingRead schema)
                Structure:
                {
                    "id": "uuid",                    # Training ID (uuid)
                    "name": "string",                  # Training name
                    "description": "string",           # Training description
                    "status": "string",                # Current status (initialized, starting, training, trained, etc.)
                    "prev_status": "string",           # Previous status
                    "progress": {},                    # Progress information (e.g., {"percentage": 100})
                    "resource": {},                    # Resource configuration
                    "dataset_ids": ["uuid"],         # List of dataset IDs(uuids)
                    "base_model_id": "uuid",         # Base model ID(uuid)
                    "trainer_id": "uuid",            # Trainer ID(uuid)
                    "params": "string",                # Training parameters
                    "envs": {},                        # Environment variables
                    "is_auto_model_creation": bool,   # Auto model creation flag
                    "type": "string",                # Training type (e.g., "sft"(default), "dpo")
                    "project_id": "uuid",            # Project ID(uuid)
                    "task_id": "uuid",               # Task ID (may be null)
                    "created_at": "string",           # Creation timestamp
                    "updated_at": "string"            # Update timestamp
                }
            
        Raises:
            RequestException: If the API request fails with specific error messages:
                - 400 Bad Request: Private trainer requires uploaded script file
                - 404 Not Found: Trainer not found. Please use the registered trainer
                - 409 Conflict: Training ID already exists
                - 422 Validation error: Invalid training data format
                - 500 Internal Server Error: Failed to register training
            ValueError: If training_data is empty or invalid
        """
        try:
            # Validate training_data
            if not training_data or not isinstance(training_data, dict):
                raise ValueError("training_data must be a non-empty dictionary")
            
            # Validate required fields
            required_fields = ['name', 'dataset_ids', 'base_model_id', 'trainer_id', 'resource', 'params']
            missing_fields = [field for field in required_fields if field not in training_data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            # Validate dataset_ids is a list
            dataset_ids = training_data.get('dataset_ids')
            if not isinstance(dataset_ids, list) or not dataset_ids:
                raise ValueError("dataset_ids must be a non-empty list of strings")
            
            # Validate resource is a dict
            resource = training_data.get('resource')
            if not isinstance(resource, dict):
                raise ValueError("resource must be a dictionary")
            
            # Validate resource structure (actual API format)
            if 'cpu_quota' in resource or 'gpu_quota' in resource:
                # Actual API format: {"cpu_quota": 2, "mem_quota": 8, "gpu_quota": 1.0}
                if 'gpu_quota' in resource and not isinstance(resource.get('gpu_quota'), (int, float)):
                    raise ValueError("gpu_quota must be a number (int or float)")
                if 'cpu_quota' in resource and not isinstance(resource.get('cpu_quota'), int):
                    raise ValueError("cpu_quota must be an integer")
                if 'mem_quota' in resource and not isinstance(resource.get('mem_quota'), int):
                    raise ValueError("mem_quota must be an integer")
                if 'gpu_type' in resource and not isinstance(resource.get('gpu_type'), str):
                    raise ValueError("gpu_type must be a string")
            elif 'type' in resource and 'count' in resource:
                # Alternative format: {"type": "gpu", "count": 1}
                if not isinstance(resource.get('type'), str) or not isinstance(resource.get('count'), (int, float)):
                    raise ValueError("resource with 'type' and 'count' must have string type and numeric count")
            else:
                raise ValueError("resource must contain quota fields (cpu_quota, gpu_quota, etc.) or type/count fields")
            
            # Validate params is a string
            if not isinstance(training_data.get('params'), str):
                raise ValueError("params must be a string")
            
            # Validate optional fields if provided
            if 'id' in training_data and not isinstance(training_data.get('id'), str):
                raise ValueError("id must be a string (UUID)")
            
            if 'description' in training_data and not isinstance(training_data.get('description'), str):
                raise ValueError("description must be a string")
            
            if 'envs' in training_data and not isinstance(training_data.get('envs'), dict):
                raise ValueError("envs must be a dictionary")
            
            if 'is_auto_model_creation' in training_data and not isinstance(training_data.get('is_auto_model_creation'), bool):
                raise ValueError("is_auto_model_creation must be a boolean")
            
            if 'policy' in training_data and not isinstance(training_data.get('policy'), list):
                raise ValueError("policy must be a list")
            
            if 'type' in training_data and not isinstance(training_data.get('type'), str):
                raise ValueError("type must be a string")
            
            if 'project_id' in training_data and not isinstance(training_data.get('project_id'), str):
                raise ValueError("project_id must be a string")
            
            # Make API request
            try:
                result = self._make_request(
                    method="POST",
                    endpoint="/api/v1/finetuning/trainings",
                    json_data=training_data
                )
            except RequestException as e:
                # Handle specific server errors
                error_str = str(e)
                if "400" in error_str:
                    if "Private trainer requires uploaded script file" in error_str:
                        raise RequestException(
                            f"Bad request: {error_str}. "
                            f"Private trainer requires uploaded script file."
                        )
                    else:
                        raise RequestException(
                            f"Bad request: {error_str}. "
                            f"Please check your training_data format and required fields."
                        )
                elif "404" in error_str:
                    raise RequestException(
                        f"Not found: {error_str}. "
                        f"Trainer not found. Please use the registered trainer."
                    )
                elif "409" in error_str:
                    raise RequestException(
                        f"Conflict: {error_str}. "
                        f"Training ID already exists. Please use a different ID or omit it for auto-generation."
                    )
                elif "422" in error_str:
                    raise RequestException(
                        f"Validation error: {error_str}. "
                        f"Please check your training_data format and required fields."
                    )
                elif "500" in error_str:
                    raise RequestException(
                        f"Internal server error: {error_str}. "
                        f"Failed to register training. Please try again later."
                    )
                raise
            
            # Ensure response has expected structure
            if not isinstance(result, dict):
                raise RequestException("Invalid response format from API")
            
            # Validate response contains expected fields
            expected_fields = ['id', 'name', 'status', 'dataset_ids', 'base_model_id', 'trainer_id', 'resource', 'params', 'type', 'project_id']
            missing_response_fields = [field for field in expected_fields if field not in result]
            if missing_response_fields:
                raise RequestException(f"API response missing expected fields: {missing_response_fields}")
            
            # Validate critical fields
            if not result.get('id'):
                raise RequestException("API response missing training ID")
            
            if not result.get('name'):
                raise RequestException("API response missing training name")
            
            # Log successful creation
            training_id = result.get('id')
            training_name = result.get('name')
            training_status = result.get('status', 'unknown')
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to create training: {str(e)}")

    # [Fine-tuning Job] Retrieve all fine-tuning trainings
    def get_trainings(
        self,
        page: int = 1,
        size: int = 10,
        sort: str = None,
        filter: str = None,
        search: str = None,
        ids: str = None,
    ) -> Dict[str, Any]:
        """
        Retrieve all fine-tuning trainings via GET /api/v1/finetuning/trainings with optional query parameters.
        
        Args:
            page (int): Page number (default: 1)
            size (int): Items per page (default: 10)
            sort (str): Sort field and order (e.g., 'created_at,desc')
            filter (str): Filter string (e.g., 'status:running')
            search (str): Search keyword
            ids (str): Comma-separated list of training IDs(uuids)
            
        Returns:
            dict: The API response containing trainings data
            
        Raises:
            RequestException: If the API request fails
        """
        try:
            # Build query parameters
            params = {
                'page': page,
                'size': size
            }
            
            if sort:
                params['sort'] = sort
            if filter:
                params['filter'] = filter
            if search:
                params['search'] = search
            if ids:
                params['ids'] = ids
            
            # Make API request
            response = requests.get(
                self._get_endpoint("trainings"),
                headers=self.headers,
                params=params
            )
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to get trainings: {str(e)}")

    # [Fine-tuning Job] Retrieve a single fine-tuning training by ID
    def get_training_by_id(self, training_id: str) -> Dict[str, Any]:
        """
        Retrieve a single fine-tuning training by ID via GET /api/v1/finetuning/trainings/{training_id}
        
        Args:
            training_id (str): The training ID(uuid)
            
        Returns:
            dict: The API response containing training data
            
        Raises:
            RequestException: If the API request fails
            ValueError: If training_id is not a valid uuid
        """
        try:
            # Validate UUID format
            if not is_valid_uuid(training_id):
                raise ValueError(f"Invalid training_id format: {training_id}")
            
            # Make API request
            response = requests.get(
                self._get_endpoint(f"trainings/{training_id}"),
                headers=self.headers
            )
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to get training {training_id}: {str(e)}")

    # [Fine-tuning Job] Update a fine-tuning training
    def update_training(self, training_id: str, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a fine-tuning training via PUT /api/v1/finetuning/trainings/{training_id}
        
        Args:
            training_id (str): The training ID(uuid)
            training_data (Dict[str, Any]): Training update data (TrainingUpdate schema)
                Supported fields: (Please use only the fields you want to update)
                - name (str, optional): Training name
                - status (str, optional): Training status (initialized, starting, training, trained, error, etc.)
                - prev_status (str, optional): Previous status
                - progress (Dict[str, Any], optional): Progress information (e.g., {"percentage": 100})
                - resource (Dict[str, Any], optional): Resource configuration
                    Note: cpu_quota, mem_quota must be integers; gpu_quota supports both int and float values
                - dataset_ids (List[str], optional): List of dataset IDs(uuids)
                - base_model_id (str, optional): Base model ID(uuid)
                - params (str, optional): Training parameters
                - envs (Dict[str, Any], optional): Environment variables
                - description (str, optional): Training description
                - project_id (str, optional): Project ID(uuid)
                - task_id (str, optional): Task ID
                - trainer_id (str, optional): Trainer ID(uuid)
                - id (str, optional): Training ID (UUID)
                - is_auto_model_creation (bool, optional): Auto model creation after training
                - type (str, optional): Training type (e.g., "sft", "dpo")
                - policy (List[Dict], optional): Access policy configuration
                
                Example:
                {
                    "name": "updated_training_name",
                    "description": "Updated training description",
                    "status": "initialized",
                    "progress": {"percentage": 50},
                    "resource": {
                        "cpu_quota": 4,
                        "mem_quota": 16,
                        "gpu_quota": 1.0,
                        "gpu_type": "H100"
                    },
                    "dataset_ids": [
                        "2fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "e5826063-33a9-4b69-aa2b-bba656d80e07"
                    ],
                    "base_model_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "params": "[TrainingConfig]\nuse_lora = true\nnum_train_epochs = 1\nvalidation_split = 0.0\nlearning_rate = 0.0001\nbatch_size = 1",
                    "trainer_id": "77a85f64-5717-4562-b3fc-2c963f66afa6",
                    "project_id": "55826063-33a9-4b69-aa2b-bba656d80e07",
                    "is_auto_model_creation": true,
                    "type": "sft",
                    "policy": [{"scopes": ["GET", "POST"], "policies": [{"type": "user", "logic": "POSITIVE", "names": ["admin"]}], "logic": "POSITIVE", "decision_strategy": "UNANIMOUS", "cascade": false}]
                }
            
        Returns:
            dict: The API response containing updated training data (TrainingRead schema)
                Same structure as create_training response
            
        Raises:
            RequestException: If the API request fails
            ValueError: If training_id is not a valid UUID or training_data is invalid
        """
        try:
            # Validate UUID format
            if not is_valid_uuid(training_id):
                raise ValueError(f"Invalid training_id format: {training_id}")
            
            # Validate training_data
            if not training_data or not isinstance(training_data, dict):
                raise ValueError("training_data must be a non-empty dictionary")
            
            # Validate optional fields if provided
            if 'dataset_ids' in training_data:
                dataset_ids = training_data['dataset_ids']
                if not isinstance(dataset_ids, list):
                    raise ValueError("dataset_ids must be a list of strings")
            
            if 'resource' in training_data:
                resource = training_data['resource']
                if not isinstance(resource, dict):
                    raise ValueError("resource must be a dictionary")
                # Validate resource structure if provided
                if 'gpu_quota' in resource and not isinstance(resource.get('gpu_quota'), (int, float)):
                    raise ValueError("gpu_quota must be a number (int or float)")
                if 'cpu_quota' in resource and not isinstance(resource.get('cpu_quota'), int):
                    raise ValueError("cpu_quota must be an integer")
                if 'mem_quota' in resource and not isinstance(resource.get('mem_quota'), int):
                    raise ValueError("mem_quota must be an integer")
                if 'gpu_type' in resource and not isinstance(resource.get('gpu_type'), str):
                    raise ValueError("gpu_type must be a string")
            
            if 'params' in training_data and not isinstance(training_data.get('params'), str):
                raise ValueError("params must be a string")
            
            if 'progress' in training_data and not isinstance(training_data.get('progress'), dict):
                raise ValueError("progress must be a dictionary")
            
            if 'envs' in training_data and not isinstance(training_data.get('envs'), dict):
                raise ValueError("envs must be a dictionary")
            
            if 'id' in training_data and not isinstance(training_data.get('id'), str):
                raise ValueError("id must be a string (UUID)")
            
            if 'is_auto_model_creation' in training_data and not isinstance(training_data.get('is_auto_model_creation'), bool):
                raise ValueError("is_auto_model_creation must be a boolean")
            
            if 'type' in training_data and not isinstance(training_data.get('type'), str):
                raise ValueError("type must be a string")
            
            if 'policy' in training_data and not isinstance(training_data.get('policy'), list):
                raise ValueError("policy must be a list")
            
            # Prepare query parameters
            params = {}
            
            # Make API request
            try:
                result = self._make_request(
                    method="PUT",
                    endpoint=f"/api/v1/finetuning/trainings/{training_id}",
                    json_data=training_data,
                    params=params
                )
            except RequestException as e:
                # Handle specific server errors
                error_str = str(e)
                if "400" in error_str:
                    raise RequestException(
                        f"Bad request: {error_str}. "
                        f"Please check your training_data format and required fields."
                    )
                elif "404" in error_str:
                    raise RequestException(
                        f"Not found: {error_str}. "
                        f"Training not found. Please check the training_id."
                    )
                elif "409" in error_str:
                    raise RequestException(
                        f"Conflict: {error_str}. "
                        f"Training ID already exists. Please use a different ID."
                    )
                elif "422" in error_str:
                    raise RequestException(
                        f"Validation error: {error_str}. "
                        f"Please check your training_data format and field types."
                    )
                elif "500" in error_str:
                    raise RequestException(
                        f"Internal server error: {error_str}. "
                        f"Failed to update training. Please try again later."
                    )
                raise
            
            # Ensure response has expected structure
            if not isinstance(result, dict):
                raise RequestException("Invalid response format from API")
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to update training {training_id}: {str(e)}")

    # [Fine-tuning Job] Delete a fine-tuning training
    def delete_training(self, training_id: str) -> bool:
        """
        Delete a fine-tuning training via DELETE /api/v1/finetuning/trainings/{training_id}
        Note: This marks the training as deleted rather than permanently removing it.
        
        Args:
            training_id (str): The training ID(uuid)
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            RequestException: If the API request fails
            ValueError: If training_id is not a valid uuid
        """
        try:
            # Validate UUID format
            if not is_valid_uuid(training_id):
                raise ValueError(f"Invalid training_id format: {training_id}")
            
            # Make API request
            response = requests.delete(
                self._get_endpoint(f"trainings/{training_id}"),
                headers=self.headers
            )
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            # DELETE returns 204 (No Content) on success
            return True
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to delete training {training_id}: {str(e)}")

    # [Training] Cancel training
    def cancel_training(self, training_id: str) -> Dict[str, Any]:
        """
        Cancel a training via POST /api/v1/finetuning/trainings/{training_id}/cancel
        
        Args:
            training_id (str): The training ID(uuid)
            
        Returns:
            dict: The API response
            
        Raises:
            RequestException: If the API request fails
            ValueError: If training_id is not a valid uuid
        """
        if not is_valid_uuid(training_id):
            raise ValueError(f"Invalid training_id format: {training_id}")
        url = self._get_endpoint(f"trainings/{training_id}/cancel")
        try:
            response = requests.post(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Training not found: {training_id}")
            else:
                raise RuntimeError(f"Failed to cancel training: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to cancel training: {str(e)}")

    # [Training] Get training logs
    def get_training_logs(self, training_id: str, after: str = None, limit: int = 100) -> Dict[str, Any]:
        """
        Get training logs via GET /api/v1/finetuning/trainings/{training_id}/logs
        
        Args:
            training_id (str): The training ID(uuid)
            after (str, optional): Log start point
            limit (int): Log count limit (default: 100)
            
        Returns:
            dict: The API response
            
        Raises:
            RequestException: If the API request fails
            ValueError: If training_id is not a valid uuid
        """
        if not is_valid_uuid(training_id):
            raise ValueError(f"Invalid training_id format: {training_id}")
        url = self._get_endpoint(f"trainings/{training_id}/logs")
        params = {"limit": limit}
        if after:
            params["after"] = after
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Training not found: {training_id}")
            else:
                raise RuntimeError(f"Failed to get training logs: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get training logs: {str(e)}")

    # [Training] Force stop training
    def force_stop_training(self, training_id: str) -> Dict[str, Any]:
        """
        Force stop a training via POST /api/v1/finetuning/trainings/{training_id}/force-stop
        
        Args:
            training_id (str): The training ID(uuid)
            
        Returns:
            dict: The API response
            
        Raises:
            RequestException: If the API request fails
            ValueError: If training_id is not a valid uuid
        """
        if not is_valid_uuid(training_id):
            raise ValueError(f"Invalid training_id format: {training_id}")
        url = self._get_endpoint(f"trainings/{training_id}/force-stop")
        try:
            response = requests.post(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Training not found: {training_id}")
            else:
                raise RuntimeError(f"Failed to force stop training: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to force stop training: {str(e)}")

    # [Fine-tuning Job] Get training status
    def get_training_status(self, training_id: str) -> Dict[str, Any]:
        """
        Get the specified training status via GET /api/v1/finetuning/trainings/{training_id}/status
        
        Args:
            training_id (str): The training ID(uuid)
            
        Returns:
            dict: The API response containing training status data (TrainingStatusRead schema)
            
        Raises:
            RequestException: If the API request fails
            ValueError: If training_id is not a valid uuid
        """
        try:
            # Validate UUID format
            if not is_valid_uuid(training_id):
                raise ValueError(f"Invalid training_id format: {training_id}")
            
            # Make API request
            response = requests.get(
                f"{self.base_url}/api/v1/finetuning/trainings/{training_id}/status",
                headers=self.headers
            )
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to get training status for {training_id}: {str(e)}")

    # [Fine-tuning Job] Start training
    def start_training(self, training_id: str) -> Dict[str, Any]:
        """
        Start a fine-tuning training by updating its status to 'starting'
        
        Args:
            training_id (str): The training ID(uuid)
            
        Returns:
            dict: The API response after starting the training
            
        Raises:
            ValueError: If training cannot be started in current state (initialized, stopped, error)
            RequestException: If the API request fails
        """
        try:
            # Validate UUID format
            if not is_valid_uuid(training_id):
                raise ValueError(f"Invalid training_id format: {training_id}")
            
            # 1. 현재 상태 확인
            current_status = self.get_training_status(training_id)
            current_status_value = current_status.get('status')
            
            # 2. 시작 가능한 상태인지 확인
            startable_statuses = ['initialized', 'stopped', 'error']
            if current_status_value not in startable_statuses:
                raise ValueError(
                    f"Cannot start training {training_id}. "
                    f"Current status: {current_status_value}. "
                    f"Startable statuses: {startable_statuses}"
                )
            
            # 3. Training 시작 - status를 'starting'으로 업데이트
            update_data = {'status': 'starting'}
            response = self.update_training(training_id, update_data)
            
            return response
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to start training {training_id}: {str(e)}")

    # [Fine-tuning Job] Stop training
    def stop_training(self, training_id: str) -> Dict[str, Any]:
        """
        Stop a fine-tuning training by updating its status to 'stopping'
        
        Args:
            training_id (str): The training ID(uuid)
            
        Returns:
            dict: The API response after stopping the training
            
        Raises:
            ValueError: If training cannot be stopped in current state (starting, resource_allocating, resource_allocated, training)
            RequestException: If the API request fails
        """
        try:
            # Validate UUID format
            if not is_valid_uuid(training_id):
                raise ValueError(f"Invalid training_id format: {training_id}")
            
            # 1. 현재 상태 확인
            current_status = self.get_training_status(training_id)
            current_status_value = current_status.get('status')
            
            # 2. 중지 가능한 상태인지 확인
            stoppable_statuses = ['starting', 'resource_allocating', 'resource_allocated', 'training']
            if current_status_value not in stoppable_statuses:
                raise ValueError(
                    f"Cannot stop training {training_id}. "
                    f"Current status: {current_status_value}. "
                    f"Stoppable statuses: {stoppable_statuses}"
                )
            
            # 3. Training 중지 - status를 'stopping'으로 업데이트
            update_data = {'status': 'stopping'}
            response = self.update_training(training_id, update_data)
            
            return response
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to stop training {training_id}: {str(e)}")

    # ====================================================================
    # Training Metrics
    # ====================================================================

    # [Training Events] Get training events
    def get_training_events(
        self,
        training_id: str,
        after: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Get the specified training's events via GET /api/v1/finetuning/trainings/{training_id}/events
        
        Args:
            training_id (str): The training ID(uuid)
            after (str, optional): Get events after this timestamp (ISO 8601 format, e.g., "2025-08-26T00:00:00.000Z")
            limit (int): Maximum number of events to return (default: 100, max: 1000)
            
        Returns:
            dict: The API response containing training events data (TrainingEventsRead schema)
            
        Raises:
            RequestException: If the API request fails
            ValueError: If training_id is not a valid uuid or limit is invalid
        """
        try:
            # Validate UUID format
            if not is_valid_uuid(training_id):
                raise ValueError(f"Invalid training_id format: {training_id}")
            
            # Validate limit
            if not isinstance(limit, int) or limit <= 0 or limit > 1000:
                raise ValueError(f"Limit must be an integer between 1 and 1000, got: {limit}")
            
            # Build query parameters
            params = {'limit': limit}
            if after:
                params['after'] = after
            
            # Make API request
            response = requests.get(
                f"{self.base_url}/api/v1/finetuning/trainings/{training_id}/events",
                headers=self.headers,
                params=params
            )
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to get training events for {training_id}: {str(e)}")

    # [Training Metrics] Get training metrics
    def get_training_metrics(
        self,
        training_id: str,
        type: str = "train",
        page: int = 1,
        size: int = 10,
    ) -> Dict[str, Any]:
        """
        Get the specified training's metrics via GET /api/v1/finetuning/trainings/{training_id}/metrics
        
        Args:
            training_id (str): The training ID (UUID)
            type (str): Metric type - "train", "evaluation", or "dpo" (default: "train")
            page (int): Page number for pagination (default: 1, minimum: 1)
            size (int): Items per page (default: 10, minimum: 1, maximum: 99999)
            
        Returns:
            dict: The API response containing training metrics data (TrainingMetricsRead schema)
                Structure:
                {
                    "data": [
                        {
                            "id": "f3839d47-addb-4c5e-b068-e59e3612ebc0",  # Metric ID
                            "step": 1,                                      # Training step number
                            "loss": 11.3924,                               # Loss value
                            "custom_metric": {                             # Custom metrics (can be null)
                                "accuracy": 0.9
                            },                          
                            "created_at": "2025-08-18T18:09:55.758662",    # Creation timestamp
                            "updated_at": "2025-08-18T18:09:55.758670"     # Update timestamp
                        },
                        {
                            "id": "d514ac9f-771b-4891-a787-242d6d77acd2",  # Metric ID
                            "step": 2,                                      # Training step number
                            "loss": 10.2186,                               # Loss value
                            "custom_metric": {                             # Custom metrics (can be null)
                                "accuracy": 0.9
                            },                           
                            "created_at": "2025-08-18T18:09:55.758662",    # Creation timestamp
                            "updated_at": "2025-08-18T18:09:55.758670"     # Update timestamp
                        }
                    ],
                    "payload": {
                        "pagination": {
                            "page": 1,                                     # Current page
                            "items_per_page": 10,                          # Items per page
                            "total": 231,                                  # Total number of metrics
                            "last_page": 24,                               # Total pages
                            "from_": 1,                                    # First item index
                            "to": 10,                                      # Last item index
                            "first_page_url": "/trainings/.../metrics?page=1&size=10",
                            "last_page_url": "/trainings/.../metrics?page=24&size=10",
                            "next_page_url": "/trainings/.../metrics?page=2&size=10",
                            "prev_page_url": null,
                            "links": [...]                                 # Pagination links
                        }
                    }
                }
            
        Raises:
            RequestException: If the API request fails
            ValueError: If parameters are invalid
        """
        try:
            # Validate UUID format
            if not is_valid_uuid(training_id):
                raise ValueError(f"Invalid training_id format: {training_id}")
            
            # Validate type parameter
            valid_types = ["train", "evaluation", "dpo"]
            if type not in valid_types:
                raise ValueError(f"Invalid type '{type}'. Must be one of: {valid_types}")
            
            # Validate page parameter
            if not isinstance(page, int) or page < 1:
                raise ValueError("page must be a positive integer")
            
            # Validate size parameter
            if not isinstance(size, int) or size < 1 or size > 99999:
                raise ValueError("size must be an integer between 1 and 99999")
            
            # Build query parameters
            params = {
                'type': type,
                'page': page,
                'size': size
            }
            
            # Make API request
            response = requests.get(
                f"{self.base_url}/api/v1/finetuning/trainings/{training_id}/metrics",
                headers=self.headers,
                params=params
            )
            
            # Handle specific server errors
            if response.status_code == 422:
                try:
                    error_detail = response.json()
                    if "detail" in error_detail:
                        raise RequestException(
                            f"Validation error: {error_detail['detail']}. "
                            f"Please check your parameters (type, page, size)."
                        )
                except:
                    pass  # If we can't parse the error, fall through to generic error handling
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            # Parse and validate response
            result = response.json()
            
            # Ensure response has expected structure
            if not isinstance(result, dict):
                raise RequestException("Invalid response format from API")
            
            # Validate response contains expected fields
            expected_fields = ['data', 'payload']
            missing_fields = [field for field in expected_fields if field not in result]
            if missing_fields:
                raise RequestException(f"API response missing expected fields: {missing_fields}")
            
            # Validate data is a list
            if not isinstance(result.get('data'), list):
                raise RequestException("API response 'data' field must be a list")
            
            # Validate payload structure
            payload = result.get('payload')
            if not isinstance(payload, dict) or 'pagination' not in payload:
                raise RequestException("API response 'payload' field must contain 'pagination'")
            
            # Validate pagination structure
            pagination = payload.get('pagination')
            expected_pagination_fields = ['page', 'items_per_page', 'total', 'last_page']
            missing_pagination_fields = [field for field in expected_pagination_fields if field not in pagination]
            if missing_pagination_fields:
                raise RequestException(f"API response pagination missing expected fields: {missing_pagination_fields}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to get training metrics for {training_id}: {str(e)}")

    # ====================================================================
    # Training Metrics Registration
    # ====================================================================

    # [Training Metrics] Register training metrics
    def register_training_metrics(
        self,
        training_id: str,
        metrics_data: List[Dict[str, Any]]
    ) -> bool:
        """
        Register training metrics via POST /api/v1/finetuning/trainings/{training_id}/metrics
        
        Args:
            training_id (str): The training ID (UUID)
            metrics_data (List[Dict[str, Any]]): List of metric data to register
                Each metric object should include:
                - step (int): Training step number
                - loss (float): Loss value for monitoring training progress
                - custom_metric (Dict[str, Any]): Custom metrics for performance analysis
                - type (str): Metric type - "train", "evaluation", or "dpo"
                
                Example:
                [
                    {
                        "step": 1,
                        "loss": 11.5,
                        "custom_metric": {
                            "accuracy": 0.9
                        },
                        "type": "train"
                    }
                ]
            
        Returns:
            bool: True if registration was successful (204 No Content response)
            
        Raises:
            RequestException: If the API request fails
            ValueError: If training_id is not a valid UUID or metrics_data is invalid
        """
        try:
            # Validate UUID format
            if not is_valid_uuid(training_id):
                raise ValueError(f"Invalid training_id format: {training_id}")
            
            # Validate metrics_data
            if not metrics_data or not isinstance(metrics_data, list):
                raise ValueError("metrics_data must be a non-empty list")
            
            # Validate each metric object
            for i, metric in enumerate(metrics_data):
                if not isinstance(metric, dict):
                    raise ValueError(f"Metric at index {i} must be a dictionary")
                if 'step' not in metric or 'loss' not in metric:
                    raise ValueError(f"Metric at index {i} must contain 'step' and 'loss' fields")
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/api/v1/finetuning/trainings/{training_id}/metrics",
                headers=self.headers,
                json=metrics_data
            )
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            # 204 No Content indicates successful registration
            return True
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to register training metrics for {training_id}: {str(e)}")

    # ====================================================================
    # Trainers
    # ====================================================================

    # [Trainers] Get all trainers
    def get_trainers(
        self,
        page: int = 1,
        size: int = 10,
        sort: str = None,
        filter: str = None,
        search: str = None,
    ) -> Dict[str, Any]:
        """
        Get all trainers via GET /api/v1/finetuning/trainers with optional query parameters.
        
        Args:
            page (int): Page number (default: 1, minimum: 1)
            size (int): Items per page (default: 10, minimum: 1, maximum: 100)
            sort (str): Sort field and order (e.g., 'created_at,desc')
            filter (str): Filter string (e.g., 'status:active')
            search (str): Search keyword
            
        Returns:
            dict: The API response containing trainers data (TrainersRead schema)
                Structure:
                {
                    "data": [
                        {
                            "id": "11fb1694-f7dd-4546-ad32-78e73fe55d80",  # Trainer ID
                            "registry_url": "registry.example.com/trainer",  # Registry URL
                            "description": null,                              # Description (can be null)
                            "default_params": "[TrainingConfig]\\nuse_lora = true\\n...",  # Default parameters
                            "created_at": "2025-07-29T12:58:35.164239",     # Creation timestamp
                            "updated_at": "2025-07-29T12:58:35.164244"      # Update timestamp
                        }
                    ],
                    "payload": {
                        "pagination": {
                            "page": 1,                                     # Current page
                            "items_per_page": 10,                          # Items per page
                            "total": 38,                                   # Total number of trainers
                            "last_page": 4,                                # Total pages
                            "from_": 1,                                    # First item index
                            "to": 10,                                      # Last item index
                            "first_page_url": "/trainers?page=1&size=10",
                            "last_page_url": "/trainers?page=4&size=10",
                            "next_page_url": "/trainers?page=2&size=10",
                            "prev_page_url": null,
                            "links": [...]                                 # Pagination links
                        }
                    }
                }
            
        Raises:
            RequestException: If the API request fails
            ValueError: If parameters are invalid
        """
        try:
            # Validate parameters
            if not isinstance(page, int) or page < 1:
                raise ValueError("page must be a positive integer")
            
            if not isinstance(size, int) or size < 1 or size > 100:
                raise ValueError("size must be an integer between 1 and 100")
            
            # Build query parameters
            params = {
                'page': page,
                'size': size
            }
            
            if sort:
                params['sort'] = sort
            if filter:
                params['filter'] = filter
            if search:
                params['search'] = search
            
            # Make API request
            response = requests.get(
                f"{self.base_url}/api/v1/finetuning/trainers",
                headers=self.headers,
                params=params
            )
            
            # Handle specific server errors
            if response.status_code == 422:
                try:
                    error_detail = response.json()
                    if "detail" in error_detail:
                        raise RequestException(
                            f"Validation error: {error_detail['detail']}. "
                            f"Please check your parameters (page, size, sort, filter, search)."
                        )
                except:
                    pass  # If we can't parse the error, fall through to generic error handling
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            # Parse and validate response
            result = response.json()
            
            # Ensure response has expected structure
            if not isinstance(result, dict):
                raise RequestException("Invalid response format from API")
            
            # Validate response contains expected fields
            expected_fields = ['data', 'payload']
            missing_fields = [field for field in expected_fields if field not in result]
            if missing_fields:
                raise RequestException(f"API response missing expected fields: {missing_fields}")
            
            # Validate data is a list
            if not isinstance(result.get('data'), list):
                raise RequestException("API response 'data' field must be a list")
            
            # Validate payload structure
            payload = result.get('payload')
            if not isinstance(payload, dict) or 'pagination' not in payload:
                raise RequestException("API response 'payload' field must contain 'pagination'")
            
            # Validate pagination structure
            pagination = payload.get('pagination')
            expected_pagination_fields = ['page', 'items_per_page', 'total', 'last_page']
            missing_pagination_fields = [field for field in expected_pagination_fields if field not in pagination]
            if missing_pagination_fields:
                raise RequestException(f"API response pagination missing expected fields: {missing_pagination_fields}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to get trainers: {str(e)}")

    # [Trainers] Get trainer by ID
    def get_trainer_by_id(self, trainer_id: str) -> Dict[str, Any]:
        """
        Get the specified trainer by ID via GET /api/v1/finetuning/trainers/{trainer_id}
        
        Args:
            trainer_id (str): The trainer ID (UUID)
            
        Returns:
            dict: The API response containing trainer data (TrainerRead schema)
                Structure:
                {
                    "id": "e79e4b00-8df4-46d2-a083-bd193a808607",        # Trainer ID
                    "registry_url": "registry.example.com/trainer",  # Registry URL
                    "description": null,                                    # Description (can be null)
                    "default_params": "[TrainingConfig]\\nuse_lora = true\\n...",  # Default parameters (can be null)
                    "created_at": "2025-07-29T12:57:38.316195",           # Creation timestamp
                    "updated_at": "2025-07-29T12:57:38.316203"            # Update timestamp
                }
            
        Raises:
            RequestException: If the API request fails
            ValueError: If trainer_id is not a valid UUID
        """
        try:
            # Validate UUID format
            if not is_valid_uuid(trainer_id):
                raise ValueError(f"Invalid trainer_id format: {trainer_id}")
            
            # Make API request
            response = requests.get(
                f"{self.base_url}/api/v1/finetuning/trainers/{trainer_id}",
                headers=self.headers
            )
            
            # Handle specific server errors
            if response.status_code == 404:
                raise RequestException(f"Trainer {trainer_id} not found")
            elif response.status_code == 422:
                try:
                    error_detail = response.json()
                    if "detail" in error_detail:
                        raise RequestException(
                            f"Validation error: {error_detail['detail']}. "
                            f"Please check your trainer_id format."
                        )
                except:
                    pass  # If we can't parse the error, fall through to generic error handling
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            # Parse and validate response
            result = response.json()
            
            # Ensure response has expected structure
            if not isinstance(result, dict):
                raise RequestException("Invalid response format from API")
            
            # Validate response contains expected fields
            expected_fields = ['id', 'registry_url', 'created_at', 'updated_at']
            missing_fields = [field for field in expected_fields if field not in result]
            if missing_fields:
                raise RequestException(f"API response missing expected fields: {missing_fields}")
            
            # Validate critical fields
            if not result.get('id'):
                raise RequestException("API response missing trainer ID")
            
            if not result.get('registry_url'):
                raise RequestException("API response missing registry URL")
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to get trainer {trainer_id}: {str(e)}")

    # [Trainers] Get platform information
    def get_platform_info(self) -> Dict[str, Any]:
        """
        Get platform information via GET /api/v1/finetuning/trainers/platform-info
        
        Returns:
            dict: The API response containing platform information
                Structure:
                {
                    "platform_type": "axp" | "backend_ai",  # Platform type
                    "base_url": "string"                     # AXP base URL (Backend.ai only)
                }
                
        Raises:
            RequestException: If the API request fails
        """
        try:
            result = self._make_request(
                method="GET",
                endpoint="/api/v1/finetuning/trainers/platform-info"
            )
            
            # Ensure response has expected structure
            if not isinstance(result, dict):
                raise RequestException("Invalid response format from API")
            
            # Validate response contains required fields
            if 'platform_type' not in result:
                raise RequestException("API response missing platform_type field")
            
            # Validate platform_type value
            valid_platform_types = ['axp', 'backend_ai']
            if result['platform_type'] not in valid_platform_types:
                raise RequestException(f"Invalid platform_type: {result['platform_type']}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to get platform info: {str(e)}")

    # [Trainers] Create a new trainer
    def create_trainer(self, trainer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new trainer via POST /api/v1/finetuning/trainers
        
        Args:
            trainer_data (Dict[str, Any]): Trainer creation data (TrainerCreate schema)
                Required:
                - registry_url (str): Docker image URL
                    Examples:
                    - AXP: "aip-harbor.sktai.io/sktai/trainer:latest"
                    - Backend.ai: "bai-repo:7080/bai/ngc-pytorch:24.12-pytorch2.6-py312-cuda12.6"
                
                Optional:
                - id (str, UUID): Trainer ID (auto-generated if not provided)
                - description (str): Trainer description
                - is_private (bool): Private trainer (default: False)
                - default_params (str): Default training parameters in TOML format
                    Example: "[TrainingConfig]\\nuse_lora = true\\nnum_train_epochs = 1\\nvalidation_split = 0.0\\nlearning_rate = 0.0001\\nbatch_size = 1"
                - policy (List[Dict]): Access policy configuration
                    Example: [{"scopes": ["GET", "POST", "PUT", "DELETE"], "policies": [{"type": "user", "logic": "POSITIVE", "names": ["admin"]}], "logic": "POSITIVE", "decision_strategy": "UNANIMOUS", "cascade": false}]

        Returns:
            dict: The API response containing created trainer data (TrainerRead schema)
                Structure:
                {
                    "id": "9fa466f2-996f-46bf-884a-e0d040330081",        # Trainer ID
                    "registry_url": "registry.example.com/trainer",        # Registry URL
                    "description": "This is a trainer description",         # Description (can be empty string)
                    "default_params": "[TrainingConfig]...",               # Default parameters (can be empty string)
                    "is_private": false,                                   # Private trainer flag
                    "created_at": "2025-09-16T16:34:01.352739",           # Creation timestamp
                    "updated_at": "2025-09-16T16:34:01.352746"            # Update timestamp
                }
            
        Raises:
            RequestException: If the API request fails
            ValueError: If trainer_data is empty or invalid
        """
        try:
            # Validate trainer_data
            if not trainer_data or not isinstance(trainer_data, dict):
                raise ValueError("trainer_data must be a non-empty dictionary")
            
            # Validate required fields (only registry_url is required)
            if 'registry_url' not in trainer_data:
                raise ValueError("registry_url is required")
            
            # Validate field types
            if not isinstance(trainer_data.get('registry_url'), str):
                raise ValueError("registry_url must be a string")
            
            # Validate optional fields
            if 'description' in trainer_data and not isinstance(trainer_data.get('description'), str):
                raise ValueError("description must be a string")
            
            if 'default_params' in trainer_data and not isinstance(trainer_data.get('default_params'), str):
                raise ValueError("default_params must be a string")
            
            if 'is_private' in trainer_data and not isinstance(trainer_data.get('is_private'), bool):
                raise ValueError("is_private must be a boolean")
            
            if 'id' in trainer_data and not isinstance(trainer_data.get('id'), str):
                raise ValueError("id must be a string (UUID)")
            
            if 'policy' in trainer_data and not isinstance(trainer_data.get('policy'), list):
                raise ValueError("policy must be a list")
            
            # Make API request
            try:
                result = self._make_request(
                    method="POST",
                    endpoint="/api/v1/finetuning/trainers",
                    json_data=trainer_data
                )
            except RequestException as e:
                # Handle specific server errors
                error_str = str(e)
                if "400" in error_str:
                    raise RequestException(
                        f"Bad request: {error_str}. "
                        f"Please check that registry_url is provided and valid."
                    )
                elif "409" in error_str:
                    raise RequestException(
                        f"Conflict: {error_str}. "
                        f"Trainer ID already exists. Please use a different ID or omit it for auto-generation."
                    )
                elif "422" in error_str:
                    raise RequestException(
                        f"Validation error: {error_str}. "
                        f"Please check your trainer_data format and required fields."
                    )
                raise
            
            # Ensure response has expected structure
            if not isinstance(result, dict):
                raise RequestException("Invalid response format from API")
            
            # Validate response contains expected fields
            expected_fields = ['id', 'registry_url', 'created_at', 'updated_at']
            missing_fields = [field for field in expected_fields if field not in result]
            if missing_fields:
                raise RequestException(f"API response missing expected fields: {missing_fields}")
            
            # Validate critical fields
            if not result.get('id'):
                raise RequestException("API response missing trainer ID")
            
            if not result.get('registry_url'):
                raise RequestException("API response missing registry URL")
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to create trainer: {str(e)}")

    # [Trainers] Update a trainer
    def update_trainer(self, trainer_id: str, trainer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a trainer via PUT /api/v1/finetuning/trainers/{trainer_id}
        
        Args:
            trainer_id (str): The trainer ID (UUID)
            trainer_data (Dict[str, Any]): Trainer update data (TrainerUpdate schema)
                Supported fields (all optional - only include fields you want to update):
                - registry_url (str, optional): Docker image URL (Example: aip-harbor.sktai.io/sktai/trainer:latest, bai-repo:7080/bai/ngc-pytorch:24.12-pytorch2.6-py312-cuda12.6)
                - description (str, optional): Trainer description
                - is_private (bool, optional): Private trainer flag
                - default_params (str, optional): Training configuration parameters in TOML format
                - policy (List[Dict], optional): Access policy configuration
                
                Example:
                {
                    "registry_url": "aip-harbor.sktai.io/sktai/trainer:latest",
                    "description": "Updated trainer description",
                    "is_private": true,
                    "default_params": "[TrainingConfig]\\nuse_lora = false\\nnum_train_epochs = 5",
                    "policy": [{"scopes": ["GET", "POST"], "policies": [{"type": "user", "logic": "POSITIVE", "names": ["admin"]}], "logic": "POSITIVE", "decision_strategy": "UNANIMOUS", "cascade": false}]
                }
            
        Returns:
            dict: The API response containing updated trainer data (TrainerRead schema)
                Structure:
                {
                    "id": "9fa466f2-996f-46bf-884a-e0d040330081",        # Trainer ID
                    "registry_url": "aip-harbor.sktai.io/sktai/trainer:latest",  # Updated registry URL
                    "description": "Updated description",                  # Updated description
                    "default_params": "[TrainingConfig]...",              # Updated default parameters
                    "is_private": true,                                   # Updated privacy flag
                    "created_at": "2025-09-16T16:34:01.352739",           # Creation timestamp
                    "updated_at": "2025-09-16T16:34:01.352746"            # Update timestamp
                }
            
        Raises:
            RequestException: If the API request fails
            ValueError: If trainer_id is not a valid UUID or trainer_data is invalid
        """
        try:
            # Validate UUID format
            if not is_valid_uuid(trainer_id):
                raise ValueError(f"Invalid trainer_id format: {trainer_id}")
            
            # Validate trainer_data
            if not trainer_data or not isinstance(trainer_data, dict):
                raise ValueError("trainer_data must be a non-empty dictionary")
            
            # Validate field types if provided
            if 'registry_url' in trainer_data and not isinstance(trainer_data.get('registry_url'), str):
                raise ValueError("registry_url must be a string")
            
            if 'description' in trainer_data and not isinstance(trainer_data.get('description'), str):
                raise ValueError("description must be a string")
            
            if 'is_private' in trainer_data and not isinstance(trainer_data.get('is_private'), bool):
                raise ValueError("is_private must be a boolean")
            
            if 'default_params' in trainer_data and not isinstance(trainer_data.get('default_params'), str):
                raise ValueError("default_params must be a string")
            
            if 'policy' in trainer_data and not isinstance(trainer_data.get('policy'), list):
                raise ValueError("policy must be a list")
            
            # Make API request
            response = requests.put(
                f"{self.base_url}/api/v1/finetuning/trainers/{trainer_id}",
                headers=self.headers,
                json=trainer_data
            )
            
            # Handle specific server errors
            if response.status_code == 404:
                raise RequestException(f"Trainer {trainer_id} not found")
            elif response.status_code == 422:
                try:
                    error_detail = response.json()
                    if "detail" in error_detail:
                        raise RequestException(
                            f"Validation error: {error_detail['detail']}. "
                            f"Please check your trainer_data format and field types."
                        )
                except:
                    pass  # If we can't parse the error, fall through to generic error handling
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            # Parse and validate response
            result = response.json()
            
            # Ensure response has expected structure
            if not isinstance(result, dict):
                raise RequestException("Invalid response format from API")
            
            # Validate response contains expected fields
            expected_fields = ['id', 'registry_url', 'created_at', 'updated_at']
            missing_fields = [field for field in expected_fields if field not in result]
            if missing_fields:
                raise RequestException(f"API response missing expected fields: {missing_fields}")
            
            # Validate critical fields
            if not result.get('id'):
                raise RequestException("API response missing trainer ID")
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to update trainer {trainer_id}: {str(e)}")

    # [Trainers] Delete a trainer
    def delete_trainer(self, trainer_id: str) -> bool:
        """
        Delete a trainer via DELETE /api/v1/finetuning/trainers/{trainer_id}
        Note: This marks the trainer as deleted rather than permanently removing it.
        
        Args:
            trainer_id (str): The trainer ID (UUID)
            
        Returns:
            Return 204 (No Content) on success
            
        Raises:
            RequestException: If the API request fails
            ValueError: If trainer_id is not a valid UUID
        """
        try:
            # Validate UUID format
            if not is_valid_uuid(trainer_id):
                raise ValueError(f"Invalid trainer_id format: {trainer_id}")
            
            # Make API request
            response = requests.delete(
                f"{self.base_url}/api/v1/finetuning/trainers/{trainer_id}",
                headers=self.headers
            )
            
            # Handle specific server errors
            if response.status_code == 404:
                raise RequestException(f"Trainer {trainer_id} not found")
            elif response.status_code == 422:
                try:
                    error_detail = response.json()
                    if "detail" in error_detail:
                        raise RequestException(
                            f"Validation error: {error_detail['detail']}. "
                            f"Please check your trainer_id format."
                        )
                except:
                    pass  # If we can't parse the error, fall through to generic error handling
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            # DELETE returns 204 (No Content) on success - no response body
            return True
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to delete trainer {trainer_id}: {str(e)}")

    # ====================================================================
    # Platform Type API
    # ====================================================================

    def get_platform_type(self) -> Dict[str, Any]:
        """
        Get platform type via GET /api/v1/finetuning/trainers/platform-type
        
        Returns:
            dict: The API response containing platform type information
                Structure:
                {
                    "platform_type": "backend_ai" or "axp",
                    "backend_ai_default_image": "nvcr.io/nvidia/pytorch:24.07-py3"
                }

        Raises:
            RequestException: If the API request fails
        """
        try:
            # Make API request
            result = self._make_request(
                method="GET",
                endpoint="/api/v1/finetuning/trainers/platform-type"
            )
            
            return result
            
        except RequestException:
            raise
        except Exception as e:
            raise RequestException(f"Failed to get platform type: {str(e)}")
