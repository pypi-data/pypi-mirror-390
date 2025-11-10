"""
Unified Aggregation Service - Single Source of Truth for Metrics Calculation.

This service provides consistent aggregation logic across all parts of the application
to ensure metrics are calculated the same way everywhere.
"""

import logging
from typing import Dict, Any, List
from server.backend.database.supabase_client import get_supabase_service

logger = logging.getLogger(__name__)


class AggregationService:
    """Centralized service for aggregating metrics across projects and users."""
    
    def __init__(self):
        self.supabase = get_supabase_service()
    
    def aggregate_project_metrics(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate metrics from a list of projects.
        
        Args:
            projects: List of project dictionaries with fields like:
                - status
                - tokens_saved
                - total_endpoints
                - total_api_calls
                - connected_endpoints
                - detected_framework
        
        Returns:
            Dictionary with aggregated metrics:
            - total_projects: Total number of projects
            - completed_projects: Number of completed projects
            - total_tokens_saved: Sum of tokens saved
            - total_endpoints: Sum of total endpoints
            - total_api_calls: Sum of total API calls
            - total_connections: Sum of connected endpoints
            - success_rate: Percentage of completed projects
            - frameworks: Dictionary of framework counts
        """
        if not projects:
            return {
                "total_projects": 0,
                "completed_projects": 0,
                "total_tokens_saved": 0,
                "total_endpoints": 0,
                "total_api_calls": 0,
                "total_connections": 0,
                "success_rate": 0.0,
                "frameworks": {}
            }
        
        total_projects = len(projects)
        completed_projects = len([p for p in projects if p.get("status") == "completed"])
        
        total_tokens_saved = sum(
            p.get("tokens_saved", 0) or 0 
            for p in projects
        )
        
        total_endpoints = sum(
            p.get("total_endpoints", 0) or 0 
            for p in projects
        )
        
        total_api_calls = sum(
            p.get("total_api_calls", 0) or 0 
            for p in projects
        )
        
        total_connections = sum(
            p.get("connected_endpoints", 0) or 0 
            for p in projects
        )
        
        # Calculate success rate
        success_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0.0
        
        # Count frameworks
        frameworks = {}
        for project in projects:
            framework = project.get("detected_framework")
            if framework:
                frameworks[framework] = frameworks.get(framework, 0) + 1
        
        return {
            "total_projects": total_projects,
            "completed_projects": completed_projects,
            "total_tokens_saved": total_tokens_saved,
            "total_endpoints": total_endpoints,
            "total_api_calls": total_api_calls,
            "total_connections": total_connections,
            "success_rate": round(success_rate, 2),
            "frameworks": frameworks
        }
    
    def aggregate_api_key_metrics(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate metrics for API key statistics.
        
        Args:
            projects: List of project dictionaries
        
        Returns:
            Dictionary with:
            - total_tokens_saved: Sum of tokens saved
            - total_time_saved_minutes: Estimated time saved in minutes
        """
        if not projects:
            return {
                "total_tokens_saved": 0,
                "total_time_saved_minutes": 0
            }
        
        total_tokens_saved = sum(
            p.get("tokens_saved", 0) or 0 
            for p in projects
        )
        
        # Estimate time saved: ~2 minutes per 1000 tokens saved
        # This is a rough estimate based on typical API analysis time
        total_time_saved_minutes = (total_tokens_saved / 1000.0) * 2.0
        
        return {
            "total_tokens_saved": total_tokens_saved,
            "total_time_saved_minutes": round(total_time_saved_minutes, 2)
        }
    
    def aggregate_user_metrics(self, user_id: str) -> Dict[str, Any]:
        """
        Aggregate metrics for a specific user.
        
        Args:
            user_id: User UUID
        
        Returns:
            Dictionary with:
            - total_tokens_saved: Sum of tokens saved across all user projects
            - total_time_saved_minutes: Estimated time saved in minutes
            - total_projects: Total number of projects
        """
        try:
            # Get all projects for user
            projects_response = self.supabase.table("projects").select(
                "id, status, tokens_saved"
            ).eq("user_id", user_id).eq("is_deleted", False).execute()
            
            projects = projects_response.data or []
            
            total_projects = len(projects)
            total_tokens_saved = sum(
                p.get("tokens_saved", 0) or 0 
                for p in projects
            )
            
            # Estimate time saved: ~2 minutes per 1000 tokens saved
            total_time_saved_minutes = (total_tokens_saved / 1000.0) * 2.0
            
            return {
                "total_tokens_saved": total_tokens_saved,
                "total_time_saved_minutes": round(total_time_saved_minutes, 2),
                "total_projects": total_projects
            }
        except Exception as e:
            logger.error(f"Error aggregating user metrics for {user_id}: {e}")
            return {
                "total_tokens_saved": 0,
                "total_time_saved_minutes": 0,
                "total_projects": 0
            }
    
    def aggregate_admin_metrics(self) -> Dict[str, Any]:
        """
        Aggregate metrics for admin dashboard.
        
        Returns:
            Dictionary with:
            - analysis_metrics: Dictionary containing:
                - total_tokens_saved: Total tokens saved across all projects
                - total_time_saved_hours: Estimated time saved in hours
        """
        try:
            # Get all projects
            projects_response = self.supabase.table("projects").select(
                "id, tokens_saved"
            ).eq("is_deleted", False).execute()
            
            projects = projects_response.data or []
            
            total_tokens_saved = sum(
                p.get("tokens_saved", 0) or 0 
                for p in projects
            )
            
            # Estimate time saved: ~2 minutes per 1000 tokens saved
            total_time_saved_minutes = (total_tokens_saved / 1000.0) * 2.0
            total_time_saved_hours = total_time_saved_minutes / 60.0
            
            return {
                "analysis_metrics": {
                    "total_tokens_saved": total_tokens_saved,
                    "total_time_saved_hours": round(total_time_saved_hours, 2)
                }
            }
        except Exception as e:
            logger.error(f"Error aggregating admin metrics: {e}")
            return {
                "analysis_metrics": {
                    "total_tokens_saved": 0,
                    "total_time_saved_hours": 0.0
                }
            }


# Create singleton instance
aggregation_service = AggregationService()

