"""HTTP client for accessing HumaLab service APIs with API key authentication."""

from enum import Enum
import os
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
from humalab.humalab_config import HumalabConfig


class RunStatus(Enum):
    """Status of runs"""
    RUNNING = "running"
    CANCELED = "canceled"
    ERRORED = "errored"
    FINISHED = "finished"


class EpisodeStatus(Enum):
    """Status of validation episodes"""
    RUNNING = "running"
    CANCELED = "canceled"
    ERRORED = "errored"
    SUCCESS = "success"
    FAILED = "failed"


class HumaLabApiClient:
    """HTTP client for making authenticated requests to HumaLab service APIs."""
    
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float | None = None
    ):
        """
        Initialize the HumaLab API client.
        
        Args:
            base_url: Base URL for the HumaLab service (defaults to https://api.humalab.ai)
            api_key: API key for authentication (defaults to HUMALAB_API_KEY env var)
            timeout: Request timeout in seconds
        """
        humalab_config = HumalabConfig()
        self.base_url = base_url or humalab_config.base_url or os.getenv("HUMALAB_SERVICE_URL", "https://api.humalab.ai")
        self.api_key = api_key or humalab_config.api_key or os.getenv("HUMALAB_API_KEY")
        self.timeout = timeout or humalab_config.timeout or 30.0  # Default timeout of 30 seconds
        
        # Ensure base_url ends without trailing slash
        self.base_url = self.base_url.rstrip('/')
        
        if not self.api_key:
            raise ValueError(
                "API key is required. Set HUMALAB_API_KEY environment variable "
                "or pass api_key parameter to HumaLabApiClient constructor."
            )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get common headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "HumaLab-SDK/1.0"
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make an HTTP request to the HumaLab service.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (will be joined with base_url)
            data: JSON data for request body
            params: Query parameters
            files: Files for multipart upload
            **kwargs: Additional arguments passed to requests
            
        Returns:
            requests.Response object
            
        Raises:
            requests.exceptions.RequestException: For HTTP errors
        """
        url = urljoin(self.base_url + "/", endpoint.lstrip('/'))
        headers = self._get_headers()
        
        # If files are being uploaded, don't set Content-Type (let requests handle it)
        if files:
            headers.pop("Content-Type", None)
        
        # Determine if we should send form data or JSON
        # Form data endpoints: /artifacts/code, /artifacts/blob/upload, /artifacts/python
        is_form_endpoint = any(form_path in endpoint for form_path in ['/artifacts/code', '/artifacts/blob', '/artifacts/python'])
        
        if is_form_endpoint or files:
            # Send as form data
            headers.pop("Content-Type", None)  # Let requests set multipart/form-data
            response = requests.request(
                method=method,
                url=url,
                data=data,
                params=params,
                files=files,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
        else:
            # Send as JSON (default behavior)
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                files=files,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
        
        # Raise an exception for HTTP error responses
        response.raise_for_status()
        
        return response
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params, **kwargs)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """Make a POST request."""
        return self._make_request("POST", endpoint, data=data, files=files, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Make a PUT request."""
        return self._make_request("PUT", endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint, **kwargs)

    # User Authentication API methods
    def validate_token(self) -> Dict[str, Any]:
        """
        Validate JWT token and return user info.

        Returns:
            User information from the validated token
        """
        response = self.get("/auth/validate")
        return response.json()

    # Convenience methods for common API operations
    
    def get_resources(
        self,
        project_name: str,
        resource_types: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        latest_only: bool = True
    ) -> Dict[str, Any]:
        """
        Get list of all resources.

        Args:
            project_name: Project name (required)
            resource_types: Comma-separated resource types to filter by
            limit: Maximum number of resources to return
            offset: Number of resources to skip
            latest_only: If true, only return latest version of each resource

        Returns:
            Resource list with pagination info
        """
        params = {
            "project_name": project_name,
            "limit": limit,
            "offset": offset,
            "latest_only": latest_only
        }
        if resource_types:
            params["resource_types"] = resource_types

        response = self.get("/resources", params=params)
        return response.json()
    
    def get_resource(self, name: str, project_name: str, version: Optional[int] = None) -> Dict[str, Any]:
        """
        Get a specific resource.

        Args:
            name: Resource name
            project_name: Project name (required)
            version: Optional specific version (defaults to latest)

        Returns:
            Resource data
        """
        if version is not None:
            endpoint = f"/resources/{name}/{version}"
            params = {"project_name": project_name}
        else:
            endpoint = f"/resources/{name}"
            params = {"project_name": project_name}

        response = self.get(endpoint, params=params)
        return response.json()
    
    def download_resource(
        self,
        name: str,
        project_name: str,
        version: Optional[int] = None
    ) -> bytes:
        """
        Download a resource file.

        Args:
            name: Resource name
            project_name: Project name (required)
            version: Optional specific version (defaults to latest)

        Returns:
            Resource file content as bytes
        """
        endpoint = f"/resources/{name}/download"
        params = {"project_name": project_name}
        if version is not None:
            params["version"] = str(version)

        response = self.get(endpoint, params=params)
        return response.content
    
    def upload_resource(
        self,
        name: str,
        file_path: str,
        resource_type: str,
        project_name: str,
        description: Optional[str] = None,
        filename: Optional[str] = None,
        allow_duplicate_name: bool = False
    ) -> Dict[str, Any]:
        """
        Upload a resource file.

        Args:
            name: Resource name
            file_path: Path to file to upload
            resource_type: Type of resource (urdf, mjcf, etc.)
            project_name: Project name (required)
            description: Optional description
            filename: Optional custom filename
            allow_duplicate_name: Allow creating new version with existing name

        Returns:
            Created resource data
        """
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {}
            if description:
                data['description'] = description
            if filename:
                data['filename'] = filename

            params = {
                'resource_type': resource_type,
                'project_name': project_name,
                'allow_duplicate_name': allow_duplicate_name
            }

            response = self.post(f"/resources/{name}/upload", files=files, params=params)
            return response.json()
    
    def get_resource_types(self) -> List[str]:
        """Get list of all available resource types."""
        response = self.get("/resources/types")
        return response.json()

    def get_scenarios(
        self,
        project_name: str,
        limit: int = 20,
        offset: int = 0,     
        include_inactive: bool = False,
        search: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get list of scenarios with pagination and filtering.

        Args:
            project_name: Project name (required)
            limit: Maximum number of scenarios to return (1-100)
            offset: Number of scenarios to skip
            include_inactive: Include inactive scenarios in results
            search: Search term to filter by name, description, or UUID
            status_filter: Filter by specific status

        Returns:
            Paginated list of scenarios
        """
        params = {
            "project_name": project_name,
            "skip": offset,
            "limit": limit,
            "include_inactive": include_inactive
        }
        if search:
            params["search"] = search
        if status_filter:
            params["status_filter"] = status_filter

        response = self.get("/scenarios", params=params)
        return response.json()
    
    def get_scenario(self, uuid: str, project_name: str, version: Optional[int] = None) -> Dict[str, Any]:
        """
        Get a specific scenario.

        Args:
            uuid: Scenario UUID
            project_name: Project name (required)
            version: Optional specific version (defaults to latest)

        Returns:
            Scenario data
        """
        endpoint = f"/scenarios/{uuid}"
        params = {"project_name": project_name}
        if version is not None:
            params["scenario_version"] = str(version)

        response = self.get(endpoint, params=params)
        return response.json()

    def create_scenario(
        self,
        name: str,
        project_name: str,
        description: Optional[str] = None,
        yaml_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new scenario.

        Args:
            name: Scenario name
            project_name: Project name to organize the scenario (required)
            description: Optional scenario description
            yaml_content: Optional YAML content defining the scenario

        Returns:
            Created scenario data with UUID and version

        Raises:
            HTTPException: If scenario name already exists for the project
        """
        data = {
            "name": name,
            "project_name": project_name
        }
        if description:
            data["description"] = description
        if yaml_content:
            data["yaml_content"] = yaml_content

        response = self.post("/scenarios", data=data)
        return response.json()

    # Run CI API methods
    
    def create_project(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            name: Project name
            description: Optional project description
            
        Returns:
            Created project data
        """
        data = {"name": name}
        if description:
            data["description"] = description
            
        response = self.post("/projects", data=data)
        return response.json()
    
    def get_projects(
        self, 
        limit: int = 20, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get list of projects.
        
        Args:
            limit: Maximum number of projects to return
            offset: Number of projects to skip
            
        Returns:
            Project list with pagination info
        """
        params = {"limit": limit, "offset": offset}
        response = self.get("/projects", params=params)
        return response.json()
    
    def get_project(self, name: str) -> Dict[str, Any]:
        """
        Get a specific project.
        
        Args:
            name: Project name
            
        Returns:
            Project data
        """
        response = self.get(f"/projects/{name}")
        return response.json()
    
    def update_project(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a project.

        Args:
            name: Project name
            description: Optional new description

        Returns:
            Updated project data
        """
        data = {}
        if description is not None:
            data["description"] = description

        response = self.put(f"/projects/{name}", data=data)
        return response.json()
    
    def create_run(
        self, 
        name: str, 
        project_name: str,
        description: Optional[str] = None,
        arguments: Optional[List[Dict[str, str]]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new run.
        
        Args:
            name: Run name
            project_name: Project name
            description: Optional run description
            arguments: Optional list of key-value arguments
            tags: Optional list of tags
            
        Returns:
            Created run data with runId
        """
        data = {
            "name": name,
            "project_name": project_name,
            "arguments": arguments or [],
            "tags": tags or [],
            "status": RunStatus.RUNNING.value
        }
        if description:
            data["description"] = description
            
        response = self.post("/runs", data=data)
        return response.json()
    
    def get_runs(
        self,
        project_name: Optional[str],
        status: Optional[RunStatus] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get list of runs.
        
        Args:
            project_name: Filter by project name
            status: Filter by status (running, finished, failed, killed)
            tags: Filter by tags
            limit: Maximum number of runs to return
            offset: Number of runs to skip
            
        Returns:
            Run list with pagination info
        """
        params = {"limit": limit, "offset": offset}
        if not project_name:
            raise ValueError("project_name is required to get runs.")
        params["project_name"] = project_name
        if status:
            params["status"] = status.value
        if tags:
            params["tags"] = ",".join(tags)
            
        response = self.get("/runs", params=params)
        return response.json()
    
    def get_run(self, run_id: str) -> Dict[str, Any]:
        """
        Get a specific run.
        
        Args:
            run_id: Run ID
            
        Returns:
            Run data
        """
        response = self.get(f"/runs/{run_id}")
        return response.json()
    
    def update_run(
        self,
        run_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[RunStatus] = None,
        err_msg: Optional[str] = None,
        arguments: Optional[List[Dict[str, str]]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update a run.

        Args:
            run_id: Run ID
            name: Optional new name
            description: Optional new description
            status: Optional new status
            err_msg: Optional error message
            arguments: Optional new arguments
            tags: Optional new tags

        Returns:
            Updated run data
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if status is not None:
            data["status"] = status.value
        if err_msg is not None:
            data["err_msg"] = err_msg
        if arguments is not None:
            data["arguments"] = arguments
        if tags is not None:
            data["tags"] = tags

        response = self.put(f"/runs/{run_id}", data=data)
        return response.json()
    
    def create_episode(
        self, 
        run_id: str, 
        episode_id: str,
        status: Optional[EpisodeStatus] = None
    ) -> Dict[str, Any]:
        """
        Create a new episode.
        
        Args:
            run_id: Run ID
            episode_id: Episode name
            status: Optional episode status
            
        Returns:
            Created episode data
        """
        data = {
            "episode_id": episode_id,
            "run_id": run_id
        }
        if status:
            data["status"] = status.value
            
        response = self.post("/episodes", data=data)
        return response.json()
    
    def get_episodes(
        self,
        run_id: Optional[str] = None,
        status: Optional[EpisodeStatus] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get list of episodes.
        
        Args:
            run_id: Filter by run ID
            status: Filter by status
            limit: Maximum number of episodes to return
            offset: Number of episodes to skip
            
        Returns:
            Episode list with pagination info
        """
        params = {"limit": limit, "offset": offset}
        if run_id:
            params["run_id"] = run_id
        if status:
            params["status"] = status.value
            
        response = self.get("/episodes", params=params)
        return response.json()
    
    def get_episode(self, run_id: str, episode_id: str) -> Dict[str, Any]:
        """
        Get a specific episode.
        
        Args:
            run_id: Run ID
            episode_id: Episode name
            
        Returns:
            Episode data
        """
        response = self.get(f"/episodes/{run_id}/{episode_id}")
        return response.json()
    
    def update_episode(
        self,
        run_id: str,
        episode_id: str,
        status: Optional[EpisodeStatus] = None,
        err_msg: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an episode.
        
        Args:
            run_id: Run ID
            episode_id: Episode name
            status: Optional new status
            err_msg: Optional error message

        Returns:
            Updated episode data
        """
        data = {}
        if status is not None:
            data["status"] = status.value
        if err_msg is not None:
            data["err_msg"] = err_msg
        response = self.put(f"/episodes/{run_id}/{episode_id}", data=data)
        return response.json()
    
    def delete_episode(self, run_id: str, episode_id: str) -> None:
        """
        Delete an episode.
        
        Args:
            run_id: Run ID
            episode_id: Episode name
        """
        self.delete(f"/episodes/{run_id}/{episode_id}")
    
    def upload_blob(
        self,
        artifact_key: str,
        run_id: str,
        artifact_type: str,
        file_content: bytes | None = None,
        file_path: str | None = None,
        episode_id: Optional[str] = None,
        filename: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a blob artifact (image/video).

        Args:
            artifact_key: Artifact key identifier
            run_id: Run ID
            artifact_type: Type of artifact ('image' or 'video')
            file_content: File content as bytes
            file_path: Path to file to upload
            episode_id: Optional episode ID (None for run-level artifacts)
            filename: Optional filename to use for the uploaded file
            content_type: Optional content type (e.g., 'image/png', 'video/mp4')

        Returns:
            Created artifact data
        """
        form_data = {
            'artifact_key': artifact_key,
            'run_id': run_id,
            'artifact_type': artifact_type
        }
        if episode_id:
            form_data['episode_id'] = episode_id
        if filename:
            form_data['filename'] = filename
        if content_type:
            form_data['content_type'] = content_type

        if file_path:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = self.post("/artifacts/blob/upload", files=files, data=form_data)
        elif file_content:
            files = {'file': ('blob', file_content)}
            response = self.post("/artifacts/blob/upload", files=files, data=form_data)
        else:
            raise ValueError("Either file_path or file_content must be provided for blob upload.")
        return response.json()
    
    def upsert_metrics(
        self,
        artifact_key: str,
        run_id: str,
        metric_type: str,
        metric_data: Optional[List[Dict[str, Any]]] = None,
        episode_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upsert metrics artifact (create or append).

        Args:
            artifact_key: Artifact key identifier
            run_id: Run ID
            metric_type: Type of metric display ('line', 'bar', 'scatter', 'gauge', 'counter')
            metric_data: List of metric data points with 'key', 'values', 'timestamp'
            episode_id: Optional episode ID (None for run-level artifacts)

        Returns:
            Created/updated artifact data
        """
        data = {
            "artifact_key": artifact_key,
            "run_id": run_id,
            "metric_type": metric_type
        }
        if episode_id:
            data["episode_id"] = episode_id
        if metric_data:
            data["metric_data"] = metric_data

        response = self.post("/artifacts/metrics", data=data)
        return response.json()
    
    def get_artifacts(
        self,
        run_id: Optional[str] = None,
        episode_id: Optional[str] = None,
        artifact_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get list of artifacts.

        Args:
            run_id: Filter by run ID
            episode_id: Filter by episode ID
            artifact_type: Filter by artifact type
            limit: Maximum number of artifacts to return (0 for no limit)
            offset: Number of artifacts to skip

        Returns:
            Artifact list with pagination info
        """
        params = {"limit": limit, "offset": offset}
        if run_id:
            params["run_id"] = run_id
        if episode_id:
            params["episode_id"] = episode_id
        if artifact_type:
            params["artifact_type"] = artifact_type

        response = self.get("/artifacts", params=params)
        return response.json()
    
    def get_artifact(
        self,
        run_id: str,
        episode_id: str,
        artifact_key: str
    ) -> Dict[str, Any]:
        """
        Get a specific artifact.

        Args:
            run_id: Run ID
            episode_id: Episode ID
            artifact_key: Artifact key

        Returns:
            Artifact data
        """
        response = self.get(f"/artifacts/{run_id}/{episode_id}/{artifact_key}")
        return response.json()

    def upload_code(
        self,
        artifact_key: str,
        run_id: str,
        code_content: str,
        episode_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload code artifact (YAML/string content).

        Args:
            artifact_key: Artifact key identifier
            run_id: Run ID
            code_content: Code/text content to upload
            episode_id: Optional episode ID (None for run-level artifacts)

        Returns:
            Created artifact data
        """
        data = {
            'artifact_key': artifact_key,
            'run_id': run_id,
            'code_content': code_content
        }
        if episode_id:
            data['episode_id'] = episode_id

        response = self.post("/artifacts/code", data=data)
        return response.json()

    def upload_python(
        self,
        artifact_key: str,
        run_id: str,
        pickled_bytes: bytes,
        episode_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload pickled Python object as artifact.

        Args:
            artifact_key: Artifact key identifier
            run_id: Run ID
            pickled_bytes: Pickled Python object as bytes
            episode_id: Optional episode ID (None for run-level artifacts)

        Returns:
            Created artifact data
        """
        data = {
            'artifact_key': artifact_key,
            'run_id': run_id
        }
        if episode_id:
            data['episode_id'] = episode_id

        files = {'file': pickled_bytes}
        response = self.post("/artifacts/python", files=files, data=data)
        return response.json()

    def upload_scenario_stats_artifact(
        self,
        artifact_key: str,
        run_id: str,
        pickled_bytes: bytes,
        graph_type: str,
    ) -> Dict[str, Any]:
        """
        Upload scenario stats artifact (pickled Python dict data).
        This is an upsert operation - creates if doesn't exist, appends if it does.
        Run-level only (no episode_id support).

        Args:
            artifact_key: Artifact key identifier
            run_id: Run ID
            pickled_bytes: Pickled Python dict as bytes containing scenario stats
            graph_type: Graph display type - one of: 'line', 'bar', 'scatter',
                       'histogram', 'gaussian', 'heatmap', '3d_map'

        Returns:
            Created/updated artifact data
        """
        data = {
            'artifact_key': artifact_key,
            'run_id': run_id,
            'graph_type': graph_type
        }

        files = {'file': pickled_bytes}
        response = self.post("/artifacts/scenario_stats", files=files, data=data)
        return response.json()

    def download_artifact(
        self,
        run_id: str,
        episode_id: str,
        artifact_key: str
    ) -> bytes:
        """
        Download a blob artifact file.

        Args:
            run_id: Run ID
            episode_id: Episode ID
            artifact_key: Artifact key

        Returns:
            Artifact file content as bytes
        """
        endpoint = f"/artifacts/{run_id}/{episode_id}/{artifact_key}/download"
        response = self.get(endpoint)
        return response.content

    def upload_metrics(
        self,
        run_id: str,
        artifact_key: str,
        pickled_bytes: bytes,
        graph_type: str,
        episode_id: str | None = None,
    ) -> Dict[str, Any]:
        """
        Upload metrics artifact.

        Args:
            run_id: Run ID
            artifact_key: Artifact key
            pickled_bytes: Pickled metrics data as bytes
            graph_type: Optional new graph type
            episode_id: Optional new episode ID

        Returns:
            Updated artifact data
        """
        data = {
            "run_id": run_id,
            "artifact_key": artifact_key,
            'graph_type': graph_type
        }
        files = {'file': pickled_bytes}
        if episode_id:
            data["episode_id"] = episode_id

        response = self.post("/artifacts/metrics", files=files, data=data)
        return response.json()
