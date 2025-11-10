from typing import Optional
from datetime import datetime, timedelta
import requests
from requests.exceptions import RequestException
from pydantic import BaseModel, PrivateAttr, model_validator, SecretStr
from typing_extensions import Self
from abc import ABC, abstractmethod
import warnings


class BaseCredentials(BaseModel, ABC):
    """
    Abstract base class for authentication credentials.

    This class provides a common interface for different types of credentials
    that can be used with the A.X Platform API.
    """

    @abstractmethod
    def get_headers(self) -> dict:
        """
        Returns the headers required for API requests.

        Returns:
            dict: Headers containing the authentication information
        """
        pass


class ApiKeyCredentials(BaseCredentials):
    """
    Authentication credentials for the A.X Platform API using API key.

    Attributes:
        api_key (str): API key

    Example:
        ```python
        credentials = ApiKeyCredentials(api_key="your_api_key")
        headers = credentials.get_headers()
        ```
    """

    api_key: str
    base_url: str

    def get_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}


class PasswordCredentials(BaseCredentials):
    """
    Authentication credentials for the A.X Platform API using username/password.

    Attributes:
        username (str): User name
        password (str): User password
        project (str): Project name. it is used as client_id in keycloak
        base_url (str): Base URL of the API

    Example:
        ```python
        credentials = PasswordCredentials(
            username="user",
            password="password",
            project="project_name",
            base_url="https://aip.sktai.io"
        )
        token = credentials.authenticate()
        headers = credentials.get_headers()
        ```
    """

    username: str
    password: SecretStr
    project: str
    base_url: str

    _token: Optional[str] = PrivateAttr(default=None)
    _auth_time: Optional[datetime] = PrivateAttr(default=None)
    _token_expiry_seconds: int = PrivateAttr(default=1800)  # 30분을 초로 변경
    _refresh_token: Optional[str] = PrivateAttr(default=None)
    _refresh_expiry_seconds: int = PrivateAttr(default=10800)  # 3시간을 초로 변경
    _grant_type: str = PrivateAttr(default="password")

    @model_validator(mode="after")
    def auto_authenticate(self) -> Self:
        if self.base_url.endswith("/"):
            self.base_url = self.base_url.rstrip("/")
        self.authenticate()
        return self

    @property
    def token(self) -> Optional[str]:
        return self._token

    @property
    def is_token_expired(self) -> bool:
        if not self._auth_time:
            return True
        expiry_time = self._auth_time + timedelta(seconds=self._token_expiry_seconds)
        return datetime.now() > expiry_time

    def _perform_auth(self) -> str:
        login_url = f"{self.base_url}/api/v1/auth/login"
        login_data = {
            "grant_type": self._grant_type,
            "username": self.username,
            "password": self.password.get_secret_value(),
            "client_id": self.project,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        }

        try:
            res = requests.post(login_url, data=login_data, headers=headers)
            if res.status_code == 201:
                response_data = res.json()
                self._token = response_data.get("access_token")
                self._refresh_token = response_data.get("refresh_token")
                self._auth_time = datetime.now()
                
                # expires_in이 있으면 초 단위로 저장
                if "expires_in" in response_data:
                    self._token_expiry_seconds = response_data["expires_in"]
                if "refresh_expires_in" in response_data:
                    self._refresh_expiry_seconds = response_data["refresh_expires_in"]
                
                if self._token is None:
                    raise RuntimeError("Authentication failed: No token received")
                return self._token
            raise RuntimeError(f"Authentication failed: {res.status_code}, {res.text}")
        except RequestException as e:
            raise RuntimeError(
                f"Error occurred during authentication request: {str(e)}"
            )

    def _refresh_token(self) -> str:
        """
        Refresh the access token using refresh token.

        Returns:
            str: New access token

        Raises:
            RuntimeError: If refresh fails
        """
        if not self._refresh_token:
            return self._perform_auth()
        
        refresh_url = f"{self.base_url}/api/v1/auth/token/refresh"
        refresh_data = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
            "client_id": self.project,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        }

        try:
            res = requests.post(refresh_url, data=refresh_data, headers=headers)
            if res.status_code == 201:
                response_data = res.json()
                self._token = response_data.get("access_token")
                self._refresh_token = response_data.get("refresh_token")
                self._auth_time = datetime.now()
                
                # expires_in이 있으면 초 단위로 저장
                if "expires_in" in response_data:
                    self._token_expiry_seconds = response_data["expires_in"]
                if "refresh_expires_in" in response_data:
                    self._refresh_expiry_seconds = response_data["refresh_expires_in"]
                
                if self._token is None:
                    raise RuntimeError("Token refresh failed: No token received")
                return self._token
            raise RuntimeError(f"Token refresh failed: {res.status_code}, {res.text}")
        except RequestException as e:
            raise RuntimeError(
                f"Error occurred during token refresh request: {str(e)}"
            )

    def authenticate(self) -> str:
        """
        Authenticates with the API server and retrieves a token.
        If the token is expired, it automatically attempts to refresh.

        Returns:
            str: Authentication token

        Raises:
            RuntimeError: If authentication fails
        """
        if self._token and not self.is_token_expired:
            return self._token
        else:
            # 토큰이 만료되었을 때 refresh 시도, 실패하면 재인증
            try:
                return self._refresh_token()
            except RuntimeError:
                return self._perform_auth()

    def get_headers(self) -> dict:
        """
        Returns the headers required for API requests.

        Returns:
            dict: Headers containing the authentication token
        """
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        if self._token is None or self.is_token_expired:
            self.authenticate()

        headers["Authorization"] = f"Bearer {self._token}"

        return headers

    @staticmethod
    def exchange_token(base_url: str, token: str, project_name: str) -> dict:
        """
        Exchange an existing token for another client.

        Args:
            base_url (str): API base URL
            token (str): Existing access token
            to_exchange_client_name (str): Target client name

        Returns:
            dict: Full JSON response
        """
        url = f"{base_url}/api/v1/auth/token/exchange"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        params = {"to_exchange_client_name": project_name}

        try:
            res = requests.get(url, params=params, headers=headers)
            res.raise_for_status()
            return res.json()
        except RequestException as e:
            raise RuntimeError(f"Error during token exchange request: {str(e)}")


