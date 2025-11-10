"""
Standard Accuracy Report Schema

This is the SINGLE SOURCE OF TRUTH for accuracy report format across:
- CLI output
- Database storage
- Web API responses
- Frontend display

All components must use this schema to ensure consistency.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ConfidenceDistribution(BaseModel):
    """Confidence level distribution."""
    certain: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    unknown: int = 0
    
    def total(self) -> int:
        """Get total count."""
        return self.certain + self.high + self.medium + self.low + self.unknown
    
    def reliable_count(self) -> int:
        """Get reliable count (CERTAIN + HIGH)."""
        return self.certain + self.high
    
    def reliable_percentage(self) -> float:
        """Get reliable percentage."""
        total = self.total()
        return (self.reliable_count() / total * 100) if total > 0 else 0.0


class ConfidencePercentages(BaseModel):
    """Confidence level percentages."""
    certain: float = 0.0
    high: float = 0.0
    medium: float = 0.0
    low: float = 0.0
    unknown: float = 0.0


class DetectionMethodStats(BaseModel):
    """Statistics for a detection method."""
    method: str
    count: int
    percentage: float = 0.0


class AccuracySummary(BaseModel):
    """High-level accuracy summary."""
    total_endpoints: int = 0
    total_api_calls: int = 0
    total_connections: int = 0
    
    # Confidence distributions
    endpoint_confidence: ConfidenceDistribution = Field(default_factory=ConfidenceDistribution)
    api_call_confidence: ConfidenceDistribution = Field(default_factory=ConfidenceDistribution)
    
    # Percentages
    endpoint_percentages: ConfidencePercentages = Field(default_factory=ConfidencePercentages)
    api_call_percentages: ConfidencePercentages = Field(default_factory=ConfidencePercentages)
    
    # Reliable coverage
    reliable_endpoint_coverage: float = 0.0  # Percentage
    reliable_api_call_coverage: float = 0.0  # Percentage
    
    # Estimated accuracy (weighted by confidence levels)
    estimated_endpoint_accuracy: float = 0.0  # Percentage
    estimated_api_call_accuracy: float = 0.0  # Percentage
    
    # Overall metrics
    overall_reliable_coverage: float = 0.0  # Average of endpoint and API call
    overall_estimated_accuracy: float = 0.0  # Average of endpoint and API call


class DetectionBreakdown(BaseModel):
    """Breakdown of detections by characteristics."""
    total: int = 0
    literal_count: int = 0  # Literal paths/URLs
    computed_count: int = 0  # Computed/dynamic paths/URLs
    cross_file_count: int = 0  # Required cross-file analysis
    single_file_count: int = 0  # Single-file detection
    
    # By confidence
    by_confidence: Dict[str, int] = Field(default_factory=dict)
    
    # Top detection methods
    top_methods: List[DetectionMethodStats] = Field(default_factory=list)


class ConnectionQuality(BaseModel):
    """Connection quality metrics."""
    total_connections: int = 0
    high_confidence: int = 0  # ≥80% match confidence
    medium_confidence: int = 0  # 50-79% match confidence
    low_confidence: int = 0  # <50% match confidence
    average_confidence: float = 0.0


class CoverageEstimate(BaseModel):
    """Coverage estimates based on confidence distribution."""
    estimated_endpoint_accuracy: float = 0.0
    estimated_api_call_accuracy: float = 0.0
    reliable_endpoint_coverage: float = 0.0
    reliable_api_call_coverage: float = 0.0
    explanation: str = "Estimated accuracy based on confidence distribution and empirical accuracy boundaries"


class Recommendation(BaseModel):
    """Actionable recommendation."""
    severity: str  # "info", "warning", "error"
    message: str
    category: str  # "confidence", "coverage", "connections", "refactoring"


class AccuracyReport(BaseModel):
    """
    Complete Accuracy Report - Standard Format
    
    This is the canonical format for accuracy reports across all components.
    """
    # Metadata
    report_id: str
    project_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    analyzer_version: str = "2.0.0"
    
    # Summary
    summary: AccuracySummary
    
    # Detailed breakdowns
    endpoint_breakdown: DetectionBreakdown
    api_call_breakdown: DetectionBreakdown
    connection_quality: ConnectionQuality
    
    # Coverage estimates
    coverage: CoverageEstimate
    
    # Recommendations
    recommendations: List[Recommendation] = Field(default_factory=list)
    
    # Raw counts for reference
    raw_data: Optional[Dict] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AccuracyReportDisplay(BaseModel):
    """
    Simplified format for display (CLI/Web).
    
    Contains only essential information for user-facing display.
    """
    # Key metrics
    reliable_coverage: float  # Percentage
    estimated_accuracy: float  # Percentage
    
    # Confidence breakdown
    endpoints: Dict[str, int]  # {"certain": 10, "high": 20, ...}
    api_calls: Dict[str, int]
    
    # Quality indicators
    connection_quality: str  # "excellent", "good", "fair", "poor"
    
    # Top recommendations
    top_recommendations: List[str]  # Max 3-5 most important
    
    # Metadata
    generated_at: str
    total_items: int


# Helper functions for creating reports

def calculate_confidence_percentages(distribution: ConfidenceDistribution) -> ConfidencePercentages:
    """Calculate percentages from distribution."""
    total = distribution.total()
    if total == 0:
        return ConfidencePercentages()
    
    return ConfidencePercentages(
        certain=round(distribution.certain / total * 100, 1),
        high=round(distribution.high / total * 100, 1),
        medium=round(distribution.medium / total * 100, 1),
        low=round(distribution.low / total * 100, 1),
        unknown=round(distribution.unknown / total * 100, 1)
    )


def calculate_weighted_accuracy(distribution: ConfidenceDistribution) -> float:
    """
    Calculate weighted accuracy based on confidence distribution.
    
    Weights based on empirical accuracy boundaries:
    - CERTAIN: 100% (1.0)
    - HIGH: 92.5% (0.925) - average of 90-95%
    - MEDIUM: 70% (0.70) - average of 60-80%
    - LOW: 50% (0.50)
    - UNKNOWN: 0% (0.0)
    """
    total = distribution.total()
    if total == 0:
        return 0.0
    
    weights = {
        'certain': 1.0,
        'high': 0.925,
        'medium': 0.70,
        'low': 0.50,
        'unknown': 0.0
    }
    
    weighted_sum = (
        distribution.certain * weights['certain'] +
        distribution.high * weights['high'] +
        distribution.medium * weights['medium'] +
        distribution.low * weights['low'] +
        distribution.unknown * weights['unknown']
    )
    
    return round(weighted_sum / total * 100, 1)


def determine_connection_quality(avg_confidence: float) -> str:
    """Determine connection quality label."""
    if avg_confidence >= 0.85:
        return "excellent"
    elif avg_confidence >= 0.70:
        return "good"
    elif avg_confidence >= 0.50:
        return "fair"
    else:
        return "poor"
