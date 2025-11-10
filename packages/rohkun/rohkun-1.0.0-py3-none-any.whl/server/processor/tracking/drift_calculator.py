"""
Drift score calculation.

Calculates drift scores based on structural changes between snapshots.
"""

import logging
from typing import Dict, Any

from .models import Diff, DriftScore

logger = logging.getLogger(__name__)


class DriftCalculator:
    """Calculates drift scores from diffs."""
    
    def calculate_drift(self, diff: Diff) -> DriftScore:
        """
        Calculate drift score from diff.
        
        Drift = measure of structural change velocity
        
        Thresholds:
        - 0.00 - 0.20: Low (healthy, focused changes)
        - 0.20 - 0.50: Medium (caution, review changes)
        - 0.50 - 1.00: High (significant refactor)
        
        Args:
            diff: Diff instance
            
        Returns:
            DriftScore instance
        """
        components = self._calculate_drift_components(diff)
        score = sum(components.values())
        
        # Cap at 1.0
        score = min(score, 1.0)
        
        # Normalize by time elapsed (optional - can be adjusted)
        # For now, we use raw score
        
        status = self._get_drift_status(score)
        interpretation = self._get_interpretation(score, status)
        
        drift_score = DriftScore(
            score=score,
            status=status,
            components=components,
            interpretation=interpretation
        )
        
        # Update diff with drift score
        diff.drift_score = score
        
        logger.debug(f"Calculated drift score: {score} ({status})")
        return drift_score
    
    def _calculate_drift_components(self, diff: Diff) -> Dict[str, float]:
        """
        Calculate individual drift components.
        
        Args:
            diff: Diff instance
            
        Returns:
            Dictionary of component scores
        """
        components = {}
        
        backend_changes = diff.backend_changes
        frontend_changes = diff.frontend_changes
        file_changes = diff.file_changes
        
        # New endpoints: +0.05 per endpoint
        new_endpoints = backend_changes.get("added_count", 0)
        components["new_endpoints"] = new_endpoints * 0.05
        
        # Deleted endpoints: +0.05 per endpoint
        deleted_endpoints = backend_changes.get("removed_count", 0)
        components["deleted_endpoints"] = deleted_endpoints * 0.05
        
        # Modified endpoints: +0.01 per endpoint
        modified_endpoints = backend_changes.get("modified_count", 0)
        components["modified_endpoints"] = modified_endpoints * 0.01
        
        # New API calls: +0.03 per call
        new_api_calls = frontend_changes.get("added_count", 0)
        components["new_api_calls"] = new_api_calls * 0.03
        
        # Removed API calls: +0.03 per call
        removed_api_calls = frontend_changes.get("removed_count", 0)
        components["removed_api_calls"] = removed_api_calls * 0.03
        
        # Method changes: +0.05 per change
        method_changes = frontend_changes.get("method_changes", 0)
        components["method_changes"] = method_changes * 0.05
        
        # New files: +0.01 per file
        new_files = file_changes.get("new_files", 0)
        components["new_files"] = new_files * 0.01
        
        # Modified files: +0.01 per file (if we track this)
        modified_files = file_changes.get("modified_files", 0)
        components["modified_files"] = modified_files * 0.01
        
        return components
    
    def _get_drift_status(self, score: float) -> str:
        """
        Get drift status from score.
        
        Args:
            score: Drift score (0.0 - 1.0)
            
        Returns:
            Status string: "healthy", "caution", or "high"
        """
        if score < 0.20:
            return "healthy"
        elif score < 0.50:
            return "caution"
        else:
            return "high"
    
    def _get_interpretation(self, score: float, status: str) -> str:
        """
        Get human-readable interpretation of drift score.
        
        Args:
            score: Drift score
            status: Drift status
            
        Returns:
            Interpretation string
        """
        if status == "healthy":
            return "Low drift - focused, incremental changes"
        elif status == "caution":
            return "Medium drift - review changes to ensure they align with intent"
        else:
            return "High drift - significant structural changes, verify intent"
    
    def get_drift_status_emoji(self, status: str) -> str:
        """
        Get emoji for drift status.
        
        Args:
            status: Drift status
            
        Returns:
            Emoji string
        """
        status_map = {
            "healthy": "🟢",
            "caution": "🟡",
            "high": "🔴"
        }
        return status_map.get(status, "⚪")

