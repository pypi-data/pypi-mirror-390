"""API client for Simultaneous hosted API."""

import json
import os
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console

from cli.auth import get_current_token, load_token

console = Console()

# API base URL
API_BASE_URL = os.getenv("SIMULTANEOUS_API_URL", "https://simultaneous-api.fly.dev")
FRONTEND_URL = os.getenv("SIMULTANEOUS_FRONTEND_URL", "https://simultaneous.live")


class APIError(Exception):
    """Exception raised for API errors."""
    
    def __init__(self, message: str, status_code: int | None = None, response: dict[str, Any] | None = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class APIClient:
    """Client for interacting with Simultaneous API."""
    
    def __init__(self, base_url: str | None = None):
        """Initialize API client.
        
        Args:
            base_url: Base URL for the API (defaults to SIMULTANEOUS_API_URL env var)
        """
        self.base_url = (base_url or API_BASE_URL).rstrip("/")
        self._client = httpx.Client(timeout=30.0)
    
    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers with authentication token.
        
        Returns:
            Dictionary of headers
        """
        headers = {"Content-Type": "application/json"}
        token = get_current_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request to API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            
        Returns:
            Response JSON data
            
        Raises:
            APIError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            response = self._client.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
            )
            
            # Handle non-JSON responses
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"detail": response.text}
            
            if not response.is_success:
                error_msg = response_data.get("detail", response_data.get("error", "Unknown error"))
                raise APIError(
                    message=error_msg,
                    status_code=response.status_code,
                    response=response_data,
                )
            
            return response_data
            
        except httpx.HTTPError as e:
            raise APIError(f"Network error: {str(e)}") from e
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}") from e
    
    # Authentication methods
    def signup(self, email: str, password: str, metadata: dict[str, str] | None = None) -> dict[str, Any]:
        """Sign up a new user.
        
        Args:
            email: User email
            password: User password
            metadata: Optional metadata
            
        Returns:
            User data
        """
        return self._request("POST", "/v1/auth/signup", data={
            "email": email,
            "password": password,
            "metadata": metadata or {},
        })
    
    def signin(self, email: str, password: str) -> dict[str, Any]:
        """Sign in a user.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Auth response with tokens
        """
        return self._request("POST", "/v1/auth/signin", data={
            "email": email,
            "password": password,
        })
    
    def signout(self) -> dict[str, str]:
        """Sign out current user.
        
        Returns:
            Success message
        """
        return self._request("POST", "/v1/auth/signout")
    
    def get_me(self) -> dict[str, Any]:
        """Get current authenticated user.
        
        Returns:
            User data
        """
        return self._request("GET", "/v1/auth/me")
    
    def sync_user(self) -> dict[str, Any]:
        """Sync user with API (creates default project if needed).
        
        Returns:
            User and project data
        """
        return self._request("POST", "/v1/auth/sync")
    
    # Organization methods (if endpoints exist)
    def create_org(self, name: str) -> dict[str, Any]:
        """Create a new organization.
        
        Args:
            name: Organization name
            
        Returns:
            Organization data
        """
        # Note: This endpoint may need to be created in the API
        return self._request("POST", "/v1/organizations", data={"name": name})
    
    def list_orgs(self) -> list[dict[str, Any]]:
        """List all organizations.
        
        Returns:
            List of organizations
        """
        # Note: This endpoint may need to be created in the API
        return self._request("GET", "/v1/organizations")
    
    # Project methods
    def create_project(self, name: str, slug: str | None = None) -> dict[str, Any]:
        """Create a new project.
        
        Args:
            name: Project name
            slug: Optional project slug (auto-generated if not provided)
            
        Returns:
            Project data
        """
        data = {"name": name}
        if slug:
            data["slug"] = slug
        return self._request("POST", "/v1/projects", data=data)
    
    def list_projects(self, archived: bool = False) -> list[dict[str, Any]]:
        """List all projects.
        
        Args:
            archived: Whether to include archived projects
            
        Returns:
            List of projects
        """
        return self._request("GET", "/v1/projects", params={"archived": archived})
    
    def get_project(self, project_id: str) -> dict[str, Any]:
        """Get a project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project data
        """
        return self._request("GET", f"/v1/projects/{project_id}")
    
    def update_project(self, project_id: str, name: str | None = None, archived: bool | None = None) -> dict[str, Any]:
        """Update a project.
        
        Args:
            project_id: Project ID
            name: New project name (optional)
            archived: Archive status (optional)
            
        Returns:
            Updated project data
        """
        data = {}
        if name is not None:
            data["name"] = name
        if archived is not None:
            data["archived"] = archived
        return self._request("PATCH", f"/v1/projects/{project_id}", data=data)
    
    def delete_project(self, project_id: str) -> None:
        """Delete a project.
        
        Args:
            project_id: Project ID
        """
        self._request("DELETE", f"/v1/projects/{project_id}")
    
    # Agent methods
    def create_agent(
        self,
        project_id: str,
        name: str,
        script: str,
        provider_project_id: str | None = None,
        description: str | None = None,
        env_vars: dict[str, str] | None = None,
        context_id: str | None = None,
        extension_id: str | None = None,
        region: str | None = None,
        timeout_sec: int | None = None,
    ) -> dict[str, Any]:
        """Create a new agent.
        
        Args:
            project_id: Project ID
            name: Agent name
            script: Agent script
            provider_project_id: Browserbase project ID (optional, defaults to BROWSERBASE_PROJECT_ID from API secrets)
            description: Agent description
            env_vars: Environment variables
            context_id: Context ID
            extension_id: Extension ID
            region: Region
            timeout_sec: Timeout in seconds
            
        Returns:
            Agent data
        """
        data = {
            "name": name,
            "script": script,
        }
        if provider_project_id:
            data["providerProjectId"] = provider_project_id
        if description:
            data["description"] = description
        if env_vars:
            data["envVars"] = env_vars
        if context_id:
            data["contextId"] = context_id
        if extension_id:
            data["extensionId"] = extension_id
        if region:
            data["region"] = region
        if timeout_sec:
            data["timeoutSec"] = timeout_sec
        
        return self._request("POST", f"/v1/browserbase/projects/{project_id}/agents", data=data)
    
    def list_agents(self, project_id: str, active_only: bool = False) -> list[dict[str, Any]]:
        """List agents for a project.
        
        Args:
            project_id: Project ID
            active_only: Whether to filter only active agents
            
        Returns:
            List of agents
        """
        return self._request("GET", f"/v1/browserbase/projects/{project_id}/agents", params={"active_only": active_only})
    
    def get_agent(self, project_id: str, agent_id: str) -> dict[str, Any]:
        """Get an agent by ID.
        
        Args:
            project_id: Project ID
            agent_id: Agent ID
            
        Returns:
            Agent data
        """
        return self._request("GET", f"/v1/browserbase/projects/{project_id}/agents/{agent_id}")
    
    def update_agent(
        self,
        project_id: str,
        agent_id: str,
        name: str | None = None,
        script: str | None = None,
        description: str | None = None,
        env_vars: dict[str, str] | None = None,
        context_id: str | None = None,
        extension_id: str | None = None,
        region: str | None = None,
        timeout_sec: int | None = None,
        active: bool | None = None,
    ) -> dict[str, Any]:
        """Update an agent.
        
        Args:
            project_id: Project ID
            agent_id: Agent ID
            name: Agent name (optional)
            script: Agent script (optional)
            description: Agent description (optional)
            env_vars: Environment variables (optional)
            context_id: Context ID (optional)
            extension_id: Extension ID (optional)
            region: Region (optional)
            timeout_sec: Timeout in seconds (optional)
            active: Active flag (optional)
            
        Returns:
            Updated agent data
        """
        data = {}
        if name is not None:
            data["name"] = name
        if script is not None:
            data["script"] = script
        if description is not None:
            data["description"] = description
        if env_vars is not None:
            data["envVars"] = env_vars
        if context_id is not None:
            data["contextId"] = context_id
        if extension_id is not None:
            data["extensionId"] = extension_id
        if region is not None:
            data["region"] = region
        if timeout_sec is not None:
            data["timeoutSec"] = timeout_sec
        if active is not None:
            data["active"] = active
        
        return self._request("PUT", f"/v1/browserbase/projects/{project_id}/agents/{agent_id}", data=data)
    
    def delete_agent(self, project_id: str, agent_id: str) -> None:
        """Delete an agent.
        
        Args:
            project_id: Project ID
            agent_id: Agent ID
        """
        self._request("DELETE", f"/v1/browserbase/projects/{project_id}/agents/{agent_id}")
    
    # Agent execution methods
    def run_agent(
        self,
        project_id: str,
        agent_id: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run an agent.
        
        Args:
            project_id: Project ID
            agent_id: Agent ID
            params: Agent parameters
            
        Returns:
            Run response with run ID
        """
        # Note: This endpoint may need to be created in the API
        return self._request("POST", f"/v1/browserbase/projects/{project_id}/agents/{agent_id}/run", data={"params": params or {}})
    
    # Marketplace methods (to be implemented)
    def publish_agent(self, project_id: str, agent_id: str, public: bool = True) -> dict[str, Any]:
        """Publish an agent to the marketplace.
        
        Args:
            project_id: Project ID (may be empty if agent_id is globally unique)
            agent_id: Agent ID
            public: Whether to make the agent public
            
        Returns:
            Publication response
        """
        # Note: This endpoint may need to be created in the API
        data = {"public": public}
        if project_id:
            data["project_id"] = project_id
        return self._request("POST", f"/v1/marketplace/agents/{agent_id}/publish", data=data)
    
    def list_marketplace_agents(self) -> list[dict[str, Any]]:
        """List agents in the marketplace.
        
        Returns:
            List of marketplace agents
        """
        # Note: This endpoint may need to be created in the API
        return self._request("GET", "/v1/marketplace/agents")
    
    def deploy_from_marketplace(self, agent_id: str, project_id: str) -> dict[str, Any]:
        """Deploy an agent from the marketplace to a project.
        
        Args:
            agent_id: Marketplace agent ID
            project_id: Target project ID
            
        Returns:
            Deployment response
        """
        # Note: This endpoint may need to be created in the API
        return self._request("POST", f"/v1/marketplace/agents/{agent_id}/deploy", data={"project_id": project_id})
    
    # Deploy to cloud (Modal - placeholder)
    def deploy_agent_to_cloud(self, project_id: str, agent_id: str) -> dict[str, Any]:
        """Deploy an agent to the cloud (Modal).
        
        Args:
            project_id: Project ID
            agent_id: Agent ID
            
        Returns:
            Deployment response
        """
        # Note: This endpoint may need to be created in the API
        return self._request("POST", f"/v1/browserbase/projects/{project_id}/agents/{agent_id}/deploy", data={})

    # New: Container-based deployment and run via Modal (API-managed)
    def deploy_agent(
        self,
        project_id: str,
        agent_id: str,
        container_image: str,
        container_registry: str = "ghcr",
        build_image: bool = False,
        push_image: bool = False,
        agent_dir_path: Path | None = None,
    ) -> dict[str, Any]:
        """Register or build-and-register a container image for an agent.

        If build_image is True and agent_dir_path is provided, the agent directory will be uploaded
        as a tar.gz and built server-side. Otherwise, only registers the provided image.
        """
        endpoint = f"/v1/agents/projects/{project_id}/agents/{agent_id}/deploy"
        data: dict[str, Any] = {
            "container_image": container_image,
            "container_registry": container_registry,
            "build_image": build_image,
            "push_image": push_image,
        }

        if build_image and agent_dir_path and agent_dir_path.exists():
            # Multipart upload path
            url = f"{self.base_url}{endpoint}"
            headers = self._get_headers()
            # Allow httpx to set multipart boundary
            if "Content-Type" in headers:
                del headers["Content-Type"]

            # Create tar.gz of the agent directory
            import tarfile
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
                with tarfile.open(tmp.name, "w:gz") as tar:
                    tar.add(agent_dir_path, arcname=".")
                files = {"agent_dir": ("agent.tar.gz", open(tmp.name, "rb"), "application/gzip")}
                resp = self._client.post(url, headers=headers, data=data, files=files)
                try:
                    body = resp.json()
                except Exception:
                    body = {"detail": resp.text}
                if not resp.is_success:
                    raise APIError(body.get("detail", "Upload failed"), status_code=resp.status_code, response=body)
                return body

        return self._request("POST", endpoint, data=data)

    def run_agent_container(
        self,
        project_id: str,
        agent_id: str,
        params: dict[str, Any] | None = None,
        env_vars: dict[str, str] | None = None,
        timeout_sec: int = 600,
    ) -> dict[str, Any]:
        """Run a deployed agent container via Modal (API orchestrated)."""
        return self._request(
            "POST",
            f"/v1/agents/projects/{project_id}/agents/{agent_id}/run",
            data={
                "params": params or {},
                "env_vars": env_vars or {},
                "timeout_sec": timeout_sec,
            },
        )
    
    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

