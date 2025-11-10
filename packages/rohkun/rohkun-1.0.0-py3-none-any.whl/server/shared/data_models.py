"""
Unified data models - SINGLE SOURCE OF TRUTH for all analysis data.

This module defines the canonical data structures that serve as the single source
of truth for all reports, database storage, and dashboard displays.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class AnalysisStatus(str, Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MetricsModel(BaseModel):
    """
    SINGLE SOURCE OF TRUTH for all analysis metrics.
    
    This model is created once during analysis and used everywhere:
    - CLI output
    - Web dashboard
    - Database aggregations
    - API responses
    - Report generation
    
    No duplication - one entity represented everywhere.
    """
    # Core analysis metrics
    files_processed: int = 0
    lines_analyzed: int = 0
    total_endpoints: int = 0
    total_api_calls: int = 0
    connected_endpoints: int = 0
    orphaned_endpoints: int = 0
    orphaned_api_calls: int = 0
    uncertain_connections: int = 0
    
    # Function analysis metrics
    total_functions: int = 0
    total_function_calls: int = 0
    connected_functions: int = 0
    orphaned_functions: int = 0
    missing_functions: int = 0
    
    # Framework and technology detection
    framework: str = "Unknown"
    detected_technologies: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Calculated savings (derived from analysis)
    tokens_saved: int = 0
    cost_savings_usd: float = 0.0
    savings_percent: int = 0
    time_saved_minutes: int = 0
    
    # Analysis metadata
    project_name: str = "unknown"
    analyzed_date: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    analysis_version: str = "1.0"
    
    # Quality metrics
    confidence_score: float = 0.0  # Overall confidence in analysis (0-1)
    coverage_percent: int = 0  # Percentage of codebase analyzed
    
    def calculate_derived_metrics(self) -> None:
        """Calculate derived metrics from base metrics."""
        # Calculate confidence based on connections found
        total_items = self.total_endpoints + self.total_api_calls
        if total_items > 0:
            connected_items = self.connected_endpoints
            self.confidence_score = min(1.0, connected_items / total_items)
        
        # Calculate coverage
        if self.files_processed > 0:
            # Estimate coverage based on files processed vs typical project size
            estimated_total_files = max(self.files_processed, 50)  # Minimum baseline
            self.coverage_percent = min(100, int((self.files_processed / estimated_total_files) * 100))


class AnalysisDataModel(BaseModel):
    """
    Core analysis data structure - contains all raw analysis results.
    
    This is the canonical representation of analysis findings.
    All formatted reports are generated from this data.
    """
    # Raw analysis results
    connections: List[Dict[str, Any]] = Field(default_factory=list)
    orphaned_endpoints: List[Dict[str, Any]] = Field(default_factory=list)
    orphaned_api_calls: List[Dict[str, Any]] = Field(default_factory=list)
    dummy_data: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Function analysis results
    function_connections: List[Dict[str, Any]] = Field(default_factory=list)
    orphaned_functions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Supporting data for report generation
    endpoints: List[Dict[str, Any]] = Field(default_factory=list)
    api_calls: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Analysis metadata
    summary: Dict[str, Any] = Field(default_factory=dict)
    
    # Quality indicators
    needs_review: List[Dict[str, Any]] = Field(default_factory=list)
    uncertain_patterns: List[Dict[str, Any]] = Field(default_factory=list)


class ProjectModel(BaseModel):
    """
    Unified project model - single source of truth for project data.
    """
    # Core identifiers
    id: str
    user_id: str
    
    # Project metadata
    name: str
    original_filename: str
    file_size_bytes: int
    
    # Status tracking
    status: AnalysisStatus
    uploaded_at: datetime
    analysis_started_at: Optional[datetime] = None
    analysis_completed_at: Optional[datetime] = None
    
    # Storage information
    file_storage_path: Optional[str] = None
    file_hash: Optional[str] = None
    
    # Error handling
    error_message: Optional[str] = None
    
    # API key tracking (if created via API)
    api_key_id: Optional[str] = None
    
    # Soft delete
    is_deleted: bool = False


class ReportModel(BaseModel):
    """
    Unified report model - single source of truth for all report data.
    
    This model contains:
    1. Raw analysis data (for regenerating reports)
    2. Calculated metrics (single source of truth)
    3. Metadata for tracking and auditing
    
    All formatted outputs are generated from this model on-demand.
    """
    # Core identifiers
    id: Optional[str] = None
    project_id: str
    user_id: str
    
    # Report naming and identification
    report_name: str = ""  # User-customizable report name
    report_display_name: str = ""  # Display name (defaults to report_name or project name)
    
    # Single source of truth for metrics
    metrics: MetricsModel
    
    # Raw analysis data (for report generation)
    analysis_data: AnalysisDataModel
    
    # Report metadata
    analysis_version: str = "1.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Web app integration
    webapp_url: Optional[str] = None  # URL to view this report in webapp
    
    # Cached formatted reports (optional - can be regenerated)
    cached_reports: Optional[Dict[str, str]] = None
    
    def generate_formatted_reports(self) -> Dict[str, str]:
        """
        Generate all formatted report variants from analysis data.
        
        Returns:
            Dictionary with report formats: {
                'full': full_report_text,
                'short': short_report_text,
                'summary': summary_text,
                'detail_files': detail_files_json
            }
        """
        # Import here to avoid circular imports
        from server.processor.report_formatter import ReportFormatter
        
        # Use report display name or fallback to project name
        display_name = self.report_display_name or self.report_name or self.metrics.project_name
        formatter = ReportFormatter(project_name=display_name)
        
        # Convert analysis data to format expected by formatter
        formatted_report, short_copy, full_copy, detail_files, _ = formatter.format_report(
            connections=self.analysis_data.connections,
            orphaned_endpoints=self.analysis_data.orphaned_endpoints,
            orphaned_api_calls=self.analysis_data.orphaned_api_calls,
            endpoints=self.analysis_data.endpoints,
            api_calls=self.analysis_data.api_calls,
            summary=self.analysis_data.summary,
            dummy_data=self.analysis_data.dummy_data,
            function_connections=self.analysis_data.function_connections,
            orphaned_functions=self.analysis_data.orphaned_functions
        )
        
        # Add webapp URL to reports if available
        webapp_link = ""
        if self.webapp_url:
            webapp_link = f"\n\n🔗 View this report online: {self.webapp_url}\n"
        
        return {
            'full': formatted_report + webapp_link,
            'short': short_copy + webapp_link,
            'summary': full_copy + webapp_link,
            'detail_files': detail_files
        }


class UsageModel(BaseModel):
    """
    Unified usage tracking model - single source of truth for user usage.
    
    This model aggregates all usage data and serves as the canonical source
    for billing, dashboard stats, and usage limits.
    """
    # Core identifiers
    user_id: str
    period_start: str  # ISO date string
    period_end: str    # ISO date string
    
    # Credit-based usage tracking
    credits_granted: int = 0      # Credits from subscription
    credits_consumed: int = 0     # Credits used from subscription
    overage_analyses: int = 0     # Analyses beyond subscription (billable)
    
    # Storage usage
    storage_bytes_used: int = 0
    
    # Aggregated metrics (from all reports in period)
    total_tokens_saved: int = 0
    total_time_saved_minutes: int = 0
    total_projects_analyzed: int = 0
    
    # Subscription information
    subscription_tier: str = "free"
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def credits_remaining(self) -> int:
        """Calculate remaining credits."""
        return max(0, self.credits_granted - self.credits_consumed)
    
    @property
    def is_in_overage(self) -> bool:
        """Check if user is in overage billing."""
        return self.credits_remaining == 0 and self.overage_analyses > 0
    
    def add_analysis_usage(self, metrics: MetricsModel, is_overage: bool = False) -> None:
        """
        Add usage from a completed analysis.
        
        Args:
            metrics: The MetricsModel from the completed analysis
            is_overage: Whether this analysis should be counted as overage
        """
        if is_overage:
            self.overage_analyses += 1
        else:
            self.credits_consumed += 1
        
        # Aggregate metrics
        self.total_tokens_saved += metrics.tokens_saved
        self.total_time_saved_minutes += metrics.time_saved_minutes
        self.total_projects_analyzed += 1
        
        # Update timestamp
        self.updated_at = datetime.utcnow()


class DashboardStatsModel(BaseModel):
    """
    Unified dashboard statistics model.
    
    This model aggregates data from multiple sources to provide
    a single source of truth for dashboard displays.
    """
    # User identifier
    user_id: str
    
    # Project statistics
    total_projects: int = 0
    completed_projects: int = 0
    failed_projects: int = 0
    
    # Usage statistics (aggregated from UsageModel)
    total_analyses: int = 0
    total_tokens_saved: int = 0
    total_time_saved_hours: float = 0.0
    
    # Current period usage
    current_period_analyses: int = 0
    current_period_overage: int = 0
    credits_remaining: int = 0
    
    # Subscription information
    subscription_tier: str = "free"
    
    # Calculated at generation time
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_usage_and_projects(
        cls,
        user_id: str,
        usage: UsageModel,
        projects: List[ProjectModel]
    ) -> 'DashboardStatsModel':
        """
        Create dashboard stats from usage and project data.
        
        Args:
            user_id: User identifier
            usage: Current usage model
            projects: List of user's projects
            
        Returns:
            DashboardStatsModel with aggregated statistics
        """
        completed_projects = [p for p in projects if p.status == AnalysisStatus.COMPLETED]
        failed_projects = [p for p in projects if p.status == AnalysisStatus.FAILED]
        
        return cls(
            user_id=user_id,
            total_projects=len(projects),
            completed_projects=len(completed_projects),
            failed_projects=len(failed_projects),
            total_analyses=usage.total_projects_analyzed,
            total_tokens_saved=usage.total_tokens_saved,
            total_time_saved_hours=usage.total_time_saved_minutes / 60.0,
            current_period_analyses=usage.credits_consumed + usage.overage_analyses,
            current_period_overage=usage.overage_analyses,
            credits_remaining=usage.credits_remaining,
            subscription_tier=usage.subscription_tier
        )