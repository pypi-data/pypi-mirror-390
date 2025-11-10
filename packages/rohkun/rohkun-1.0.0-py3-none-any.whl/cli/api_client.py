"""
Unified API client for CLI to ensure consistency with backend responses.

This module provides a single source of truth for API calls, ensuring
the CLI and frontend use the same endpoints and handle responses consistently.
"""

import requests
from typing import Dict, List, Optional, Any
from cli.auth import get_auth_token
from cli.config import get_config


class APIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


def _get_headers() -> Dict[str, str]:
    """Get authentication headers."""
    token = get_auth_token()
    if not token:
        raise APIError("Not authenticated. Please run 'rohkun login' first.")
    return {"Authorization": f"Bearer {token}"}


def _make_request(
    method: str,
    endpoint: str,
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    timeout: int = 30
) -> requests.Response:
    """
    Make an authenticated API request.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint (e.g., "/projects")
        params: Query parameters
        json_data: JSON body for POST/PUT requests
        timeout: Request timeout in seconds
        
    Returns:
        Response object
        
    Raises:
        APIError: If request fails
    """
    config = get_config()
    headers = _get_headers()
    
    url = f"{config.api_url}{endpoint}"
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            timeout=timeout
        )
        
        if response.status_code >= 400:
            error_detail = None
            if response.headers.get("content-type") == "application/json":
                try:
                    error_detail = response.json().get("detail", "Unknown error")
                except:
                    error_detail = response.text
            else:
                error_detail = response.text
                
            raise APIError(
                f"API request failed: {error_detail}",
                status_code=response.status_code,
                response=error_detail
            )
        
        return response
        
    except requests.exceptions.RequestException as e:
        raise APIError(f"Network error: {str(e)}")


def get_projects(
    framework: Optional[str] = None,
    status: Optional[str] = None,
    min_endpoints: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get list of projects.
    
    Backend returns: { "projects": [...], "summary": {...} }
    
    Args:
        framework: Filter by framework
        status: Filter by status
        min_endpoints: Filter by minimum endpoints
        
    Returns:
        Dictionary with "projects" list and "summary" dict
    """
    params = {}
    if framework:
        params["framework"] = framework
    if status:
        params["status"] = status
    if min_endpoints is not None:
        params["min_endpoints"] = min_endpoints
    
    response = _make_request("GET", "/projects", params=params)
    return response.json()


def get_project(project_id: str) -> Dict[str, Any]:
    """
    Get a single project by ID.
    
    Args:
        project_id: Project UUID
        
    Returns:
        Project dictionary
    """
    response = _make_request("GET", f"/projects/{project_id}")
    return response.json()


def delete_project(project_id: str) -> Dict[str, Any]:
    """
    Delete a project.
    
    Args:
        project_id: Project UUID
        
    Returns:
        Response dictionary with message and project_id
    """
    response = _make_request("DELETE", f"/projects/{project_id}")
    return response.json()


def find_project_by_hash(project_hash: str) -> Optional[Dict[str, Any]]:
    """
    Find a project by its project_hash.
    
    Args:
        project_hash: Project hash (e.g., "RHKN-XXXXXX")
        
    Returns:
        Project dictionary if found, None otherwise
    """
    try:
        data = get_projects()
        projects = data.get("projects", [])
        
        for project in projects:
            if project.get("project_hash") == project_hash:
                return project
        
        return None
    except APIError:
        return None

