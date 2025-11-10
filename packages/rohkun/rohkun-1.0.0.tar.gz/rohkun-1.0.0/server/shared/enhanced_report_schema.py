"""
Enhanced Report Schema with Confidence and Security Integration

This extends the existing report models to include:
1. Confidence-based accuracy reporting
2. Security issue tracking
3. Function analysis
4. All new analysis features

SINGLE SOURCE OF TRUTH for enhanced report data.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

from server.shared.accuracy_report_schema import AccuracyReport


class SecuritySummary(BaseModel):
    """Summary of security issues found in analysis."""
    total_issues: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0
    
    # Detection metadata
    detection_method: str = "regex"
    detection_method_name: str = "Regex Pattern Matching"
    accuracy_range: str = "60-85%"
    false_positive_risk: str = "Medium"
    
    # Categories detected
    categories: List[str] = Field(default_factory=list)
    
    def total_critical_high(self) -> int:
        """Get count of critical and high severity issues."""
        return self.critical + self.high


class EnhancedMetrics(BaseModel):
    """
    Enhanced metrics including confidence and security data.
    
    Extends MetricsModel with additional analysis features.
    """
    # Core analysis metrics (from MetricsModel)
    files_processed: int = 0
    lines_analyzed: int = 0
    total_endpoints: int = 0
    total_api_calls: int = 0
    connected_endpoints: int = 0
    orphaned_endpoints: int = 0
    orphaned_api_calls: int = 0
    uncertain_connections: int = 0
    
    # Function analysis
    total_functions: int = 0
    total_function_calls: int = 0
    connected_functions: int = 0
    orphaned_functions: int = 0
    missing_functions: int = 0
    
    # Security analysis
    security_issues: int = 0
    security_critical: int = 0
    security_high: int = 0
    security_medium: int = 0
    security_low: int = 0
    
    # Confidence distribution
    endpoints_certain: int = 0
    endpoints_high: int = 0
    endpoints_medium: int = 0
    endpoints_low: int = 0
    endpoints_unknown: int = 0
    
    api_calls_certain: int = 0
    api_calls_high: int = 0
    api_calls_medium: int = 0
    api_calls_low: int = 0
    api_calls_unknown: int = 0
    
    # Calculated accuracy
    estimated_endpoint_accuracy: float = 0.0  # Percentage
    estimated_api_call_accuracy: float = 0.0  # Percentage
    reliable_coverage: float = 0.0  # Percentage of CERTAIN + HIGH
    
    # Framework and technology
    framework: str = "Unknown"
    detected_technologies: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Savings metrics
    tokens_saved: int = 0
    cost_savings_usd: float = 0.0
    savings_percent: int = 0
    
    # Metadata
    project_name: str = "unknown"
    analyzed_date: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    analysis_version: str = "2.0"


class EnhancedAnalysisData(BaseModel):
    """
    Enhanced analysis data including all new features.
    
    Extends AnalysisDataModel with security and function analysis.
    """
    # Core analysis results
    connections: List[Dict[str, Any]] = Field(default_factory=list)
    orphaned_endpoints: List[Dict[str, Any]] = Field(default_factory=list)
    orphaned_api_calls: List[Dict[str, Any]] = Field(default_factory=list)
    dummy_data: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Function analysis
    function_connections: List[Dict[str, Any]] = Field(default_factory=list)
    orphaned_functions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Security analysis
    security_issues: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Supporting data
    endpoints: List[Dict[str, Any]] = Field(default_factory=list)
    api_calls: List[Dict[str, Any]] = Field(default_factory=list)
    functions: List[Dict[str, Any]] = Field(default_factory=list)
    function_calls: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Analysis metadata
    summary: Dict[str, Any] = Field(default_factory=dict)


class EnhancedReportModel(BaseModel):
    """
    Enhanced report model with confidence and security integration.
    
    This is the SINGLE SOURCE OF TRUTH for all enhanced report data.
    """
    # Core identifiers
    id: Optional[str] = None
    project_id: str
    user_id: str
    
    # Report naming
    report_name: str = ""
    report_display_name: str = ""
    
    # Enhanced metrics (includes confidence and security)
    metrics: EnhancedMetrics
    
    # Enhanced analysis data (includes security and functions)
    analysis_data: EnhancedAnalysisData
    
    # Accuracy report (confidence distribution and recommendations)
    accuracy_report: Optional[AccuracyReport] = None
    
    # Security summary
    security_summary: Optional[SecuritySummary] = None
    
    # Report metadata
    analysis_version: str = "2.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Web app integration
    webapp_url: Optional[str] = None
    
    def to_legacy_report_model(self):
        """Convert to legacy ReportModel for backward compatibility."""
        from server.shared.data_models import ReportModel, MetricsModel, AnalysisDataModel
        
        # Convert enhanced metrics to legacy metrics
        legacy_metrics = MetricsModel(
            files_processed=self.metrics.files_processed,
            lines_analyzed=self.metrics.lines_analyzed,
            total_endpoints=self.metrics.total_endpoints,
            total_api_calls=self.metrics.total_api_calls,
            connected_endpoints=self.metrics.connected_endpoints,
            orphaned_endpoints=self.metrics.orphaned_endpoints,
            orphaned_api_calls=self.metrics.orphaned_api_calls,
            uncertain_connections=self.metrics.uncertain_connections,
            total_functions=self.metrics.total_functions,
            total_function_calls=self.metrics.total_function_calls,
            connected_functions=self.metrics.connected_functions,
            orphaned_functions=self.metrics.orphaned_functions,
            missing_functions=self.metrics.missing_functions,
            framework=self.metrics.framework,
            detected_technologies=self.metrics.detected_technologies,
            tokens_saved=self.metrics.tokens_saved,
            cost_savings_usd=self.metrics.cost_savings_usd,
            savings_percent=self.metrics.savings_percent,
            project_name=self.metrics.project_name,
            analyzed_date=self.metrics.analyzed_date,
            analysis_version=self.metrics.analysis_version
        )
        
        # Convert enhanced analysis data to legacy
        legacy_analysis_data = AnalysisDataModel(
            connections=self.analysis_data.connections,
            orphaned_endpoints=self.analysis_data.orphaned_endpoints,
            orphaned_api_calls=self.analysis_data.orphaned_api_calls,
            dummy_data=self.analysis_data.dummy_data,
            function_connections=self.analysis_data.function_connections,
            orphaned_functions=self.analysis_data.orphaned_functions,
            endpoints=self.analysis_data.endpoints,
            api_calls=self.analysis_data.api_calls,
            summary=self.analysis_data.summary
        )
        
        return ReportModel(
            id=self.id,
            project_id=self.project_id,
            user_id=self.user_id,
            report_name=self.report_name,
            report_display_name=self.report_display_name,
            metrics=legacy_metrics,
            analysis_data=legacy_analysis_data,
            analysis_version=self.analysis_version,
            created_at=self.created_at,
            webapp_url=self.webapp_url
        )


def create_enhanced_report_from_analysis(
    project_id: str,
    user_id: str,
    raw_analysis_result: Dict[str, Any],
    project_name: str,
    report_name: Optional[str] = None
) -> EnhancedReportModel:
    """
    Create enhanced report from raw analysis results.
    
    This is the PRIMARY method for creating reports with all new features.
    """
    from server.processor.reporting.accuracy_reporter import AccuracyReporter
    
    # Extract all data from raw results
    endpoints = raw_analysis_result.get("endpoints", [])
    api_calls = raw_analysis_result.get("api_calls", [])
    connections = raw_analysis_result.get("connections", [])
    orphaned_endpoints = raw_analysis_result.get("orphaned_endpoints", [])
    orphaned_api_calls = raw_analysis_result.get("orphaned_api_calls", [])
    dummy_data = raw_analysis_result.get("dummy_data", [])
    function_connections = raw_analysis_result.get("function_connections", [])
    orphaned_functions = raw_analysis_result.get("orphaned_functions", [])
    security_issues = raw_analysis_result.get("security_issues", [])
    functions = raw_analysis_result.get("functions", [])
    function_calls = raw_analysis_result.get("function_calls", [])
    summary = raw_analysis_result.get("summary", {})
    
    # Helper function to convert Pydantic models to dicts
    def to_dict_list(items):
        """Convert list of Pydantic models or dicts to list of dicts"""
        result = []
        for item in items:
            if hasattr(item, 'model_dump'):
                # It's a Pydantic model
                result.append(item.model_dump(mode='json'))
            elif isinstance(item, dict):
                # Already a dict
                result.append(item)
            else:
                # Try to convert to dict
                result.append(dict(item) if hasattr(item, '__dict__') else item)
        return result
    
    # Create enhanced analysis data with proper dict conversion
    analysis_data = EnhancedAnalysisData(
        connections=to_dict_list(connections),
        orphaned_endpoints=to_dict_list(orphaned_endpoints),
        orphaned_api_calls=to_dict_list(orphaned_api_calls),
        dummy_data=to_dict_list(dummy_data),
        function_connections=to_dict_list(function_connections),
        orphaned_functions=to_dict_list(orphaned_functions),
        security_issues=to_dict_list(security_issues),
        endpoints=to_dict_list(endpoints),
        api_calls=to_dict_list(api_calls),
        functions=to_dict_list(functions),
        function_calls=to_dict_list(function_calls),
        summary=summary
    )
    
    # Count confidence levels (works with both dicts and Pydantic models)
    def count_confidence(items: List) -> Dict[str, int]:
        counts = {"certain": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}
        for item in items:
            # Handle both dict and Pydantic model
            if hasattr(item, 'confidence'):
                conf = str(item.confidence).lower()
            elif isinstance(item, dict):
                conf = str(item.get("confidence", "high")).lower()
            else:
                conf = "high"
            
            if conf in counts:
                counts[conf] += 1
        return counts
    
    # Convert to dicts first for consistent handling
    endpoints_dict = to_dict_list(endpoints)
    api_calls_dict = to_dict_list(api_calls)
    
    endpoint_conf = count_confidence(endpoints_dict)
    api_call_conf = count_confidence(api_calls_dict)
    
    # Calculate weighted accuracy
    def calc_accuracy(conf_dist: Dict[str, int], total: int) -> float:
        if total == 0:
            return 0.0
        weights = {"certain": 1.0, "high": 0.925, "medium": 0.70, "low": 0.50, "unknown": 0.0}
        weighted_sum = sum(conf_dist.get(level, 0) * weight for level, weight in weights.items())
        return round(weighted_sum / total * 100, 1)
    
    endpoint_accuracy = calc_accuracy(endpoint_conf, len(endpoints))
    api_call_accuracy = calc_accuracy(api_call_conf, len(api_calls))
    reliable_coverage = ((endpoint_conf["certain"] + endpoint_conf["high"] + 
                         api_call_conf["certain"] + api_call_conf["high"]) / 
                        max(len(endpoints) + len(api_calls), 1) * 100)
    
    # Count security issues by severity
    security_summary_data = summary.get("security_summary", {})
    security_metadata = summary.get("security_metadata", {})
    
    # Calculate token savings
    files_processed = summary.get("files_processed", 0)
    lines_analyzed = summary.get("lines_analyzed", files_processed * 200)
    estimated_codebase_tokens = lines_analyzed * 10
    base_tokens_per_connection = 50
    tokens_saved = len(connections) * base_tokens_per_connection
    savings_percent = int((tokens_saved / max(estimated_codebase_tokens, 1)) * 100)
    
    # Cost calculation
    input_cost_per_1k = 0.03
    output_cost_per_1k = 0.06
    estimated_full_cost = (estimated_codebase_tokens / 1000) * (input_cost_per_1k + output_cost_per_1k * 2)
    cost_savings = estimated_full_cost * 0.7
    
    # Create enhanced metrics
    metrics = EnhancedMetrics(
        files_processed=files_processed,
        lines_analyzed=lines_analyzed,
        total_endpoints=len(endpoints),
        total_api_calls=len(api_calls),
        connected_endpoints=len(connections),
        orphaned_endpoints=len(orphaned_endpoints),
        orphaned_api_calls=len(orphaned_api_calls),
        uncertain_connections=0,
        total_functions=summary.get("total_functions", 0),
        total_function_calls=summary.get("total_function_calls", 0),
        connected_functions=summary.get("connected_functions", 0),
        orphaned_functions=summary.get("orphaned_functions", 0),
        missing_functions=summary.get("missing_functions", 0),
        security_issues=len(security_issues),
        security_critical=security_summary_data.get("critical", 0),
        security_high=security_summary_data.get("high", 0),
        security_medium=security_summary_data.get("medium", 0),
        security_low=security_summary_data.get("low", 0),
        endpoints_certain=endpoint_conf["certain"],
        endpoints_high=endpoint_conf["high"],
        endpoints_medium=endpoint_conf["medium"],
        endpoints_low=endpoint_conf["low"],
        endpoints_unknown=endpoint_conf["unknown"],
        api_calls_certain=api_call_conf["certain"],
        api_calls_high=api_call_conf["high"],
        api_calls_medium=api_call_conf["medium"],
        api_calls_low=api_call_conf["low"],
        api_calls_unknown=api_call_conf["unknown"],
        estimated_endpoint_accuracy=endpoint_accuracy,
        estimated_api_call_accuracy=api_call_accuracy,
        reliable_coverage=reliable_coverage,
        framework=summary.get("framework", "Unknown"),
        detected_technologies=summary.get("detected_technologies", {}),
        tokens_saved=tokens_saved,
        cost_savings_usd=cost_savings,
        savings_percent=savings_percent,
        project_name=project_name,
        analyzed_date=datetime.utcnow().isoformat(),
        analysis_version="2.0"
    )
    
    # Generate accuracy report
    accuracy_report = AccuracyReporter.generate_standard_report(
        raw_analysis_result,
        project_id=project_id
    )
    
    # Create security summary
    security_summary = SecuritySummary(
        total_issues=len(security_issues),
        critical=security_summary_data.get("critical", 0),
        high=security_summary_data.get("high", 0),
        medium=security_summary_data.get("medium", 0),
        low=security_summary_data.get("low", 0),
        info=security_summary_data.get("info", 0),
        detection_method=security_metadata.get("detection_method", "regex"),
        detection_method_name=security_metadata.get("detection_method_name", "Regex Pattern Matching"),
        accuracy_range=security_metadata.get("accuracy_range", "60-85%"),
        false_positive_risk=security_metadata.get("false_positive_risk", "Medium"),
        categories=security_metadata.get("categories_detected", [])
    )
    
    # Generate webapp URL
    from server.backend.config import settings
    webapp_url = None
    if hasattr(settings, 'web_app_url') and settings.web_app_url:
        webapp_url = f"{settings.web_app_url}/report-detail.html?id={project_id}"
    
    # Create enhanced report
    report = EnhancedReportModel(
        project_id=project_id,
        user_id=user_id,
        report_name=report_name or project_name,
        report_display_name=report_name or project_name,
        metrics=metrics,
        analysis_data=analysis_data,
        accuracy_report=accuracy_report,
        security_summary=security_summary,
        analysis_version="2.0",
        created_at=datetime.utcnow(),
        webapp_url=webapp_url
    )
    
    return report
