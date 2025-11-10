"""
Report Formatter - Wrapper for reporting module.

This is a compatibility layer that imports from the actual reporting module.
The real implementation is in server.processor.reporting.report_formatter
"""

# Import the actual ReportFormatter from the reporting module
from server.processor.reporting.report_formatter import ReportFormatter

__all__ = ['ReportFormatter']
