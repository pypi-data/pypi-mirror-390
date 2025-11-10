import requests
from typing import Dict, Any, Optional, Union, List
from requests.exceptions import RequestException
from adxp_sdk.auth import BaseCredentials
from .utils import is_valid_uuid
import os


# Self-hosting 모델을 위한 기본 serving_params
DEFAULT_SERVING_PARAMS = {
    "inflight_quantization": False,
    "quantization": None,
    "dtype": "auto",
    "gpu_memory_utilization": 0.9,
    "load_format": "auto",
    "tensor_parallel_size": None,
    "cpu_offload_gb": 0,
    "enforce_eager": False,
    "max_model_len": None,
    "vllm_use_v1": "1",
    "max_num_seqs": None,
    "limit_mm_per_prompt": None,
    "tokenizer_mode": "auto",
    "config_format": "auto",
    "trust_remote_code": False,
    "hf_overrides": None,
    "mm_processor_kwargs": None,
    "disable_mm_preprocessor_cache": False,
    "enable_auto_tool_choice": False,
    "tool_call_parser": None,
    "tool_parser_plugin": None,
    "chat_template": None,
    "guided_decoding_backend": "auto",
    "enable_reasoning": False,
    "reasoning_parser": None,
    "device": None,
    "shm_size": None,
    "custom_serving": None
}


