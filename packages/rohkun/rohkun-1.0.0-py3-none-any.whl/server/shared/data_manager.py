"""
Centralized Data Manager - SINGLE SOURCE OF TRUTH for all data operations.

This module ensures that all data flows through unified models and maintains
consistency across reports, database, and dashboards.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date, timedelta
from pathlib import Path

from server.shared.data_models import (
    MetricsModel, AnalysisDataModel, ReportModel, ProjectModel, 
    UsageModel, DashboardStatsModel, AnalysisStatus
)
from server.shared.enhanced_report_schema import (
    EnhancedReportModel, create_enhanced_report_from_analysis
)
from server.backend.database.supabase_client import get_supabase_service

logger = logging.getLogger(__name__)


def generate_report_name(folder_name: str, user_id: str, supabase) -> str:
    """
    Generate report name in format: "foldername" (sr no) (time and date)
    
    Args:
        folder_name: Name of the folder/project
        user_id: User ID to count reports for serial number
        supabase: Supabase client instance
        
    Returns:
        Formatted report name: "foldername" (1) (2025-11-08 22:30:45)
    """
    try:
        # Get count of reports for this user to generate serial number
        reports_response = supabase.table("reports").select("id").eq("user_id", user_id).execute()
        serial_number = len(reports_response.data or []) + 1
        
        # Format current date and time
        now = datetime.utcnow()
        date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate report name: "foldername" (sr no) (time and date)
        report_name = f'"{folder_name}" ({serial_number}) ({date_time_str})'
        
        return report_name
    except Exception as e:
        logger.warning(f"Error generating report name, using fallback: {e}")
        # Fallback to simple format if counting fails
        now = datetime.utcnow()
        date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        return f'"{folder_name}" (1) ({date_time_str})'


class DataManager:
    """
    Centralized data manager that ensures single source of truth.
    
    All data operations flow through this manager to maintain consistency
    across CLI, web app, database, and API responses.
    """
    
    def __init__(self):
        self.supabase = get_supabase_service()
    
    def create_analysis_report(
        self,
        project_id: str,
        user_id: str,
        raw_analysis_result: Dict[str, Any],
        project_name: str,
        report_name: Optional[str] = None,
        use_enhanced: bool = True
    ) -> ReportModel:
        """
        Create a unified report from raw analysis results.
        
        This is the SINGLE ENTRY POINT for all analysis data.
        All metrics and data flow through this method.
        
        Args:
            project_id: Project identifier
            user_id: User identifier  
            raw_analysis_result: Raw results from analyzer
            project_name: Project name for formatting
            report_name: Optional custom report name (if not provided, generates: "foldername" (sr no) (time and date))
            use_enhanced: If True, create enhanced report with confidence/security data
            
        Returns:
            ReportModel - single source of truth for all report data
        """
        logger.info(f"Creating unified report for project {project_id} (enhanced={use_enhanced})")
        
        # Generate report name if not provided: "foldername" (sr no) (time and date)
        if not report_name:
            report_name = generate_report_name(project_name, user_id, self.supabase)
            logger.info(f"Generated report name: {report_name}")
        
        # Create enhanced report with all new features
        if use_enhanced:
            enhanced_report = create_enhanced_report_from_analysis(
                project_id=project_id,
                user_id=user_id,
                raw_analysis_result=raw_analysis_result,
                project_name=project_name,
                report_name=report_name
            )
            
            # Convert to legacy format for backward compatibility
            legacy_report = enhanced_report.to_legacy_report_model()
            
            # Generate webapp URL for this report (PRE-BAKED LINK)
            from server.backend.config import settings
            if settings.web_app_url:
                webapp_url = f"{settings.web_app_url}/report-detail.html?id={project_id}"
                legacy_report.webapp_url = webapp_url
                logger.info(f"Generated webapp URL for enhanced report: {webapp_url}")
            
            # Store enhanced data in the report for database storage
            legacy_report._enhanced_data = enhanced_report
            
            logger.info(f"Created enhanced report with {enhanced_report.metrics.total_endpoints} endpoints, "
                       f"{enhanced_report.metrics.security_issues} security issues, "
                       f"{enhanced_report.metrics.reliable_coverage:.1f}% reliable coverage")
            
            return legacy_report
        
        # Legacy path (for backward compatibility)
        logger.info(f"Creating legacy report for project {project_id}")
        
        # Extract raw data
        connections = raw_analysis_result.get("connections", [])
        orphaned_endpoints = raw_analysis_result.get("orphaned_endpoints", [])
        orphaned_api_calls = raw_analysis_result.get("orphaned_api_calls", [])
        endpoints = raw_analysis_result.get("endpoints", [])
        api_calls = raw_analysis_result.get("api_calls", [])
        summary = raw_analysis_result.get("summary", {})
        dummy_data = raw_analysis_result.get("dummy_data", [])
        function_connections = raw_analysis_result.get("function_connections", [])
        orphaned_functions = raw_analysis_result.get("orphaned_functions", [])
        
        # Create analysis data model
        analysis_data = AnalysisDataModel(
            connections=connections,
            orphaned_endpoints=orphaned_endpoints,
            orphaned_api_calls=orphaned_api_calls,
            dummy_data=dummy_data,
            function_connections=function_connections,
            orphaned_functions=orphaned_functions,
            endpoints=endpoints,
            api_calls=api_calls,
            summary=summary
        )
        
        # Calculate unified metrics (SINGLE SOURCE OF TRUTH)
        metrics = self._calculate_unified_metrics(
            analysis_data=analysis_data,
            project_name=project_name,
            summary=summary
        )
        
        # Generate webapp URL for this report (PRE-BAKED LINK)
        from server.backend.config import settings
        webapp_url = None
        if settings.web_app_url:
            # Always generate the URL - this is the pre-baked link
            webapp_url = f"{settings.web_app_url}/report-detail.html?id={project_id}"
            logger.info(f"Generated webapp URL for report: {webapp_url}")
        
        # Generate report name if not provided: "foldername" (sr no) (time and date)
        if not report_name:
            report_name = generate_report_name(project_name, user_id, self.supabase)
            logger.info(f"Generated report name: {report_name}")
        
        # Create unified report model WITH pre-baked webapp URL
        report = ReportModel(
            project_id=project_id,
            user_id=user_id,
            report_name=report_name,
            report_display_name=report_name,
            webapp_url=webapp_url,  # PRE-BAKED LINK - ready to use immediately
            metrics=metrics,
            analysis_data=analysis_data
        )
        
        logger.info(f"Created unified report with {metrics.total_endpoints} endpoints, "
                   f"{metrics.connected_endpoints} connections, "
                   f"{metrics.tokens_saved} tokens saved")
        
        return report
    
    def _calculate_unified_metrics(
        self,
        analysis_data: AnalysisDataModel,
        project_name: str,
        summary: Dict[str, Any]
    ) -> MetricsModel:
        """
        Calculate unified metrics from analysis data.
        
        This ensures all metrics calculations are centralized and consistent.
        """
        # Import here to avoid circular imports
        from server.processor.metrics_calculator import calculate_metrics
        from server.processor.analysis_classifier import detect_framework
        
        # Basic counts
        files_processed = summary.get("files_processed", 0)
        lines_analyzed = summary.get("lines_analyzed", files_processed * 200)  # Estimate if missing
        total_endpoints = len(analysis_data.endpoints)
        total_api_calls = len(analysis_data.api_calls)
        connected_endpoints = len(analysis_data.connections)
        orphaned_endpoints = len(analysis_data.orphaned_endpoints)
        orphaned_api_calls = len(analysis_data.orphaned_api_calls)
        uncertain_connections = len(analysis_data.uncertain_patterns)
        
        # Function analysis counts
        total_functions = summary.get("total_functions", 0)
        total_function_calls = summary.get("total_function_calls", 0)
        connected_functions = summary.get("connected_functions", 0)
        orphaned_functions = summary.get("orphaned_functions", 0)
        missing_functions = summary.get("missing_functions", 0)
        
        # Framework detection
        framework = detect_framework(analysis_data.endpoints, analysis_data.api_calls)
        
        # Time saved calculation removed
        
        # Calculate token savings
        estimated_codebase_tokens = lines_analyzed * 10
        # Token savings based on connections found - each connection saves manual analysis time
        base_tokens_per_connection = 50  # Conservative estimate per connection
        tokens_saved = connected_endpoints * base_tokens_per_connection
        savings_percent = int((tokens_saved / max(estimated_codebase_tokens, 1)) * 100) if estimated_codebase_tokens > 0 else 0
        
        # Cost calculation (GPT-4 pricing)
        input_cost_per_1k = 0.03
        output_cost_per_1k = 0.06
        estimated_full_cost = (estimated_codebase_tokens / 1000) * (input_cost_per_1k + output_cost_per_1k * 2)
        cost_savings = estimated_full_cost * 0.7  # Conservative estimate
        
        # Create unified metrics model
        metrics = MetricsModel(
            files_processed=files_processed,
            lines_analyzed=lines_analyzed,
            total_endpoints=total_endpoints,
            total_api_calls=total_api_calls,
            connected_endpoints=connected_endpoints,
            orphaned_endpoints=orphaned_endpoints,
            orphaned_api_calls=orphaned_api_calls,
            uncertain_connections=uncertain_connections,
            framework=framework,
            tokens_saved=tokens_saved,
            cost_savings_usd=cost_savings,
            savings_percent=savings_percent,

            project_name=project_name,
            analyzed_date=datetime.utcnow().isoformat()
        )
        
        # Calculate derived metrics
        metrics.calculate_derived_metrics()
        
        return metrics
    

    
    def save_report_to_database(self, report: ReportModel) -> bool:
        """
        Save unified report to database.
        
        This ensures consistent data storage across all tables.
        Includes enhanced data (confidence, security) if available.
        """
        try:
            # Check if this report has enhanced data
            enhanced_report = getattr(report, '_enhanced_data', None)
            
            # Prepare base report data
            report_data = {
                "user_id": report.user_id,
                "project_id": report.project_id,
                "analysis_version": report.analysis_version,
                "summary": {
                    # Store unified metrics as single source of truth
                    "metrics": report.metrics.model_dump(mode='json'),
                    # Keep legacy fields for backward compatibility
                    "tokens_saved": report.metrics.tokens_saved,
                    
                    # Store report naming information
                    "report_name": report.report_name,
                    "report_display_name": report.report_display_name,

                    # Store supporting data for report generation (match expected structure)
                    "endpoints": report.analysis_data.endpoints,
                    "api_calls": report.analysis_data.api_calls,
                    "connections": report.analysis_data.connections,
                    # FIXED: Store orphaned data at root level for frontend compatibility
                    "orphaned_endpoints": report.analysis_data.orphaned_endpoints,
                    "orphaned_api_calls": report.analysis_data.orphaned_api_calls,
                    # Include original summary data
                    **report.analysis_data.summary
                },
                "analysis_data": report.analysis_data.model_dump(mode='json'),
                "created_at": report.created_at.isoformat()
            }
            
            # Add enhanced data if available
            if enhanced_report:
                # Add enhanced metrics to summary
                report_data["summary"]["enhanced_metrics"] = enhanced_report.metrics.model_dump(mode='json')
                
                # Add accuracy report
                if enhanced_report.accuracy_report:
                    report_data["summary"]["accuracy_report"] = enhanced_report.accuracy_report.model_dump(mode='json')
                
                # Add security summary
                if enhanced_report.security_summary:
                    report_data["summary"]["security_summary"] = enhanced_report.security_summary.model_dump(mode='json')
                
                # Add security issues to analysis_data
                report_data["analysis_data"]["security_issues"] = enhanced_report.analysis_data.security_issues
                report_data["analysis_data"]["functions"] = enhanced_report.analysis_data.functions
                report_data["analysis_data"]["function_calls"] = enhanced_report.analysis_data.function_calls
                
                logger.info(f"Saving enhanced report with {enhanced_report.metrics.security_issues} security issues, "
                           f"{enhanced_report.metrics.reliable_coverage:.1f}% reliable coverage")
            
            
            # Use upsert to handle existing reports (project_id is unique)
            response = self.supabase.table("reports").upsert(report_data, on_conflict="project_id").execute()
            
            if response.data:
                logger.info(f"✅ Saved unified report to database for project {report.project_id}")
                logger.info(f"Report data saved: {response.data[0]['id'] if response.data else 'No ID'}")
                return True
            else:
                logger.error(f"❌ Failed to save report to database: no data returned")
                logger.error(f"Save response: {response}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error saving report to database: {e}")
            logger.error(f"Report data that failed to save: {report_data}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
            return False
    
    def get_report_from_database(self, project_id: str, user_id: str) -> Optional[ReportModel]:
        """
        Retrieve unified report from database.
        
        Returns the canonical ReportModel with all data.
        """
        try:
            response = self.supabase.table("reports").select("*").eq("project_id", project_id).single().execute()
            
            if not response.data:
                return None
            
            data = response.data
            
            # Reconstruct metrics from stored data
            summary = data.get("summary", {})
            metrics_dict = summary.get("metrics", {})
            
            if metrics_dict:
                # Use stored unified metrics
                metrics = MetricsModel(**metrics_dict)
            else:
                # Fallback: reconstruct from legacy fields
                metrics = MetricsModel(
                    tokens_saved=summary.get("tokens_saved", 0),

                    # Add other fields with defaults
                )
            
            # Reconstruct analysis data
            analysis_data_dict = data.get("analysis_data", {})
            analysis_data = AnalysisDataModel(**analysis_data_dict)
            
            # Create unified report model
            report = ReportModel(
                id=data.get("id"),
                project_id=data["project_id"],
                user_id=data["user_id"],
                metrics=metrics,
                analysis_data=analysis_data,
                analysis_version=data.get("analysis_version", "1.0"),
                created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat()))
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error retrieving report from database: {e}")
            return None
    
    def update_usage_from_report(
        self,
        user_id: str,
        report: ReportModel,
        subscription_tier: str,
        is_overage: bool = False
    ) -> bool:
        """
        Update user usage from completed report.
        
        This ensures usage tracking is consistent with report metrics.
        """
        try:
            # Get or create current usage period
            usage = self.get_current_usage(user_id, subscription_tier)
            
            # Add analysis usage from report metrics
            usage.add_analysis_usage(report.metrics, is_overage)
            
            # Save updated usage
            return self.save_usage_to_database(usage)
            
        except Exception as e:
            logger.error(f"Error updating usage from report: {e}")
            return False
    
    def get_current_usage(self, user_id: str, subscription_tier: str) -> UsageModel:
        """
        Get current usage period for user.
        
        Creates new usage record if none exists for current period.
        """
        # Calculate current period
        today = date.today()
        period_start = today.replace(day=1)
        if period_start.month == 12:
            period_end = period_start.replace(year=period_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            period_end = period_start.replace(month=period_start.month + 1, day=1) - timedelta(days=1)
        
        try:
            # Try to get existing usage record
            response = self.supabase.table("usage_records").select("*").eq("user_id", user_id).eq("period_start", period_start.isoformat()).execute()
            
            if response.data:
                data = response.data[0]
                return UsageModel(
                    user_id=data["user_id"],
                    period_start=data["period_start"],
                    period_end=data["period_end"],
                    credits_granted=self._get_credits_for_tier(subscription_tier),
                    credits_consumed=data.get("analyses_count", 0) or 0,
                    overage_analyses=data.get("overage_analyses_count", 0) or 0,
                    storage_bytes_used=data.get("storage_bytes_used", 0) or 0,
                    total_tokens_saved=data.get("tokens_saved_total", 0) or 0,

                    subscription_tier=subscription_tier
                )
            else:
                # Create new usage record
                return UsageModel(
                    user_id=user_id,
                    period_start=period_start.isoformat(),
                    period_end=period_end.isoformat(),
                    credits_granted=self._get_credits_for_tier(subscription_tier),
                    subscription_tier=subscription_tier
                )
                
        except Exception as e:
            logger.error(f"Error getting current usage: {e}")
            # Return default usage model
            return UsageModel(
                user_id=user_id,
                period_start=period_start.isoformat(),
                period_end=period_end.isoformat(),
                credits_granted=self._get_credits_for_tier(subscription_tier),
                subscription_tier=subscription_tier
            )
    
    def _get_credits_for_tier(self, tier: str) -> int:
        """Get credits granted for subscription tier."""
        tier_credits = {
            "free": 5,
            "pro": 50,
            "enterprise": 200
        }
        return tier_credits.get(tier.lower(), 5)
    
    def save_usage_to_database(self, usage: UsageModel) -> bool:
        """Save usage model to database."""
        try:
            update_data = {
                "analyses_count": usage.credits_consumed,
                "overage_analyses_count": usage.overage_analyses,
                "storage_bytes_used": usage.storage_bytes_used,
                "tokens_saved_total": usage.total_tokens_saved,
                "updated_at": usage.updated_at.isoformat()
            }
            
            # Upsert usage record
            upsert_data = {
                "user_id": usage.user_id,
                "period_start": usage.period_start,
                "period_end": usage.period_end,
                **update_data
            }
            
            response = self.supabase.table("usage_records").upsert(upsert_data, on_conflict="user_id,period_start").execute()
            
            if response.data:
                logger.info(f"Saved usage to database for user {usage.user_id}")
                return True
            else:
                logger.error("Failed to save usage: no data returned")
                return False
                
        except Exception as e:
            logger.error(f"Error saving usage to database: {e}")
            return False
    
    def get_dashboard_stats(self, user_id: str) -> DashboardStatsModel:
        """
        Get unified dashboard statistics.
        
        This aggregates data from multiple sources into a single model.
        """
        try:
            # Get user's projects
            projects_response = self.supabase.table("projects").select("*").eq("user_id", user_id).eq("is_deleted", False).execute()
            projects_data = projects_response.data or []
            
            projects = [
                ProjectModel(
                    id=p["id"],
                    user_id=p["user_id"],
                    name=p["name"],
                    original_filename=p["original_filename"],
                    file_size_bytes=p["file_size_bytes"],
                    status=AnalysisStatus(p["status"]),
                    uploaded_at=datetime.fromisoformat(p["uploaded_at"]),
                    analysis_started_at=datetime.fromisoformat(p["analysis_started_at"]) if p.get("analysis_started_at") else None,
                    analysis_completed_at=datetime.fromisoformat(p["analysis_completed_at"]) if p.get("analysis_completed_at") else None,
                    file_storage_path=p.get("file_storage_path"),
                    file_hash=p.get("file_hash"),
                    error_message=p.get("error_message"),
                    api_key_id=p.get("api_key_id"),
                    is_deleted=p.get("is_deleted", False)
                )
                for p in projects_data
            ]
            
            # Get user's current usage
            try:
                profile_response = self.supabase.table("profiles").select("subscription_tier").eq("id", user_id).single().execute()
                subscription_tier = profile_response.data.get("subscription_tier", "free") if profile_response.data else "free"
            except Exception:
                # User doesn't exist or other error - use default
                subscription_tier = "free"
            
            usage = self.get_current_usage(user_id, subscription_tier)
            
            # Create dashboard stats
            stats = DashboardStatsModel.from_usage_and_projects(user_id, usage, projects)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            # Return empty stats
            return DashboardStatsModel(user_id=user_id)
    
    def generate_formatted_reports(self, report: ReportModel) -> Dict[str, str]:
        """
        Generate formatted reports from unified report model.
        
        This ensures all formatted outputs come from the same source.
        """
        try:
            return report.generate_formatted_reports()
        except Exception as e:
            logger.error(f"Error generating formatted reports: {e}")
            return {
                'full': f"Error generating report: {str(e)}",
                'short': f"Error generating report: {str(e)}",
                'summary': f"Error generating report: {str(e)}",
                'detail_files': {}
            }


# Global instance for use throughout the application
data_manager = DataManager()