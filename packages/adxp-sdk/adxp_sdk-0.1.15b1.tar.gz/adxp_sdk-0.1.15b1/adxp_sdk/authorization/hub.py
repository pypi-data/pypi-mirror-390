import requests
from typing import Dict, Any, Optional, Union
from requests.exceptions import RequestException
from adxp_sdk.auth import BaseCredentials, TokenCredentials
from adxp_sdk.auth.credentials import Credentials
from .utils import is_valid_uuid


class AXAuthorizationHub:
    """
    SDK for managing Projects, Roles, Users, and Groups
    """

    def __init__(
        self,
        credentials: Union[BaseCredentials, TokenCredentials, Credentials, None] = None,
        headers: Optional[Dict[str, str]] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the authorization hub object.

        Args:
            credentials: Authentication credentials (BaseCredentials, TokenCredentials, or Credentials)
            headers: HTTP headers for authentication (alternative to credentials)
            base_url: Base URL of the API (alternative to credentials)
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


    # ====================================================================
    # Project Management (CRUD)
    # ====================================================================
    # - List Projects
    # - Create Project
    # - Update Project
    # - Delete Project
    # ====================================================================

    def list_projects(self, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """Fetch project list via GET /api/v1/projects"""
        try:
            url = f"{self.base_url}/api/v1/projects"
            params = {"page": page, "size": size}
            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to list projects: {str(e)}")

    def create_project(self, name: str, cpu_quota: int, mem_quota: int, gpu_quota: int = 0) -> Dict[str, Any]:
        """Create a new project via POST /api/v1/projects"""
        try:
            url = f"{self.base_url}/api/v1/projects"
            payload = {
                "project": {"name": name},
                "namespace": {
                    "cpu_quota": cpu_quota,
                    "mem_quota": mem_quota,
                    "gpu_quota": gpu_quota,
                },
            }
            resp = requests.post(url, headers=self.headers, json=payload)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to create project: {str(e)}")

    def update_project(self, project_id: str, name: str, cpu_quota: int, mem_quota: int, gpu_quota: int = 0) -> Dict[str, Any]:
        """Update an existing project via PUT /api/v1/projects/{project_id}"""
        try:
            if not is_valid_uuid(project_id):
                raise ValueError(f"Invalid project_id format: {project_id}")

            url = f"{self.base_url}/api/v1/projects/{project_id}"
            payload = {
                "project": {"name": name},
                "namespace": {
                    "cpu_quota": cpu_quota,
                    "mem_quota": mem_quota,
                    "gpu_quota": gpu_quota,
                },
            }
            resp = requests.put(url, headers=self.headers, json=payload)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to update project {project_id}: {str(e)}")

    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Delete a project via DELETE /api/v1/projects/{project_id}"""
        try:
            if not is_valid_uuid(project_id):
                raise ValueError(f"Invalid project_id format: {project_id}")

            url = f"{self.base_url}/api/v1/projects/{project_id}"
            resp = requests.delete(url, headers=self.headers)
            resp.raise_for_status()
            try:
                return resp.json()
            except ValueError:
                return {"status": "deleted", "project_id": project_id}
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to delete project {project_id}: {str(e)}")


    # ====================================================================
    # Project Role Management
    # ====================================================================
    # - List Roles in a Project
    # - Create Role
    # - Update Role
    # - Delete Role
    # ====================================================================

    def list_project_roles(self, client_id: str, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """Fetch role list for a project via GET /api/v1/projects/{client_id}/roles"""
        try:
            url = f"{self.base_url}/api/v1/projects/{client_id}/roles"
            params = {"page": page, "size": size}
            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to list roles for project {client_id}: {str(e)}")

    def create_project_role(self, client_id: str, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new role in a project via POST /api/v1/projects/{client_id}/roles"""
        try:
            url = f"{self.base_url}/api/v1/projects/{client_id}/roles"
            payload = {"name": name, "description": description}
            resp = requests.post(url, headers=self.headers, json=payload)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to create role for project {client_id}: {str(e)}")

    def update_project_role(self, client_id: str, role_name: str, description: str) -> Dict[str, Any]:
        """Update an existing role's description via PUT /api/v1/projects/{client_id}/roles/{role_name}"""
        try:
            url = f"{self.base_url}/api/v1/projects/{client_id}/roles/{role_name}"
            payload = {"description": description}
            resp = requests.put(url, headers=self.headers, json=payload)

            # Handle 204 No Content
            if resp.status_code == 204 or not resp.text.strip():
                return {"status": "updated", "role_name": role_name, "description": description}

            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to update role {role_name} in project {client_id}: {str(e)}")

    def delete_project_role(self, client_id: str, role_name: str) -> Dict[str, Any]:
        """Delete a role from a project via DELETE /api/v1/projects/{client_id}/roles/{role_name}"""
        try:
            url = f"{self.base_url}/api/v1/projects/{client_id}/roles/{role_name}"
            resp = requests.delete(url, headers=self.headers)

            # Handle 204 No Content
            if resp.status_code == 204 or not resp.text.strip():
                return {"status": "deleted", "role_name": role_name}

            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to delete role {role_name} in project {client_id}: {str(e)}")


    # ====================================================================
    # User Management (CRUD)
    # ====================================================================
    # - List Users
    # - Create User
    # - Update User
    # - Delete User
    # ====================================================================

    def list_users(self, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """Fetch user list via GET /api/v1/users"""
        try:
            url = f"{self.base_url}/api/v1/users"
            params = {"page": page, "size": size}
            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to list users: {str(e)}")

    def create_user(self, username: str, password: str, email: str, first_name: str, last_name: str) -> Dict[str, Any]:
        """Create a new user via POST /api/v1/users/register"""
        try:
            url = f"{self.base_url}/api/v1/users/register"
            payload = {
                "username": username,
                "password": password,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
            }
            resp = requests.post(url, headers=self.headers, json=payload)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to create user: {str(e)}")

    def update_user(self, user_id: str, email: str, first_name: str, last_name: str) -> Dict[str, Any]:
        """Update a user via PUT /api/v1/users/{user_id}"""
        try:
            if not is_valid_uuid(user_id):
                raise ValueError(f"Invalid user_id format: {user_id}")

            url = f"{self.base_url}/api/v1/users/{user_id}"
            payload = {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
            }
            resp = requests.put(url, headers=self.headers, json=payload)

            # Handle 204 No Content
            if resp.status_code == 204 or not resp.text.strip():
                return {"status": "updated", "user_id": user_id}

            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to update user {user_id}: {str(e)}")

    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete a user via DELETE /api/v1/users/{user_id}"""
        try:
            if not is_valid_uuid(user_id):
                raise ValueError(f"Invalid user_id format: {user_id}")

            url = f"{self.base_url}/api/v1/users/{user_id}"
            resp = requests.delete(url, headers=self.headers)

            # Handle 204 No Content
            if resp.status_code == 204 or not resp.text.strip():
                return {"status": "deleted", "user_id": user_id}

            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to delete user {user_id}: {str(e)}")
        
        
    # ====================================================================
    # User Role Management
    # ====================================================================
    # Includes:
    # - Available Roles 조회
    # - Assign Roles
    # - Assigned Roles 조회
    # - Delete Roles
    # ====================================================================

    def list_user_available_roles(self, user_id: str, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """Get roles available for assignment to a specific user via GET /api/v1/users/{user_id}/role-available"""
        try:
            url = f"{self.base_url}/api/v1/users/{user_id}/role-available"
            params = {"page": page, "size": size}
            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to list available roles for user {user_id}: {str(e)}")


    def assign_roles_to_user(self, user_id: str, roles: list) -> Dict[str, Any]:
        """Assign roles to a user via PUT /api/v1/users/{user_id}/role-mappings"""
        try:
            url = f"{self.base_url}/api/v1/users/{user_id}/role-mappings"
            resp = requests.put(url, headers=self.headers, json=roles)

            # 204 No Content 대응
            if resp.status_code == 204 or not resp.text.strip():
                return {"status": "assigned", "user_id": user_id, "roles": roles}

            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to assign roles to user {user_id}: {str(e)}")


    def list_user_assigned_roles(self, user_id: str, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """Get roles currently assigned to a specific user via GET /api/v1/users/{user_id}/role-mappings"""
        try:
            url = f"{self.base_url}/api/v1/users/{user_id}/role-mappings"
            params = {"page": page, "size": size}
            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to list assigned roles for user {user_id}: {str(e)}")


    def delete_roles_from_user(self, user_id: str, roles: list) -> Dict[str, Any]:
        """Delete roles from a user via DELETE /api/v1/users/{user_id}/role-mappings"""
        try:
            url = f"{self.base_url}/api/v1/users/{user_id}/role-mappings"
            resp = requests.delete(url, headers=self.headers, json=roles)

            # 204 No Content 대응
            if resp.status_code == 204 or not resp.text.strip():
                return {"status": "deleted", "user_id": user_id, "roles": roles}

            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to delete roles from user {user_id}: {str(e)}")
        
        
    # ====================================================================
    # User Group Management
    # ====================================================================
    # - List Available Groups
    # - List Assigned Groups
    # - Assign Group
    # - Delete Group
    # ====================================================================

    def list_user_available_groups(self, user_id: str, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """Get groups available for assignment to a specific user"""
        try:
            url = f"{self.base_url}/api/v1/users/{user_id}/group-available"
            params = {"page": page, "size": size}
            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to list available groups for user {user_id}: {str(e)}")

    def list_user_assigned_groups(self, user_id: str, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """Get groups currently assigned to a specific user"""
        try:
            url = f"{self.base_url}/api/v1/users/{user_id}/group-mappings"
            params = {"page": page, "size": size}
            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to list assigned groups for user {user_id}: {str(e)}")

    def assign_group_to_user(self, user_id: str, group_id: str) -> Dict[str, Any]:
        """Assign a single group to a user (PUT, group_id as query param)"""
        try:
            url = f"{self.base_url}/api/v1/users/{user_id}/group-mappings"
            params = {"group_id": group_id}
            resp = requests.put(url, headers=self.headers, params=params)
            if resp.status_code == 204 or not resp.text.strip():
                return {"status": "assigned", "user_id": user_id, "group_id": group_id}
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to assign group {group_id} to user {user_id}: {str(e)}")

    def delete_group_from_user(self, user_id: str, group_id: str) -> Dict[str, Any]:
        """Delete a single group from a user (DELETE, group_id as query param)"""
        try:
            url = f"{self.base_url}/api/v1/users/{user_id}/group-mappings"
            params = {"group_id": group_id}
            resp = requests.delete(url, headers=self.headers, params=params)
            if resp.status_code == 204 or not resp.text.strip():
                return {"status": "deleted", "user_id": user_id, "group_id": group_id}
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to delete group {group_id} from user {user_id}: {str(e)}")


    # ====================================================================
    # Group Management (CRUD)
    # ====================================================================
    # - List Groups
    # - Create Group
    # - Update Group
    # - Delete Group
    # ====================================================================

    def list_groups(self, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """Fetch group list via GET /api/v1/groups"""
        try:
            url = f"{self.base_url}/api/v1/groups"
            params = {"page": page, "size": size}
            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to list groups: {str(e)}")

    def create_group(self, group_name: str) -> Dict[str, Any]:
        """Create a new group via POST /api/v1/groups"""
        try:
            url = f"{self.base_url}/api/v1/groups"
            params = {"group_name": group_name}
            resp = requests.post(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to create group: {str(e)}")

    def update_group(self, group_id: str, group_name: str) -> Dict[str, Any]:
        """Update a group via PUT /api/v1/groups/{group_id}"""
        try:
            if not is_valid_uuid(group_id):
                raise ValueError(f"Invalid group_id format: {group_id}")

            url = f"{self.base_url}/api/v1/groups/{group_id}"
            payload = {"group_name": group_name}
            resp = requests.put(url, headers=self.headers, json=payload)

            # Handle 204 No Content
            if resp.status_code == 204 or not resp.text.strip():
                return {"status": "updated", "id": group_id, "name": group_name}

            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to update group {group_id}: {str(e)}")

    def delete_group(self, group_id: str) -> Dict[str, Any]:
        """Delete a group via DELETE /api/v1/groups/{group_id}"""
        try:
            if not is_valid_uuid(group_id):
                raise ValueError(f"Invalid group_id format: {group_id}")

            url = f"{self.base_url}/api/v1/groups/{group_id}"
            resp = requests.delete(url, headers=self.headers)

            # Handle 204 No Content
            if resp.status_code == 204 or not resp.text.strip():
                return {"status": "deleted", "id": group_id}

            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to delete group {group_id}: {str(e)}")


    # ====================================================================
    # Cluster Resource
    # ====================================================================
    # - Fetch cluster resource usage/availability
    # ====================================================================

    def get_project_resource_status(self, node_type: str = "task") -> Dict[str, Any]:
        """Fetch cluster resource status via GET /api/v1/resources/cluster"""
        try:
            url = f"{self.base_url}/api/v1/resources/cluster"
            params = {"node_type": node_type}
            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to get resource status: {str(e)}")