class AXModelHub:
    """
    A class for providing model hub-related functionality (model creation, retrieval, deletion, etc).

    How to use:
        >>> hub = AXModelHub(TokenCredentials(base_url="https://api.sktaip.com", username="user", password="pw", client_id="cid"))
        >>> response = hub.create_model({"name": "my-model", ...})
        >>> all_models = hub.get_models()
        >>> one_model = hub.get_model_by_id("model_id")
        >>> hub.delete_model("model_id")
    """

    def __init__(self, credentials: BaseCredentials, use_backend_ai: bool = False):
        """
        Initialize the model hub object.

        Args:
            credentials: Authentication credentials (BaseCredentials)
            use_backend_ai: If True, use backend-ai endpoints (api/v1/backend-ai/servings/...)
                          If False, use standard endpoints (api/v1/servings/...)
        """
        self.credentials = credentials
        self.base_url = credentials.base_url
        self.headers = credentials.get_headers()
        self.use_backend_ai = use_backend_ai

    # ====================================================================
    # Model
    # ====================================================================

    # [Model] Create a new model
    def create_model(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Create a new model via POST /api/v1/models
        For self-hosting models, automatically uploads the model file first.
        For serverless models, also creates a model endpoint if endpoint parameters are provided.
        For custom models (is_custom=True), also creates a custom runtime if custom_runtime_image_url is provided.

        Args:
            *args: If a single dict is provided, it will be used as model_data
            **kwargs: Model creation parameters

        Required Parameters:
            - name (str): Model name
            - type (str): Model type (one of the return values from get_model_types(), e.g., 'language', 'embedding', 'image', 'multimodal', 'reranker', 'stt', 'tts', 'audio', 'code', 'vision', 'video')
            - provider_id (str): Provider ID (one of the IDs returned by get_model_providers())
            - serving_type (str): Serving type (e.g., "serverless", "self-hosting")

        Conditionally Required:
            - path (str): Model file path (REQUIRED if serving_type="self-hosting")
            - endpoint_url (str): Endpoint URL (REQUIRED if serving_type="serverless")
            - endpoint_identifier (str): Endpoint identifier (REQUIRED if serving_type="serverless")
            - endpoint_key (str): Endpoint key (REQUIRED if serving_type="serverless")
            - endpoint_description (str): Endpoint description (OPTIONAL if serving_type="serverless")
            - custom_code_path (str): Custom code path (REQUIRED if is_custom=True)
            - custom_runtime_image_url (str): Custom runtime image URL (REQUIRED if is_custom=True)
            - custom_runtime_use_bash (bool): Whether to use bash for custom runtime (default: False) (OPTIONAL if is_custom=True)
            - custom_runtime_command (List[str]): Custom runtime command (OPTIONAL if is_custom=True)
            - custom_runtime_args (List[str]): Custom runtime arguments (OPTIONAL if is_custom=True)

        Optional Parameters:
            - display_name (str): Display name for the model
            - description (str): Model description
            - size (str): Model size (e.g., "34B")
            - token_size (str): Token size (e.g., "2048")
            - license (str): License information
            - readme (str): README content
            - tags (List[str]): List of tag names
            - languages (List[str]): List of language names
            - tasks (List[str]): List of task names
            - inference_param (Dict): Inference parameters
            - quantization (Dict): Quantization parameters
            - dtype (str): Data type
            - default_params (Dict): Default parameters
            - is_private (bool): Whether the model is private (default: False)
            - is_custom (bool): Whether the model is custom (default: False)

        Returns:
            dict: The API response

        Examples:
            # Dict style (recommended for dynamic data)
            model_data = {
                "display_name": "My Model",
                "name": "my_model",
                "type": "language",
                "serving_type": "serverless",
                "provider_id": "uuid-here"
            }
            result = hub.create_model(model_data)

            # Params style (recommended for IDE support)
            result = hub.create_model(
                display_name="My Model",
                name="my_model",
                type="language",
                serving_type="serverless",
                provider_id="uuid-here"
            )

            # Serverless model with endpoint
            hub.create_model(
                display_name="display_name_of_your_model",
                name="name_of_your_model",
                type="language",                            # REQUIRED (get from get_model_types())
                description="description of your model",
                serving_type="serverless",
                provider_id="3fa85f64-5717-4562-b3fc-2c963f66afa6", # REQUIRED (get from get_model_providers())
                languages=[{"name": "Korean"}],
                tasks=[{"name": "completion"}],
                tags=[{"name": "tag"}],
                endpoint_url="https://api.sktaip.com/v1",
                endpoint_identifier="openai/gpt-3.5-turbo",
                endpoint_key="key-1234567890"
            )

            # Self-hosting model
            hub.create_model(
                display_name="display_name_of_your_model",
                name="name_of_your_model",
                type="language",                            # REQUIRED (get from get_model_types())
                description="description of your model",
                serving_type="self-hosting",
                provider_id="3fa85f64-5717-4562-b3fc-2c963f66afa6", # REQUIRED (get from get_model_providers())
                languages=[{"name": "Korean"}],
                tasks=[{"name": "completion"}],
                tags=[{"name": "tag"}],
                path="/path/to/your-model.zip"
            )
            
            # Self-hosting model (Model custom serving)
            hub.create_model(
                display_name="display_name_of_your_model",
                name="name_of_your_model",
                type="language",                            # REQUIRED (get from get_model_types())
                description="description of your model",
                serving_type="self-hosting",
                provider_id="3fa85f64-5717-4562-b3fc-2c963f66afa6", # REQUIRED (get from get_model_providers())
                languages=[{"name": "Korean"}],
                tasks=[{"name": "completion"}],
                tags=[{"name": "tag"}],
                path="/path/to/your-model.zip",
                is_custom=True,
                custom_code_path="/path/to/your-code.zip",
                custom_runtime_image_url="https://hub.docker.com/r/adxpai/adxp-custom-runtime",
                custom_runtime_use_bash=False,
                custom_runtime_command=["/bin/bash", "-c"],
                custom_runtime_args=["uvicorn", "main:app"]
            )

        Note:
            - For self-hosting models, path is REQUIRED and will be automatically uploaded
            - For external models, path is NOT needed
            - All API fields are supported
            - Supports both dict style (create_model(model_data)) and params style (create_model(**model_data))
        """

        def _upload_model_file(file_path: str) -> str:
            """내부용: 모델 파일 업로드 후 temp_file_path 반환"""
            url = f"{self.base_url}/api/v1/models/files"
            try:
                with open(file_path, "rb") as f:
                    files = {"file": (os.path.basename(f.name), f, "application/octet-stream")}
                    response = requests.post(url, files=files, headers={k: v for k, v in self.headers.items() if k.lower() != "content-type"})
                if response.status_code in (200, 201):
                    resp_json = response.json()
                    return resp_json["temp_file_path"]
                elif response.status_code == 401:
                    raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
                else:
                    raise RuntimeError(f"Failed to upload model file: {response.status_code}, {response.text}")
            except FileNotFoundError:
                raise RuntimeError(f"File not found: {file_path}")
            except RequestException as e:
                raise RuntimeError(f"Failed to upload model file: {str(e)}")

        def _upload_custom_code_file(file_path: str) -> str:
            """내부용: 커스텀 코드 파일 업로드 후 temp_file_path 반환"""
            url = f"{self.base_url}/api/v1/custom-runtimes/code/files"
            try:
                with open(file_path, "rb") as f:
                    files = {"file": (os.path.basename(f.name), f, "application/octet-stream")}
                    response = requests.post(url, files=files, headers={k: v for k, v in self.headers.items() if k.lower() != "content-type"})
                if response.status_code in (200, 201):
                    resp_json = response.json()
                    return resp_json["temp_file_path"]
                elif response.status_code == 401:
                    raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
                elif response.status_code == 400:
                    raise RuntimeError(f"Bad request: {response.text}")
                else:
                    raise RuntimeError(f"Failed to upload custom code file: {response.status_code}, {response.text}")
            except FileNotFoundError:
                raise RuntimeError(f"File not found: {file_path}")
            except RequestException as e:
                raise RuntimeError(f"Failed to upload custom code file: {str(e)}")

        def _create_model_from_params(**kwargs) -> Dict[str, Any]:
            """
            Create model using parameter style.
            """
            # Validate required parameters
            if 'name' not in kwargs:
                raise ValueError("name is required")
            if 'type' not in kwargs:
                raise ValueError("type is required")

            model_type = kwargs['type']
            path = kwargs.get('path')

            # Validate that path is provided for self-hosting models
            if model_type == 'self-hosting' and not path:
                raise ValueError("path is required for self-hosting models")
            # custom_code_path 처리: is_custom=True일 때 반드시 필요
            if kwargs.get('is_custom') and not kwargs.get('custom_code_path'):
                raise ValueError('custom_code_path is required if is_custom=True')

            # Build model data
            data = {
                'name': kwargs['name'],
                'type': model_type,
                'description': kwargs.get('description', ''),
                'is_private': kwargs.get('is_private', False),
                'is_valid': kwargs.get('is_valid', True),
                'last_version': kwargs.get('last_version', 0),
                'is_custom': kwargs.get('is_custom', False)
            }

            # Optional fields
            optional_fields = [
                'display_name', 'size', 'token_size', 'dtype', 'serving_type',
                'license', 'readme', 'provider_id', 'project_id', 'custom_code_path'
            ]
            for field in optional_fields:
                if field in kwargs:
                    data[field] = kwargs[field]

            # Handle path
            if path:
                data['path'] = path

            # Handle JSON parameters
            json_fields = ['inference_param', 'quantization', 'default_params']
            for field in json_fields:
                if field in kwargs:
                    data[field] = kwargs[field]

            # Handle list fields
            list_fields = ['tags', 'languages', 'tasks']
            for field in list_fields:
                if field in kwargs:
                    values = kwargs[field]
                    if values:
                        data[field] = [{'name': item['name']} if isinstance(item, dict) else {'name': item} for item in values]

            return _create_model_from_dict(data)

        def _create_model_from_dict(model_data: Dict[str, Any]) -> Dict[str, Any]:
            """
            Create model using dict style (with automatic file upload for self-hosting models).
            """
            # custom_code_path 처리: is_custom=True일 때 반드시 필요
            if model_data.get('is_custom') and not model_data.get('custom_code_path'):
                raise ValueError('custom_code_path is required if is_custom=True')
            # path 처리: self-hosting일 때 반드시 필요
            if model_data.get('serving_type') == 'self-hosting' and not model_data.get('path'):
                raise ValueError('path is required for self-hosting models')

            # Handle list fields conversion (strings to objects)
            list_fields = ['tags', 'languages', 'tasks']
            for field in list_fields:
                if field in model_data:
                    values = model_data[field]
                    if values:
                        model_data[field] = [{'name': item['name']} if isinstance(item, dict) else {'name': item} for item in values]

            # Check if this is a self-hosting model that needs file upload
            serving_type = model_data.get('serving_type')
            if serving_type == 'self-hosting':
                path_value = model_data.get('path')
                if path_value and os.path.exists(path_value):
                    temp_file_path = _upload_model_file(path_value)
                    if temp_file_path:
                        model_data['path'] = temp_file_path
                    else:
                        raise RuntimeError("Failed to get temp_file_path from upload response")
            # custom_code_path 자동 업로드 처리 (is_custom=True)
            if model_data.get('is_custom') and model_data.get('custom_code_path'):
                code_path = model_data['custom_code_path']
                if os.path.exists(code_path):
                    temp_code_path = _upload_custom_code_file(code_path)
                    model_data['custom_code_path'] = temp_code_path
            url = f"{self.base_url}/api/v1/models"
            try:
                response = requests.post(url, json=model_data, headers=self.headers)
                if response.status_code in (200, 201):
                    model_result = response.json()
                elif response.status_code == 401:
                    raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
                elif response.status_code == 404:
                    raise RuntimeError(f"Endpoint not found: {url}")
                else:
                    raise RuntimeError(f"Failed to create model: {response.status_code}, {response.text}")
            except RequestException as e:
                raise RuntimeError(f"Failed to create model: {str(e)}")

            # Endpoint 자동 생성 로직
            endpoint_url = model_data.get('endpoint_url')
            endpoint_identifier = model_data.get('endpoint_identifier')
            endpoint_key = model_data.get('endpoint_key')
            endpoint_description = model_data.get('endpoint_description')

            endpoint_created = None
            if (
                serving_type == 'serverless' and
                endpoint_url and endpoint_identifier and endpoint_key
            ):
                # 모델 생성 결과에서 model_id 추출
                model_id = model_result.get('id') or model_result.get('model_id')
                if not model_id:
                    raise RuntimeError('Model creation did not return an id')
                endpoint_data = {
                    'url': endpoint_url,
                    'identifier': endpoint_identifier,
                    'key': endpoint_key,
                    'description': endpoint_description or ""
                }
                endpoint_created = self.create_model_endpoint(model_id, endpoint_data)
            # 결과에 endpoint 생성 결과 포함
            if endpoint_created is not None:
                return {
                    'model': model_result,
                    'endpoint': endpoint_created
                }
            else:
                return model_result

        def _create_custom_runtime(model_result, params):
            # 내부 유틸: 커스텀 런타임 자동 생성 (직접 HTTP 요청)
            if params.get('is_custom') and params.get('custom_runtime_image_url'):
                model_id = model_result.get('id') or model_result.get('model_id')
                if not model_id:
                    raise RuntimeError('Model creation did not return an id')
                custom_runtime_data = {
                    "model_id": model_id,
                    "image_url": params['custom_runtime_image_url'],
                    "use_bash": params.get('custom_runtime_use_bash', False)
                }
                if 'custom_runtime_command' in params:
                    custom_runtime_data['command'] = params['custom_runtime_command']
                if 'custom_runtime_args' in params:
                    custom_runtime_data['args'] = params['custom_runtime_args']
                url = f"{self.base_url}/api/v1/custom-runtimes"
                try:
                    response = requests.post(url, json=custom_runtime_data, headers=self.headers)
                    if response.status_code in (200, 201):
                        return response.json()
                    elif response.status_code == 401:
                        raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
                    elif response.status_code == 404:
                        raise RuntimeError("Model not found.")
                    elif response.status_code == 409:
                        raise RuntimeError("A custom runtime configuration for this model already exists.")
                    elif response.status_code == 400:
                        raise RuntimeError(f"Bad request: {response.text}")
                    else:
                        raise RuntimeError(f"Failed to create custom runtime: {response.status_code}, {response.text}")
                except RequestException as e:
                    raise RuntimeError(f"Failed to create custom runtime: {str(e)}")
            return None

        # Check if this is a dict-style call (single positional argument that is a dict)
        if len(args) == 1 and isinstance(args[0], dict):
            model_data = args[0].copy()
            # path 자동 업로드 처리 (self-hosting)
            if model_data.get('serving_type') == 'self-hosting' and model_data.get('path'):
                model_path = model_data['path']
                if os.path.exists(model_path):
                    model_data['path'] = _upload_model_file(model_path)
            # custom_code_path 자동 업로드 처리
            if model_data.get('is_custom') and model_data.get('custom_code_path'):
                code_path = model_data['custom_code_path']
                if os.path.exists(code_path):
                    model_data['custom_code_path'] = _upload_custom_code_file(code_path)
            model_result = _create_model_from_dict(model_data)
            # dict style: model_data에 커스텀 런타임 파라미터가 있으면 처리
            custom_runtime_result = _create_custom_runtime(
                model_result["model"] if (isinstance(model_result, dict) and "model" in model_result) else model_result,
                model_data
            )
            if custom_runtime_result is not None:
                # 결과에 custom_runtime 추가
                if isinstance(model_result, dict):
                    model_result["custom_runtime"] = custom_runtime_result
                else:
                    model_result = {"model": model_result, "custom_runtime": custom_runtime_result}
            return model_result
        elif len(args) > 0:
            raise ValueError("create_model() accepts either a single dict argument or keyword arguments")
        else:
            # path 자동 업로드 처리 (self-hosting)
            kwargs = kwargs.copy()
            if kwargs.get('serving_type') == 'self-hosting' and kwargs.get('path'):
                model_path = kwargs['path']
                if os.path.exists(model_path):
                    kwargs['path'] = _upload_model_file(model_path)
            # custom_code_path 자동 업로드 처리
            if kwargs.get('is_custom') and kwargs.get('custom_code_path'):
                code_path = kwargs['custom_code_path']
                if os.path.exists(code_path):
                    kwargs['custom_code_path'] = _upload_custom_code_file(code_path)
            # custom_code_path 처리: is_custom=True일 때 반드시 필요
            if kwargs.get('is_custom') and not kwargs.get('custom_code_path'):
                raise ValueError('custom_code_path is required if is_custom=True')
            # path 처리: self-hosting일 때 반드시 필요
            if kwargs.get('serving_type') == 'self-hosting' and not kwargs.get('path'):
                raise ValueError('path is required for self-hosting models')

            # 모델 생성
            model_result = _create_model_from_params(**kwargs)

            # Endpoint 자동 생성 로직
            serving_type = kwargs.get('serving_type')
            endpoint_url = kwargs.get('endpoint_url')
            endpoint_identifier = kwargs.get('endpoint_identifier')
            endpoint_key = kwargs.get('endpoint_key')
            endpoint_description = kwargs.get('endpoint_description')

            endpoint_created = None
            if (
                serving_type == 'serverless' and
                endpoint_url and endpoint_identifier and endpoint_key
            ):
                # 모델 생성 결과에서 model_id 추출
                model_id = model_result.get('id') or model_result.get('model_id')
                if not model_id:
                    raise RuntimeError('Model creation did not return an id')
                endpoint_data = {
                    'url': endpoint_url,
                    'identifier': endpoint_identifier,
                    'key': endpoint_key,
                    'description': endpoint_description or ""
                }
                endpoint_created = self.create_model_endpoint(model_id, endpoint_data)

            # 커스텀 런타임 자동 생성
            custom_runtime_result = _create_custom_runtime(model_result, kwargs)

            # 결과에 endpoint, custom_runtime 생성 결과 포함
            result = model_result
            if endpoint_created is not None:
                result = {
                    'model': model_result,
                    'endpoint': endpoint_created
                }
            if custom_runtime_result is not None:
                if isinstance(result, dict) and 'model' in result:
                    result['custom_runtime'] = custom_runtime_result
                else:
                    result = {'model': result, 'custom_runtime': custom_runtime_result}
            return result

    # [Model] Retrieve all models
    def get_models(
        self,
        page: int = 1,
        size: int = 10,
        sort: str = None,
        filter: str = None,
        search: str = None,
        ids: str = None,
    ) -> Dict[str, Any]:
        """
        Retrieve all models via GET /api/v1/models with optional query parameters.
        Args:
            page (int): Page number (default: 1)
            size (int): Items per page (default: 10)
            sort (str): Sort field and order (e.g., 'updated_at,desc')
            filter (str): Filter string (e.g., 'name:model_name' or 'tags[].name:abc')
            search (str): Search keyword
            ids (str): Comma-separated list of model IDs
        Returns:
            dict: The API response
        """
        url = f"{self.base_url}/api/v1/models"
        params = {"page": page, "size": size}
        if sort:
            params["sort"] = sort
        if filter:
            params["filter"] = filter
        if search:
            params["search"] = search
        if ids:
            params["ids"] = ids
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Endpoint not found: {url}")
            else:
                raise RuntimeError(f"Failed to get models: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get models: {str(e)}")

    # [Model] Retrieve a single model by ID (alias for get_model_by_id)
    def get_model(self, model_id: str) -> Dict[str, Any]:
        """
        Retrieve a single model by ID via GET /api/v1/models/{model_id}
        """
        return self.get_model_by_id(model_id)

    # [Model] Retrieve a single model by ID
    def get_model_by_id(self, model_id: str) -> Dict[str, Any]:
        """
        Retrieve a single model by ID via GET /api/v1/models/{model_id}
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to get model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model: {str(e)}")

    # [Model] Delete a model by ID
    def delete_model(self, model_id: str) -> Dict[str, Any]:
        """
        Delete a model by ID via DELETE /api/v1/models/{model_id}
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}"
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code in (200, 204):
                # Some APIs return 204 No Content, some return 200 with a body
                return response.json() if response.content else {"status": "deleted"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to delete model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to delete model: {str(e)}")

    # [Model-Type] Retrieve all model types
    def get_model_types(self) -> Dict[str, Any]:
        """
        Retrieve model types via GET /api/v1/models/types
        """
        url = f"{self.base_url}/api/v1/models/types"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            else:
                raise RuntimeError(f"Failed to get model types: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model types: {str(e)}")

    # [Model-Tag] Retrieve all model tags
    def get_model_tags(self) -> Dict[str, Any]:
        """
        Retrieve model tags via GET /api/v1/models/tags
        """
        url = f"{self.base_url}/api/v1/models/tags"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            else:
                raise RuntimeError(f"Failed to get model tags: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model tags: {str(e)}")

    # [Model] Recover a deleted model by ID
    def recover_model(self, model_id: str) -> Dict[str, Any]:
        """
        Recover a deleted model via PUT /api/v1/models/{model_id}/recovery
        Args:
            model_id (str): The model ID (UUID)
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/recovery"
        try:
            response = requests.put(url, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "recovered"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to recover model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to recover model: {str(e)}")

    # [Model] Upload a local LLM model file

    # [Model] Update a model by ID
    def update_model(self, model_id: str, model_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Update a model by ID via PUT /api/v1/models/{model_id}

        Args:
            model_id (str): The model ID (UUID)
            model_data (dict, optional): The model update payload (all fields optional)
            **kwargs: Model update parameters (params style)

        Returns:
            dict: The API response (updated model info)

        Examples:
            # Dict style
            update_model(model_id, {"description": "new desc"})
            # Params style
            update_model(model_id, description="new desc", display_name="new name")
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        # dict style
        if model_data is not None and isinstance(model_data, dict):
            update_payload = model_data.copy()
        else:
            update_payload = {}
        # params style
        if kwargs:
            update_payload.update(kwargs)
        if not update_payload:
            raise ValueError("No update data provided.")
        url = f"{self.base_url}/api/v1/models/{model_id}"
        try:
            response = requests.put(url, json=update_payload, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            elif response.status_code == 400:
                raise RuntimeError(f"Bad request: {response.text}")
            else:
                raise RuntimeError(f"Failed to update model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to update model: {str(e)}")

    # [Model] Add tags to model
    def add_tags_to_model(self, model_id: str, tags: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Add tags to a model via PUT /api/v1/models/{model_id}/tags
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/tags"
        try:
            response = requests.put(url, headers=self.headers, json=tags)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to add tags to model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to add tags to model: {str(e)}")

    # [Model] Remove tags from model
    def remove_tags_from_model(self, model_id: str, tags: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Remove tags from a model via DELETE /api/v1/models/{model_id}/tags
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/tags"
        try:
            response = requests.delete(url, headers=self.headers, json=tags)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to remove tags from model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to remove tags from model: {str(e)}")

    # ====================================================================
    # Model-Provider
    # ====================================================================

    # [Model-Provider] Create a new model provider
    def create_model_provider(self, provider_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Create a new model provider via POST /api/v1/models/providers

        Args:
            provider_data (dict, optional): Provider 생성에 필요한 데이터
            **kwargs: Provider 생성 파라미터 (params style)

        Returns:
            dict: The API response

        Examples:
            # Dict style
            create_model_provider({"name": "provider1", "description": "desc"})
            # Params style
            create_model_provider(name="provider1", description="desc")
        """
        # dict style
        if provider_data is not None and isinstance(provider_data, dict):
            payload = provider_data.copy()
        else:
            payload = {}
        # params style
        if kwargs:
            payload.update(kwargs)
        if not payload:
            raise ValueError("No provider data provided.")
        url = f"{self.base_url}/api/v1/models/providers"
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            if response.status_code in (200, 201):
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            else:
                raise RuntimeError(f"Failed to create model provider: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to create model provider: {str(e)}")

    # [Model-Provider] Retrieve all model providers
    def get_model_providers(
        self,
        page: int = 1,
        size: int = 10,
        sort: str = None,
        filter: str = None,
        search: str = None,
    ) -> Dict[str, Any]:
        """
        Retrieve all model providers via GET /api/v1/models/providers with optional query parameters.
        Args:
            page (int): Page number (default: 1)
            size (int): Items per page (default: 10)
            sort (str): Sort field and order (e.g., 'updated_at,desc')
            filter (str): Filter string (e.g., 'name:provider_name')
            search (str): Search keyword
        Returns:
            dict: The API response
        """
        url = f"{self.base_url}/api/v1/models/providers"
        params = {"page": page, "size": size}
        if sort:
            params["sort"] = sort
        if filter:
            params["filter"] = filter
        if search:
            params["search"] = search
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            else:
                raise RuntimeError(f"Failed to get model providers: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model providers: {str(e)}")

    # [Model-Provider] Retrieve a single model provider by ID
    def get_model_provider_by_id(self, provider_id: str) -> Dict[str, Any]:
        """
        Retrieve a single model provider by ID via GET /api/v1/models/providers/{provider_id}
        """
        if not is_valid_uuid(provider_id):
            raise ValueError(f"provider_id must be a valid UUID string, got: {provider_id}")
        url = f"{self.base_url}/api/v1/models/providers/{provider_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Provider not found: {provider_id}")
            else:
                raise RuntimeError(f"Failed to get model provider: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model provider: {str(e)}")

    # [Model-Provider] Update a model provider
    def update_model_provider(self, provider_id: str, provider_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Update a model provider via PUT /api/v1/models/providers/{provider_id}

        Args:
            provider_id (str): Provider의 UUID
            provider_data (dict, optional): Provider 수정 데이터 (dict 스타일)
            **kwargs: Provider 수정 파라미터 (params 스타일)
        Returns:
            dict: The API response
        Examples:
            # Dict style
            update_model_provider(provider_id, {"name": "new_name", "description": "desc"})
            # Params style
            update_model_provider(provider_id, name="new_name", description="desc")
        """
        if not is_valid_uuid(provider_id):
            raise ValueError(f"provider_id must be a valid UUID string, got: {provider_id}")
        # dict style
        if provider_data is not None and isinstance(provider_data, dict):
            payload = provider_data.copy()
        else:
            payload = {}
        # params style
        if kwargs:
            payload.update(kwargs)
        if not payload:
            raise ValueError("No provider update data provided.")
        url = f"{self.base_url}/api/v1/models/providers/{provider_id}"
        try:
            response = requests.put(url, json=payload, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "updated"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Provider not found: {provider_id}")
            else:
                raise RuntimeError(f"Failed to update model provider: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to update model provider: {str(e)}")

    # [Model-Provider] Delete a model provider
    def delete_model_provider(self, provider_id: str) -> Dict[str, Any]:
        """
        Delete a model provider via DELETE /api/v1/models/providers/{provider_id}
        """
        if not is_valid_uuid(provider_id):
            raise ValueError(f"provider_id must be a valid UUID string, got: {provider_id}")
        url = f"{self.base_url}/api/v1/models/providers/{provider_id}"
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "deleted"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Provider not found: {provider_id}")
            else:
                raise RuntimeError(f"Failed to delete model provider: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to delete model provider: {str(e)}")

    # ====================================================================
    # Model-Tag
    # ====================================================================

    # [Model] Add tags to a specific model
    def add_tags_to_model(self, model_id: str, tags: List[str]) -> Dict[str, Any]:
        """
        Add tags to a specific model via PUT /api/v1/models/{model_id}/tags
        Args:
            model_id (str): The model ID (UUID)
            tags (List[str]): List of tag names, e.g. ["tag1", "tag2"]
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")

        # Convert strings to objects
        converted_tags = [{'name': tag} for tag in tags]

        url = f"{self.base_url}/api/v1/models/{model_id}/tags"
        try:
            response = requests.put(url, json=converted_tags, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "tags added"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to add tags to model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to add tags to model: {str(e)}")

    # [Model] Remove tags from a specific model
    def remove_tags_from_model(self, model_id: str, tags: List[str]) -> Dict[str, Any]:
        """
        Remove tags from a specific model via DELETE /api/v1/models/{model_id}/tags
        Args:
            model_id (str): The model ID (UUID)
            tags (List[str]): List of tag names, e.g. ["tag1", "tag2"]
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")

        # Convert strings to objects
        converted_tags = [{'name': tag} for tag in tags]

        url = f"{self.base_url}/api/v1/models/{model_id}/tags"
        try:
            response = requests.delete(url, json=converted_tags, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "tags removed"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to remove tags from model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to remove tags from model: {str(e)}")

    # ====================================================================
    # Model-Language
    # ====================================================================

    # [Model] Add languages to a specific model
    def add_languages_to_model(self, model_id: str, languages: List[str]) -> Dict[str, Any]:
        """
        Add languages to a specific model via PUT /api/v1/models/{model_id}/languages
        Args:
            model_id (str): The model ID (UUID)
            languages (List[str]): List of language names, e.g. ["English", "Korean"]
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")

        # Convert strings to objects
        converted_languages = [{'name': language} for language in languages]

        url = f"{self.base_url}/api/v1/models/{model_id}/languages"
        try:
            response = requests.put(url, json=converted_languages, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "languages added"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to add languages to model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to add languages to model: {str(e)}")

    # [Model] Remove languages from a specific model
    def remove_languages_from_model(self, model_id: str, languages: List[str]) -> Dict[str, Any]:
        """
        Remove languages from a specific model via DELETE /api/v1/models/{model_id}/languages
        Args:
            model_id (str): The model ID (UUID)
            languages (List[str]): List of language names, e.g. ["English", "Korean"]
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")

        # Convert strings to objects
        converted_languages = [{'name': language} for language in languages]

        url = f"{self.base_url}/api/v1/models/{model_id}/languages"
        try:
            response = requests.delete(url, json=converted_languages, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "languages removed"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to remove languages from model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to remove languages from model: {str(e)}")

    # ====================================================================
    # Model-Task
    # ====================================================================

    # [Model] Add tasks to a specific model
    def add_tasks_to_model(self, model_id: str, tasks: List[str]) -> Dict[str, Any]:
        """
        Add tasks to a specific model via PUT /api/v1/models/{model_id}/tasks
        Args:
            model_id (str): The model ID (UUID)
            tasks (List[str]): List of task names, e.g. ["Completion", "Classification"]
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")

        # Convert strings to objects
        converted_tasks = [{'name': task} for task in tasks]

        url = f"{self.base_url}/api/v1/models/{model_id}/tasks"
        try:
            response = requests.put(url, json=converted_tasks, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "tasks added"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to add tasks to model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to add tasks to model: {str(e)}")

    # [Model] Remove tasks from a specific model
    def remove_tasks_from_model(self, model_id: str, tasks: List[str]) -> Dict[str, Any]:
        """
        Remove tasks from a specific model via DELETE /api/v1/models/{model_id}/tasks
        Args:
            model_id (str): The model ID (UUID)
            tasks (List[str]): List of task names, e.g. ["Completion", "Classification"]
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")

        # Convert strings to objects
        converted_tasks = [{'name': task} for task in tasks]

        url = f"{self.base_url}/api/v1/models/{model_id}/tasks"
        try:
            response = requests.delete(url, json=converted_tasks, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "tasks removed"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to remove tasks from model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to remove tasks from model: {str(e)}")

    # ====================================================================
    # Model-Version
    # ====================================================================

    # [Model-Version] Create a new version for a model
    def create_version(self, model_id: str, version_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Create a new version for a model via POST /api/v1/models/{model_id}/versions

        Args:
            model_id (str): The model ID (UUID)
            version_data (dict, optional): The version creation payload (dict style)
            **kwargs: Version creation parameters (params style)

        Required Parameters:
            - path (str): Server file path (already uploaded file path)

        Optional Parameters:
            - fine_tuning_id (str): Fine-tuning ID (UUID)
            - description (str): Version description
            - is_valid (bool): Whether the version is valid (default: True)
            - policy (List[Dict]): Access policy configuration

        Returns:
            dict: The API response (created version info)

        Examples:
            # Dict style
            version_data = {
                "path": "/server/path/to/model",
                "fine_tuning_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "description": "Version 1.0",
                "is_valid": True
            }
            result = hub.create_version(model_id, version_data)

            # Params style
            result = hub.create_version(
                model_id,
                fine_tuning_id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
                path="/server/path/to/model",
                description="Version 1.0",
                is_valid=True
            )

            # With policy
            result = hub.create_version(
                model_id,
                path="/server/path/to/model",
                description="Version with policy",
                policy=[{
                    "cascade": False,
                    "decision_strategy": "UNANIMOUS",
                    "logic": "POSITIVE",
                    "policies": [{
                        "logic": "POSITIVE",
                        "names": ["admin"],
                        "type": "user"
                    }],
                    "scopes": ["GET", "POST", "PUT", "DELETE"]
                }]
            )
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")

        # dict style
        if version_data is not None and isinstance(version_data, dict):
            payload = version_data.copy()
        else:
            payload = {}
        # params style
        if kwargs:
            payload.update(kwargs)
        if not payload:
            raise ValueError("No version data provided.")

        # Validate required parameters
        if 'path' not in payload:
            raise ValueError("path is required")

        # Set default values
        if 'is_valid' not in payload:
            payload['is_valid'] = True

        url = f"{self.base_url}/api/v1/models/{model_id}/versions"
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            if response.status_code in (200, 201):
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            elif response.status_code == 400:
                raise RuntimeError(f"Bad request: {response.text}")
            elif response.status_code == 409:
                raise RuntimeError(f"Version already exists: {response.text}")
            else:
                raise RuntimeError(f"Failed to create version: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to create version: {str(e)}")

    # [Model-Version] Retrieve versions of a model
    def get_model_versions(
        self,
        model_id: str,
        page: int = 1,
        size: int = 10,
        sort: str = None,
        filter: str = None,
        search: str = None,
        ids: str = None,
    ) -> Dict[str, Any]:
        """
        Retrieve versions of a model via GET /api/v1/models/{model_id}/versions with optional query parameters.
        Args:
            model_id (str): The model ID (UUID)
            page (int): Page number (default: 1)
            size (int): Items per page (default: 10)
            sort (str): Sort field and order (e.g., 'updated_at,desc')
            filter (str): Filter string (e.g., 'description:desc')
            search (str): Search keyword
            ids (str): Comma-separated list of version IDs
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/versions"
        params = {"page": page, "size": size}
        if sort:
            params["sort"] = sort
        if filter:
            params["filter"] = filter
        if search:
            params["search"] = search
        if ids:
            params["ids"] = ids
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to get model versions: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model versions: {str(e)}")

    # [Model-Version] Retrieve a specific version of a model
    def get_model_version_by_id(self, model_id: str, version_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific version of a model via GET /api/v1/models/{model_id}/versions/{version_id}
        Args:
            model_id (str): The model ID (UUID)
            version_id (str): The version ID (UUID)
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        if not is_valid_uuid(version_id):
            raise ValueError(f"version_id must be a valid UUID string, got: {version_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/versions/{version_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model or version not found: {model_id}, {version_id}")
            else:
                raise RuntimeError(f"Failed to get model version: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model version: {str(e)}")

    # [Model-Version] Retrieve a specific version by version_id only
    def get_version_by_id(self, version_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific version by version_id via GET /api/v1/models/versions/{version_id}
        Args:
            version_id (str): The version ID (UUID)
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(version_id):
            raise ValueError(f"version_id must be a valid UUID string, got: {version_id}")
        url = f"{self.base_url}/api/v1/models/versions/{version_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Version not found: {version_id}")
            else:
                raise RuntimeError(f"Failed to get version: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get version: {str(e)}")

    # [Model-Version] Delete a specific version of a model
    def delete_model_version_by_id(self, model_id: str, version_id: str) -> Dict[str, Any]:
        """
        Delete a specific version of a model via DELETE /api/v1/models/{model_id}/versions/{version_id}
        Args:
            model_id (str): The model ID (UUID)
            version_id (str): The version ID (UUID)
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        if not is_valid_uuid(version_id):
            raise ValueError(f"version_id must be a valid UUID string, got: {version_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/versions/{version_id}"
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "deleted"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model or version not found: {model_id}, {version_id}")
            else:
                raise RuntimeError(f"Failed to delete model version: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to delete model version: {str(e)}")

    # [Model-Version] Update a specific version of a model
    def update_model_version_by_id(self, model_id: str, version_id: str, version_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Update a specific version of a model via PUT /api/v1/models/{model_id}/versions/{version_id}
        Args:
            model_id (str): The model ID (UUID)
            version_id (str): The version ID (UUID)
            version_data (dict, optional): The version update payload (dict 스타일)
            **kwargs: 버전 업데이트 파라미터 (params 스타일)
        Returns:
            dict: The API response
        Examples:
            # Dict style
            update_model_version_by_id(model_id, version_id, {"description": "new desc"})
            # Params style
            update_model_version_by_id(model_id, version_id, description="new desc")
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        if not is_valid_uuid(version_id):
            raise ValueError(f"version_id must be a valid UUID string, got: {version_id}")
        # dict style
        if version_data is not None and isinstance(version_data, dict):
            payload = version_data.copy()
        else:
            payload = {}
        # params style
        if kwargs:
            payload.update(kwargs)
        if not payload:
            raise ValueError("No version update data provided.")
        url = f"{self.base_url}/api/v1/models/{model_id}/versions/{version_id}"
        try:
            response = requests.put(url, json=payload, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "updated"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model or version not found: {model_id}, {version_id}")
            else:
                raise RuntimeError(f"Failed to update model version: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to update model version: {str(e)}")

    # [Model-Version] Promote a specific version to a model
    def promote_version(self, version_id: str, promotion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Promote a specific version to a model via POST /api/v1/models/versions/{version_id}/promote
        Args:
            version_id (str): The version ID (UUID)
            promotion_data (dict): The promotion payload (e.g., {"display_name": ..., "description": ...})
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(version_id):
            raise ValueError(f"version_id must be a valid UUID string, got: {version_id}")
        url = f"{self.base_url}/api/v1/models/versions/{version_id}/promote"
        try:
            response = requests.put(url, json=promotion_data, headers=self.headers)
            if response.status_code in (200, 201):
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Version not found: {version_id}")
            else:
                raise RuntimeError(f"Failed to promote version: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to promote version: {str(e)}") 

    # ====================================================================
    # Model-Endpoint
    # ====================================================================

    # [Model-Endpoint] Register an endpoint for a specific model
    def create_model_endpoint(self, model_id: str, endpoint_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Register an endpoint for a specific model via POST /api/v1/models/{model_id}/endpoints
        Args:
            model_id (str): The model ID (UUID)
            endpoint_data (dict, optional): The endpoint registration payload (dict 스타일)
            **kwargs: 엔드포인트 등록 파라미터 (params 스타일)
        Returns:
            dict: The API response
        Examples:
            # Dict style
            create_model_endpoint(model_id, {"url": "...", "identifier": "...", "key": "..."})
            # Params style
            create_model_endpoint(model_id, url="...", identifier="...", key="...")
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        # dict style
        if endpoint_data is not None and isinstance(endpoint_data, dict):
            payload = endpoint_data.copy()
        else:
            payload = {}
        # params style
        if kwargs:
            payload.update(kwargs)
        if not payload:
            raise ValueError("No endpoint data provided.")
        url = f"{self.base_url}/api/v1/models/{model_id}/endpoints"
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            if response.status_code in (200, 201):
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to create model endpoint: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to create model endpoint: {str(e)}")

    # [Model-Endpoint] Retrieve multiple endpoints for a specific model
    def get_model_endpoints(
        self,
        model_id: str,
        page: int = 1,
        size: int = 10,
        sort: str = None,
        filter: str = None,
        search: str = None,
    ) -> Dict[str, Any]:
        """
        Retrieve multiple endpoints for a specific model via GET /api/v1/models/{model_id}/endpoints with optional query parameters.
        Args:
            model_id (str): The model ID (UUID)
            page (int): Page number (default: 1)
            size (int): Items per page (default: 10)
            sort (str): Sort field and order (e.g., 'updated_at,desc')
            filter (str): Filter string (e.g., 'description:desc')
            search (str): Search keyword
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/endpoints"
        params = {"page": page, "size": size}
        if sort:
            params["sort"] = sort
        if filter:
            params["filter"] = filter
        if search:
            params["search"] = search
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to get model endpoints: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model endpoints: {str(e)}")

    # [Model-Endpoint] Retrieve a single endpoint for a specific model
    def get_model_endpoint_by_id(self, model_id: str, endpoint_id: str) -> Dict[str, Any]:
        """
        Retrieve a single endpoint for a specific model via GET /api/v1/models/{model_id}/endpoints/{endpoint_id}
        Args:
            model_id (str): The model ID (UUID)
            endpoint_id (str): The endpoint ID (UUID)
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        if not is_valid_uuid(endpoint_id):
            raise ValueError(f"endpoint_id must be a valid UUID string, got: {endpoint_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/endpoints/{endpoint_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model or endpoint not found: {model_id}, {endpoint_id}")
            else:
                raise RuntimeError(f"Failed to get model endpoint: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model endpoint: {str(e)}")

    # [Model-Endpoint] Delete a single endpoint for a specific model
    def delete_model_endpoint_by_id(self, model_id: str, endpoint_id: str) -> Dict[str, Any]:
        """
        Delete a single endpoint for a specific model via DELETE /api/v1/models/{model_id}/endpoints/{endpoint_id}
        Args:
            model_id (str): The model ID (UUID)
            endpoint_id (str): The endpoint ID (UUID)
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        if not is_valid_uuid(endpoint_id):
            raise ValueError(f"endpoint_id must be a valid UUID string, got: {endpoint_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/endpoints/{endpoint_id}"
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "deleted"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model or endpoint not found: {model_id}, {endpoint_id}")
            else:
                raise RuntimeError(f"Failed to delete model endpoint: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to delete model endpoint: {str(e)}")

    # ====================================================================
    # Model-Custom-Runtime
    # ====================================================================
    # [Model-Custom-Runtime] Create a custom runtime for a specific model
    def create_custom_runtime(self, runtime_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a custom runtime configuration via POST /api/v1/custom-runtimes

        Args:
            runtime_data (dict): Custom runtime configuration data
                - model_id (str): The model ID (UUID)
                - image_url (str): Custom Docker image URL
                - use_bash (bool): Whether to use bash (default: False)
                - command (List[str]): Custom runtime command
                - args (List[str]): Custom runtime arguments

        Returns:
            dict: The API response (custom runtime info)
        """
        model_id = runtime_data.get('model_id')
        if not model_id or not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")

        url = f"{self.base_url}/api/v1/custom-runtimes"
        try:
            response = requests.post(url, headers=self.headers, json=runtime_data)
            if response.status_code == 201:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 400:
                raise RuntimeError(f"Invalid request data: {response.text}")
            elif response.status_code == 404:
                raise RuntimeError("Model not found.")
            else:
                raise RuntimeError(f"Failed to create custom runtime: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to create custom runtime: {str(e)}")

    # [Model-Custom-Runtime] Retrieve custom runtime for a specific model
    def get_custom_runtime_by_model(self, model_id: str) -> Dict[str, Any]:
        """
        Retrieve custom runtime configuration by model ID via GET /api/v1/custom-runtimes/model/{model_id}

        Args:
            model_id (str): The model ID (UUID)

        Returns:
            dict: The API response (custom runtime info)
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/custom-runtimes/model/{model_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError("Model or custom runtime configuration not found.")
            else:
                raise RuntimeError(f"Failed to get custom runtime: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get custom runtime: {str(e)}")

    # [Model-Custom-Runtime] Delete a custom runtime for a specific model
    def delete_custom_runtime_by_model(self, model_id: str) -> Dict[str, Any]:
        """
        Delete custom runtime configuration by model ID via DELETE /api/v1/custom-runtimes/model/{model_id}

        Args:
            model_id (str): The model ID (UUID)

        Returns:
            dict: The API response (status or empty dict)
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/custom-runtimes/model/{model_id}"
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code in (200, 204):
                return {}  # 성공 시 빈 dict 반환
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError("Model or custom runtime configuration not found.")
            else:
                raise RuntimeError(f"Failed to delete custom runtime: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to delete custom runtime: {str(e)}")

    # ====================================================================
    # Serving
    # ====================================================================

    # [Deployment] Create a new deployment (deploy model)
    def create_deployment(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Create a new deployment (deploy model) via POST /api/v1/servings
        
        Args:
            *args: If a single dict is provided, it will be used as deployment_data
            **kwargs: Deployment creation parameters
            
        Required Parameters:
            - model_id (str): Model ID to deploy
            - name (str): Deployment name
            
        Optional Parameters:
            - description (str): Deployment description
            - cpu_request (str): CPU request (e.g., "100m")
            - cpu_limit (str): CPU limit (e.g., "500m")
            - memory_request (str): Memory request (e.g., "128Mi")
            - memory_limit (str): Memory limit (e.g., "512Mi")
            - min_replicas (int): Minimum number of replicas
            - max_replicas (int): Maximum number of replicas
            - workers_per_core (int): Workers per core
            - use_external_registry (bool): Whether to use external registry
            
        Returns:
            dict: The API response
            
        Examples:
            # Dict style
            deployment_data = {
                "model_id": "model-uuid-here",
                "name": "my-deployment",
                "description": "My model deployment",
                "cpu_request": "100m",
                "cpu_limit": "500m",
                "memory_request": "128Mi",
                "memory_limit": "512Mi",
                "min_replicas": 1,
                "max_replicas": 3
            }
            result = hub.create_deployment(deployment_data)
            
            # Params style
            result = hub.create_deployment(
                model_id="model-uuid-here",
                name="my-deployment",
                description="My model deployment"
            )
        """
        # Handle both dict and kwargs styles
        if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
            deployment_data = args[0].copy()
        else:
            deployment_data = kwargs.copy()
            
        # Self-hosting 모델일 때 기본 serving_params 설정
        model_id = deployment_data.get('model_id')
        if model_id:
            try:
                # 모델 정보를 가져와서 serving_type 확인
                model_info = self.get_model_by_id(model_id)
                serving_type = model_info.get('serving_type')
                
                if serving_type == 'self-hosting':
                    # 기본 serving_params 설정
                    if 'serving_params' not in deployment_data or deployment_data['serving_params'] is None:
                        deployment_data['serving_params'] = DEFAULT_SERVING_PARAMS.copy()
                    else:
                        # 사용자가 제공한 serving_params가 있으면 기본값과 병합
                        user_serving_params = deployment_data['serving_params']
                        if isinstance(user_serving_params, dict):
                            # 기본값으로 시작해서 사용자 값으로 덮어쓰기
                            merged_params = DEFAULT_SERVING_PARAMS.copy()
                            merged_params.update(user_serving_params)
                            deployment_data['serving_params'] = merged_params
            except Exception:
                # 모델 정보를 가져올 수 없는 경우에는 기본값 적용하지 않음
                pass
            
        if self.use_backend_ai:
            url = f"{self.base_url}/api/v1/backend-ai/servings"
        else:
            url = f"{self.base_url}/api/v1/servings"
        try:
            response = requests.post(url, json=deployment_data, headers=self.headers)
            if response.status_code == 201:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 400:
                raise RuntimeError(f"Invalid request: {response.text}")
            elif response.status_code == 404:
                raise RuntimeError("Model not found.")
            else:
                raise RuntimeError(f"Failed to create deployment: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to create deployment: {str(e)}")

    # [Deployment] List all deployments
    def list_deployments(self) -> Dict[str, Any]:
        """
        List all deployments via GET /api/v1/servings
        
        Returns:
            dict: The API response containing list of deployments
        """
        url = f"{self.base_url}/api/v1/servings"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            else:
                raise RuntimeError(f"Failed to list deployments: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to list deployments: {str(e)}")

    # [Deployment] Get a specific deployment
    def get_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """
        Get a specific deployment via GET /api/v1/servings/{deployment_id}
        
        Args:
            deployment_id (str): Deployment ID
            
        Returns:
            dict: The API response containing deployment details
        """
        url = f"{self.base_url}/api/v1/servings/{deployment_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError("Deployment not found.")
            else:
                raise RuntimeError(f"Failed to get deployment: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get deployment: {str(e)}")

    # [Deployment] Update a deployment
    def update_deployment(self, deployment_id: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Update a deployment via PUT /api/v1/servings/{deployment_id}
        
        Args:
            deployment_id (str): Deployment ID
            *args: If a single dict is provided, it will be used as deployment_data
            **kwargs: Deployment update parameters
            
        Returns:
            dict: The API response
            
        Examples:
            # Dict style
            update_data = {"name": "updated-name", "description": "Updated description"}
            result = hub.update_deployment("deployment-id", update_data)
            
            # Params style
            result = hub.update_deployment("deployment-id", name="updated-name", description="Updated description")
        """
        # Handle both dict and kwargs styles
        if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
            deployment_data = args[0]
        else:
            deployment_data = kwargs
            
        if self.use_backend_ai:
            url = f"{self.base_url}/api/v1/backend-ai/servings/{deployment_id}"
        else:
            url = f"{self.base_url}/api/v1/servings/{deployment_id}"
        try:
            response = requests.put(url, json=deployment_data, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError("Deployment not found.")
            else:
                raise RuntimeError(f"Failed to update deployment: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to update deployment: {str(e)}")

    # [Deployment] Delete a deployment
    def delete_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """
        Delete a deployment via DELETE /api/v1/servings/{deployment_id}
        
        Args:
            deployment_id (str): Deployment ID
            
        Returns:
            dict: The API response
        """
        if self.use_backend_ai:
            url = f"{self.base_url}/api/v1/backend-ai/servings/{deployment_id}"
        else:
            url = f"{self.base_url}/api/v1/servings/{deployment_id}"
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code in (200, 204):
                return {}  # 성공 시 빈 dict 반환
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError("Deployment not found.")
            else:
                raise RuntimeError(f"Failed to delete deployment: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to delete deployment: {str(e)}")

    # [Deployment] Start a deployment
    def start_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """
        Start a deployment via POST /api/v1/servings/{deployment_id}/start
        
        Args:
            deployment_id (str): Deployment ID
            
        Returns:
            dict: The API response
        """
        if self.use_backend_ai:
            url = f"{self.base_url}/api/v1/backend-ai/servings/{deployment_id}/start"
        else:
            url = f"{self.base_url}/api/v1/servings/{deployment_id}/start"
        try:
            response = requests.post(url, headers=self.headers)
            if response.status_code in (200, 202):
                return response.json() if response.content else {}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError("Deployment not found.")
            else:
                raise RuntimeError(f"Failed to start deployment: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to start deployment: {str(e)}")

    # [Deployment] Stop a deployment
    def stop_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """
        Stop a deployment via POST /api/v1/servings/{deployment_id}/stop
        
        Args:
            deployment_id (str): Deployment ID
            
        Returns:
            dict: The API response
        """
        if self.use_backend_ai:
            url = f"{self.base_url}/api/v1/backend-ai/servings/{deployment_id}/stop"
        else:
            url = f"{self.base_url}/api/v1/servings/{deployment_id}/stop"
        try:
            response = requests.post(url, headers=self.headers)
            if response.status_code in (200, 202):
                return response.json() if response.content else {}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError("Serving not found.")
            else:
                raise RuntimeError(f"Failed to stop deployment: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to stop deployment: {str(e)}")

    # [Serving] Get serving API keys
    def get_deployment_apikeys(self, deployment_id: str, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """
        Get deployment API keys via GET /api/v1/servings/{deployment_id}/apikeys
        
        Args:
            deployment_id (str): Deployment ID
            page (int): Page number (default: 1)
            size (int): Page size (default: 10)
            
        Returns:
            dict: The API response containing API keys
        """
        url = f"{self.base_url}/api/v1/servings/{deployment_id}/apikeys"
        params = {"page": page, "size": size}
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError("Serving not found.")
            else:
                raise RuntimeError(f"Failed to get deployment API keys: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get deployment API keys: {str(e)}")

    # [Serving] Hard delete serving
    def hard_delete_deployment(self) -> Dict[str, Any]:
        """
        Hard delete a deployment via POST /api/v1/servings/hard-delete
        
        Returns:
            dict: The API response
        """
        url = f"{self.base_url}/api/v1/servings/hard-delete"
        try:
            response = requests.post(url, headers=self.headers)
            if response.status_code in (200, 204):
                return {}  # 성공 시 빈 dict 반환
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError("Serving not found.")
            else:
                raise RuntimeError(f"Failed to hard delete deployment: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to hard delete deployment: {str(e)}")

    # [Resource] Get task resource information
    def get_task_resources(self, task_type: str = "serving", project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get task resource information via GET /api/v1/resources/task/{task_type}
        
        Args:
            task_type (str): Task type (default: "serving")
            project_id (str, optional): Project ID
            
        Returns:
            dict: The API response containing resource information
        """
        url = f"{self.base_url}/api/v1/resources/task/{task_type}"
        params = {}
        if project_id:
            params["project_id"] = project_id
            
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            else:
                raise RuntimeError(f"Failed to get task resources: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get task resources: {str(e)}")

