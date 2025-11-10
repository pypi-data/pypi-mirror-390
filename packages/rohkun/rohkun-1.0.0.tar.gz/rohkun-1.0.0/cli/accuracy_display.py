"""
CLI display formatter for accuracy reports.

Formats API response data for beautiful terminal output.
Works with plain dictionaries from API responses - no server imports.
"""

import os
import shutil
import math
from typing import Optional, Dict, Any
from rich.console import Console


class AccuracyCLIFormatter:
    """Formats accuracy reports from API responses for CLI display."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize formatter with optional console for terminal width detection."""
        self.console = console or Console()
        # Don't cache terminal width - get it dynamically
        self._terminal_width_cached = None
    
    def _get_terminal_width(self) -> int:
        """Get terminal width dynamically, with safe fallback."""
        try:
            # Try to get from environment first
            width = os.getenv('COLUMNS')
            if width:
                return max(40, min(200, int(width)))
            
            # Try shutil.get_terminal_size (Python 3.3+)
            try:
                size = shutil.get_terminal_size()
                return max(40, min(200, size.columns))
            except (OSError, AttributeError):
                pass
            
            # Fallback to 80 if all else fails
            return 80
        except (ValueError, TypeError):
            return 80
    
    @property
    def _terminal_width(self) -> int:
        """Get terminal width dynamically to handle resize."""
        return self._get_terminal_width()
    
    @staticmethod
    def _escape_rich_markup(text: str) -> str:
        """Escape Rich markup syntax in user-generated content."""
        if not isinstance(text, str):
            text = str(text)
        # Escape all Rich markup characters to prevent injection
        # Square brackets, backslashes, and other special chars
        text = text.replace('\\', '\\\\')  # Escape backslashes first
        text = text.replace('[', '\\[')
        text = text.replace(']', '\\]')
        return text
    
    @staticmethod
    def _safe_float(value, default: float = 0.0, min_val: Optional[float] = None, max_val: Optional[float] = None) -> float:
        """Safely convert value to float with validation and precision handling."""
        try:
            if not isinstance(value, (int, float)):
                return default
            if math.isnan(value) or math.isinf(value):
                return default
            result = float(value)
            # Handle floating-point precision issues
            # Round to 10 decimal places to avoid precision errors
            result = round(result, 10)
            if min_val is not None:
                result = max(min_val, result)
            if max_val is not None:
                result = min(max_val, result)
            return result
        except (ValueError, TypeError, OverflowError):
            return default
    
    @staticmethod
    def _safe_int(value, default: int = 0, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
        """Safely convert value to int with validation."""
        try:
            if not isinstance(value, (int, float)):
                return default
            if math.isnan(value) or math.isinf(value):
                return default
            result = int(value)
            if min_val is not None:
                result = max(min_val, result)
            if max_val is not None:
                result = min(max_val, result)
            return result
        except (ValueError, TypeError, OverflowError):
            return default
    
    def _validate_report(self, report: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate that report dict contains all required fields."""
        if not isinstance(report, dict):
            return False, "Report is not a dictionary"
        
        try:
            # Check top-level fields
            if not report.get('report_id'):
                return False, "Missing or empty report_id"
            
            if 'summary' not in report or report['summary'] is None:
                return False, "Missing summary"
            
            if 'coverage' not in report or report['coverage'] is None:
                return False, "Missing coverage"
            
            if 'connection_quality' not in report or report['connection_quality'] is None:
                return False, "Missing connection_quality"
            
            if 'endpoint_breakdown' not in report or report['endpoint_breakdown'] is None:
                return False, "Missing endpoint_breakdown"
            
            if 'api_call_breakdown' not in report or report['api_call_breakdown'] is None:
                return False, "Missing api_call_breakdown"
            
            return True, None
        except Exception as e:
            return False, f"Validation error: {type(e).__name__}"
    
    def format_full_report(self, report: Dict[str, Any], use_colors: bool = True) -> str:
        """Format complete accuracy report from API response for CLI.
        
        Args:
            report: Dictionary from API response containing report data
            use_colors: Whether to include Rich markup for colors
        
        Returns plain string with Rich markup (if use_colors=True).
        Caller should render with console.print() or similar.
        """
        # Validate input
        is_valid, error_msg = self._validate_report(report)
        if not is_valid:
            if use_colors:
                return f"[red]Error: Invalid report data - {error_msg}[/red]"
            return f"Error: Invalid report data - {error_msg}"
        
        lines = []
        width = self._terminal_width
        
        # Header
        lines.append("")
        lines.append("=" * width)
        header_text = "📊 ACCURACY & CONFIDENCE REPORT"
        lines.append(self._bold(header_text, use_colors))
        lines.append("=" * width)
        lines.append("")
        
        # Format sections
        lines.append(self._format_summary(report, use_colors))
        lines.append(self._format_confidence_distribution(report, use_colors))
        lines.append(self._format_coverage(report, use_colors))
        lines.append(self._format_connection_quality(report, use_colors))
        lines.append(self._format_detection_methods(report, use_colors))
        lines.append(self._format_recommendations(report, use_colors))
        
        # Footer
        lines.append("")
        lines.append("=" * width)
        report_id = report.get('report_id', 'unknown')
        lines.append(f"Report ID: {self._escape_rich_markup(str(report_id))}")
        
        generated_at = report.get('generated_at')
        if generated_at:
            lines.append(f"Generated: {self._escape_rich_markup(str(generated_at))}")
        
        lines.append("=" * width)
        lines.append("")
        
        return "\n".join(lines)
    
    def format_summary_only(self, report: Dict[str, Any], use_colors: bool = True) -> str:
        """Format summary only from API response (for quick display).
        
        Args:
            report: Dictionary from API response containing report data
            use_colors: Whether to include Rich markup for colors
        
        Returns plain string with Rich markup (if use_colors=True).
        """
        # Validate input
        is_valid, error_msg = self._validate_report(report)
        if not is_valid:
            if use_colors:
                return f"[red]Error: Invalid report data - {error_msg}[/red]"
            return f"Error: Invalid report data - {error_msg}"
        
        lines = []
        width = min(40, self._terminal_width)
        
        lines.append("")
        lines.append(self._bold("📊 Accuracy Summary", use_colors))
        lines.append("-" * width)
        
        summary = report.get('summary', {})
        
        # Key metrics
        overall_coverage = self._safe_float(summary.get('overall_reliable_coverage', 0.0), 0.0, 0.0, 100.0)
        overall_accuracy = self._safe_float(summary.get('overall_estimated_accuracy', 0.0), 0.0, 0.0, 100.0)
        lines.append(f"Reliable Coverage: {self._get_quality_label(overall_coverage, use_colors)}")
        lines.append(f"Estimated Accuracy: {self._get_quality_label(overall_accuracy, use_colors)}")
        lines.append("")
        
        # Counts
        total_endpoints = self._safe_int(summary.get('total_endpoints', 0), 0, 0)
        total_api_calls = self._safe_int(summary.get('total_api_calls', 0), 0, 0)
        total_connections = self._safe_int(summary.get('total_connections', 0), 0, 0)
        endpoint_coverage = self._safe_float(summary.get('reliable_endpoint_coverage', 0.0), 0.0, 0.0, 100.0)
        api_call_coverage = self._safe_float(summary.get('reliable_api_call_coverage', 0.0), 0.0, 0.0, 100.0)
        
        lines.append(f"Endpoints: {total_endpoints} ({self._get_coverage_label(endpoint_coverage)})")
        lines.append(f"API Calls: {total_api_calls} ({self._get_coverage_label(api_call_coverage)})")
        lines.append(f"Connections: {total_connections}")
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_summary(self, report: Dict[str, Any], use_colors: bool) -> str:
        """Format summary section."""
        lines = []
        width = self._terminal_width
        summary = report.get('summary', {})
        
        lines.append(self._bold("📈 SUMMARY", use_colors))
        lines.append("-" * width)
        
        total_endpoints = self._safe_int(summary.get('total_endpoints', 0), 0, 0)
        total_api_calls = self._safe_int(summary.get('total_api_calls', 0), 0, 0)
        total_connections = self._safe_int(summary.get('total_connections', 0), 0, 0)
        
        lines.append(f"Total Endpoints: {total_endpoints}")
        lines.append(f"Total API Calls: {total_api_calls}")
        lines.append(f"Total Connections: {total_connections}")
        lines.append("")
        
        overall_coverage = self._safe_float(summary.get('overall_reliable_coverage', 0.0), 0.0, 0.0, 100.0)
        overall_accuracy = self._safe_float(summary.get('overall_estimated_accuracy', 0.0), 0.0, 0.0, 100.0)
        
        lines.append(f"Overall Reliable Coverage: {self._get_quality_label(overall_coverage, use_colors)}")
        lines.append(f"Overall Estimated Accuracy: {self._get_quality_label(overall_accuracy, use_colors)}")
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_confidence_distribution(self, report: Dict[str, Any], use_colors: bool) -> str:
        """Format confidence distribution."""
        lines = []
        width = self._terminal_width
        summary = report.get('summary', {})
        
        lines.append(self._bold("🎯 CONFIDENCE DISTRIBUTION", use_colors))
        lines.append("-" * width)
        
        # Endpoints
        lines.append("Endpoints:")
        endpoint_conf = summary.get('endpoint_confidence')
        endpoint_pct = summary.get('endpoint_percentages')
        if endpoint_conf and endpoint_pct:
            lines.extend(self._format_confidence_bars(endpoint_conf, endpoint_pct, use_colors))
        else:
            lines.append("  [No data available]")
        
        lines.append("")
        
        # API Calls
        lines.append("API Calls:")
        api_conf = summary.get('api_call_confidence')
        api_pct = summary.get('api_call_percentages')
        if api_conf and api_pct:
            lines.extend(self._format_confidence_bars(api_conf, api_pct, use_colors))
        else:
            lines.append("  [No data available]")
        
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_confidence_bars(self, dist: Dict[str, Any], percentages: Dict[str, Any], use_colors: bool) -> list:
        """Format confidence distribution as bars."""
        lines = []
        
        levels = [
            ('CERTAIN', 'certain', 'green'),
            ('HIGH', 'high', 'green'),
            ('MEDIUM', 'medium', 'yellow'),
            ('LOW', 'low', 'yellow'),
            ('UNKNOWN', 'unknown', 'red'),
        ]
        
        for level_name, key_name, color_name in levels:
            count = self._safe_int(dist.get(key_name, 0), 0, 0)
            pct = self._safe_float(percentages.get(key_name, 0.0), 0.0, 0.0, 100.0)
            
            # Calculate bar length safely
            max_bar_length = max(1, min(50, self._terminal_width - 30))
            bar_length = self._safe_int((pct / 100.0) * max_bar_length, 0, 0, max_bar_length)
            bar = "█" * bar_length
            
            # Format with Rich colors if enabled
            if use_colors:
                bar_text = f"[{color_name}]{bar}[/{color_name}]"
            else:
                bar_text = bar
            
            lines.append(f"  {level_name:8s}: {count:3d} {bar_text}")
        
        return lines
    
    def _format_coverage(self, report: Dict[str, Any], use_colors: bool) -> str:
        """Format coverage estimates."""
        lines = []
        width = self._terminal_width
        
        lines.append(self._bold("📊 COVERAGE ESTIMATES", use_colors))
        lines.append("-" * width)
        
        cov = report.get('coverage', {})
        endpoint_acc = self._safe_float(cov.get('estimated_endpoint_accuracy', 0.0), 0.0, 0.0, 100.0)
        api_acc = self._safe_float(cov.get('estimated_api_call_accuracy', 0.0), 0.0, 0.0, 100.0)
        endpoint_cov = self._safe_float(cov.get('reliable_endpoint_coverage', 0.0), 0.0, 0.0, 100.0)
        api_cov = self._safe_float(cov.get('reliable_api_call_coverage', 0.0), 0.0, 0.0, 100.0)
        
        lines.append(f"Estimated Endpoint Accuracy: {self._get_quality_label(endpoint_acc, use_colors)}")
        lines.append(f"Estimated API Call Accuracy: {self._get_quality_label(api_acc, use_colors)}")
        lines.append("")
        lines.append(f"Reliable Endpoint Coverage (CERTAIN + HIGH): {self._get_quality_label(endpoint_cov, use_colors)}")
        lines.append(f"Reliable API Call Coverage (CERTAIN + HIGH): {self._color_percentage(api_cov, use_colors)}")
        lines.append("")
        
        explanation = cov.get('explanation', 'No explanation available')
        lines.append(f"ℹ️  {self._escape_rich_markup(str(explanation))}")
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_connection_quality(self, report: Dict[str, Any], use_colors: bool) -> str:
        """Format connection quality."""
        lines = []
        width = self._terminal_width
        
        lines.append(self._bold("🔗 CONNECTION QUALITY", use_colors))
        lines.append("-" * width)
        
        cq = report.get('connection_quality', {})
        total = self._safe_int(cq.get('total_connections', 0), 0, 0)
        high = self._safe_int(cq.get('high_confidence', 0), 0, 0)
        medium = self._safe_int(cq.get('medium_confidence', 0), 0, 0)
        low = self._safe_int(cq.get('low_confidence', 0), 0, 0)
        
        lines.append(f"Total Connections: {total}")
        lines.append(f"High Confidence (≥80%): {high}")
        lines.append(f"Medium Confidence (50-79%): {medium}")
        lines.append(f"Low Confidence (<50%): {low}")
        
        avg_conf = self._safe_float(cq.get('average_confidence', 0.0), 0.0, 0.0, 1.0)
        # Convert to percentage if in 0-1 range
        if avg_conf <= 1.0:
            avg_conf_pct = avg_conf * 100.0
        else:
            avg_conf_pct = avg_conf
        
        lines.append(f"Average Confidence: {self._color_percentage(avg_conf_pct, use_colors)}")
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_detection_methods(self, report: Dict[str, Any], use_colors: bool) -> str:
        """Format detection methods."""
        lines = []
        width = self._terminal_width
        
        lines.append(self._bold("🔍 TOP DETECTION METHODS", use_colors))
        lines.append("-" * width)
        
        # Endpoints
        lines.append("Endpoints:")
        endpoint_breakdown = report.get('endpoint_breakdown', {})
        top_methods = endpoint_breakdown.get('top_methods', [])
        if top_methods and isinstance(top_methods, list):
            for method in top_methods[:3]:
                if isinstance(method, dict):
                    method_name = self._escape_rich_markup(str(method.get('method', 'unknown')))
                    count = self._safe_int(method.get('count', 0), 0, 0)
                    lines.append(f"  • {method_name}: {count} detections")
        else:
            lines.append("  [No methods available]")
        
        lines.append("")
        
        # API Calls
        lines.append("API Calls:")
        api_call_breakdown = report.get('api_call_breakdown', {})
        top_methods = api_call_breakdown.get('top_methods', [])
        if top_methods and isinstance(top_methods, list):
            for method in top_methods[:3]:
                if isinstance(method, dict):
                    method_name = self._escape_rich_markup(str(method.get('method', 'unknown')))
                    count = self._safe_int(method.get('count', 0), 0, 0)
                    lines.append(f"  • {method_name}: {count} detections")
        else:
            lines.append("  [No methods available]")
        
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_recommendations(self, report: Dict[str, Any], use_colors: bool) -> str:
        """Format recommendations."""
        lines = []
        width = self._terminal_width
        
        lines.append(self._bold("💡 RECOMMENDATIONS", use_colors))
        lines.append("-" * width)
        
        recommendations = report.get('recommendations', [])
        if not recommendations:
            lines.append("✅ No recommendations - analysis quality is good!")
        else:
            for rec in recommendations:
                if isinstance(rec, dict):
                    icon = self._get_severity_icon(rec.get('severity', 'info'))
                    message = self._escape_rich_markup(str(rec.get('message', 'No message')))
                    if use_colors:
                        severity = rec.get('severity', 'info')
                        color_tag = self._get_severity_color_tag(severity)
                        lines.append(f"{color_tag}{icon} {message}[/]")
                    else:
                        lines.append(f"{icon} {message}")
        
        lines.append("")
        
        return "\n".join(lines)
    
    def _bold(self, text: str, use_colors: bool) -> str:
        """Make text bold."""
        if use_colors:
            return f"[bold]{text}[/bold]"
        return text
    
    def _color_percentage(self, value: float, use_colors: bool) -> str:
        """Color percentage based on value."""
        formatted = f"{value:.1f}%"
        if not use_colors:
            return formatted
        
        if value >= 80:
            return f"[green]{formatted}[/green]"
        elif value >= 60:
            return f"[yellow]{formatted}[/yellow]"
        else:
            return f"[red]{formatted}[/red]"
    
    def _get_quality_label(self, value: float, use_colors: bool) -> str:
        """Get subjective quality label instead of percentage."""
        if value >= 90:
            label = "Excellent"
            color = "green"
        elif value >= 75:
            label = "Very Good"
            color = "green"
        elif value >= 60:
            label = "Good"
            color = "yellow"
        elif value >= 40:
            label = "Fair"
            color = "yellow"
        elif value >= 20:
            label = "Limited"
            color = "red"
        else:
            label = "Minimal"
            color = "red"
        
        if use_colors:
            return f"[{color}]{label}[/{color}]"
        return label
    
    def _get_coverage_label(self, value: float) -> str:
        """Get coverage label without colors."""
        if value >= 90:
            return "excellent coverage"
        elif value >= 75:
            return "very good coverage"
        elif value >= 60:
            return "good coverage"
        elif value >= 40:
            return "fair coverage"
        elif value >= 20:
            return "limited coverage"
        else:
            return "minimal coverage"
    
    def _get_severity_icon(self, severity: str) -> str:
        """Get icon for severity."""
        icons = {
            'info': 'ℹ️ ',
            'warning': '⚠️ ',
            'error': '❌'
        }
        return icons.get(severity, 'ℹ️ ')
    
    def _get_severity_color_tag(self, severity: str) -> str:
        """Get Rich color tag for severity."""
        colors = {
            'info': '[cyan]',
            'warning': '[yellow]',
            'error': '[red]'
        }
        return colors.get(severity, '[cyan]')