class TokenCredentials(BaseCredentials):
    """
    Authentication credentials for the A.X Platform API using direct access token.

    This class is designed for scenarios where you already have access_token and refresh_token
    (e.g., from environment variables after portal authentication).

    Attributes:
        access_token (str): Direct access token
        refresh_token (str): Refresh token for token renewal
        base_url (str): Base URL of the API

    Example:
        ```python
        credentials = TokenCredentials(
            access_token="your_access_token",
            refresh_token="your_refresh_token",
            base_url="https://aip.sktai.io"
        )
        headers = credentials.get_headers()
        ```
    """

    access_token: str
    refresh_token: str
    base_url: str

    _token: Optional[str] = PrivateAttr(default=None)
    _auth_time: Optional[datetime] = PrivateAttr(default=None)
    _token_expiry_seconds: int = PrivateAttr(default=1800)  # 30분을 초로 변경
    _refresh_expiry_seconds: int = PrivateAttr(default=10800)  # 3시간을 초로 변경

    @model_validator(mode="after")
    def auto_authenticate(self) -> Self:
        if self.base_url.endswith("/"):
            self.base_url = self.base_url.rstrip("/")
        self._token = self.access_token
        self._auth_time = datetime.now()
        return self

    @property
    def token(self) -> Optional[str]:
        return self._token

    @property
    def is_token_expired(self) -> bool:
        if not self._auth_time:
            return True
        expiry_time = self._auth_time + timedelta(seconds=self._token_expiry_seconds)
        return datetime.now() > expiry_time

    def _refresh_token(self) -> str:
        """
        Refresh the access token using refresh token.

        Returns:
            str: New access token

        Raises:
            RuntimeError: If refresh fails
        """
        refresh_url = f"{self.base_url}/api/v1/auth/token/refresh"
        refresh_data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        }

        try:
            res = requests.post(refresh_url, data=refresh_data, headers=headers)
            if res.status_code == 201:
                response_data = res.json()
                self._token = response_data.get("access_token")
                self.refresh_token = response_data.get("refresh_token", self.refresh_token)
                self._auth_time = datetime.now()
                
                # expires_in이 있으면 초 단위로 저장
                if "expires_in" in response_data:
                    self._token_expiry_seconds = response_data["expires_in"]
                if "refresh_expires_in" in response_data:
                    self._refresh_expiry_seconds = response_data["refresh_expires_in"]
                
                if self._token is None:
                    raise RuntimeError("Token refresh failed: No token received")
                return self._token
            raise RuntimeError(f"Token refresh failed: {res.status_code}, {res.text}")
        except RequestException as e:
            raise RuntimeError(
                f"Error occurred during token refresh request: {str(e)}"
            )

    def authenticate(self) -> str:
        """
        Authenticates with the API server and retrieves a token.
        If the token is expired, it automatically attempts to refresh.

        Returns:
            str: Authentication token

        Raises:
            RuntimeError: If authentication fails
        """
        if self._token and not self.is_token_expired:
            return self._token
        else:
            # 토큰이 만료되었을 때 refresh 시도
            return self._refresh_token()

    def get_headers(self) -> dict:
        """
        Returns the headers required for API requests.

        Returns:
            dict: Headers containing the authentication token
        """
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        if self._token is None or self.is_token_expired:
            self.authenticate()

        headers["Authorization"] = f"Bearer {self._token}"

        return headers


class Credentials(PasswordCredentials):
    """
    Deprecated: Use PasswordCredentials instead.

    This class is kept for backward compatibility but will be removed in a future version.
    Please use PasswordCredentials instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Credentials is deprecated and will be removed in a future version. "
            "Please use PasswordCredentials instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
