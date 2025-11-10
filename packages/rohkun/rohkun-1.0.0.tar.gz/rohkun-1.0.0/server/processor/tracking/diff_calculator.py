"""
Diff calculation between snapshots.

Computes structural differences between two snapshots.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from .models import Snapshot, Diff

logger = logging.getLogger(__name__)


class DiffCalculator:
    """Calculates structural diffs between snapshots."""
    
    def compute_diff(self, before: Snapshot, after: Snapshot) -> Diff:
        """
        Compute structural diff between two snapshots.
        
        Args:
            before: Previous snapshot
            after: Current snapshot
            
        Returns:
            Diff instance
        """
        time_elapsed = self._calculate_time_elapsed(before.timestamp, after.timestamp)
        
        backend_changes = self._compute_backend_diff(
            before.backend.get("endpoints", []),
            after.backend.get("endpoints", [])
        )
        
        frontend_changes = self._compute_frontend_diff(
            before.frontend.get("api_calls", []),
            after.frontend.get("api_calls", [])
        )
        
        file_changes = self._compute_file_diff(
            before.metadata,
            after.metadata
        )
        
        diff = Diff(
            from_snapshot=before.id,
            to_snapshot=after.id,
            time_elapsed=time_elapsed,
            backend_changes=backend_changes,
            frontend_changes=frontend_changes,
            file_changes=file_changes,
            drift_score=0.0,  # Will be calculated by DriftCalculator
            metadata={}
        )
        
        logger.info(f"Computed diff from {before.id} to {after.id}")
        return diff
    
    def _compute_backend_diff(
        self,
        before_endpoints: List[Dict[str, Any]],
        after_endpoints: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compute backend endpoint differences.
        
        Args:
            before_endpoints: List of endpoint dictionaries from before snapshot
            after_endpoints: List of endpoint dictionaries from after snapshot
            
        Returns:
            Dictionary with added, removed, and modified endpoints
        """
        # Create lookup dictionaries by endpoint signature
        before_lookup = {self._endpoint_signature(e): e for e in before_endpoints}
        after_lookup = {self._endpoint_signature(e): e for e in after_endpoints}
        
        before_keys = set(before_lookup.keys())
        after_keys = set(after_lookup.keys())
        
        # Find added endpoints
        added_keys = after_keys - before_keys
        added = [after_lookup[key] for key in added_keys]
        
        # Find removed endpoints
        removed_keys = before_keys - after_keys
        removed = [before_lookup[key] for key in removed_keys]
        
        # Find modified endpoints (same signature but different content)
        modified = []
        common_keys = before_keys & after_keys
        for key in common_keys:
            before_ep = before_lookup[key]
            after_ep = after_lookup[key]
            
            # Check if endpoint was modified (simplified check)
            if self._endpoint_modified(before_ep, after_ep):
                modified.append({
                    "endpoint": after_ep,
                    "change": "modified"
                })
        
        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "added_count": len(added),
            "removed_count": len(removed),
            "modified_count": len(modified)
        }
    
    def _compute_frontend_diff(
        self,
        before_api_calls: List[Dict[str, Any]],
        after_api_calls: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compute frontend API call differences.
        
        Args:
            before_api_calls: List of API call dictionaries from before snapshot
            after_api_calls: List of API call dictionaries from after snapshot
            
        Returns:
            Dictionary with added, removed, and modified API calls
        """
        # Create lookup dictionaries by API call signature
        before_lookup = {self._api_call_signature(a): a for a in before_api_calls}
        after_lookup = {self._api_call_signature(a): a for a in after_api_calls}
        
        before_keys = set(before_lookup.keys())
        after_keys = set(after_lookup.keys())
        
        # Find added API calls
        added_keys = after_keys - before_keys
        added = [after_lookup[key] for key in added_keys]
        
        # Find removed API calls
        removed_keys = before_keys - after_keys
        removed = [before_lookup[key] for key in removed_keys]
        
        # Find modified API calls (method changes, etc.)
        modified = []
        common_keys = before_keys & after_keys
        for key in common_keys:
            before_call = before_lookup[key]
            after_call = after_lookup[key]
            
            if self._api_call_modified(before_call, after_call):
                modified.append({
                    "api_call": after_call,
                    "change": "modified"
                })
        
        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "added_count": len(added),
            "removed_count": len(removed),
            "modified_count": len(modified),
            "method_changes": len([m for m in modified if "method" in m.get("change", "").lower()])
        }
    
    def _compute_file_diff(
        self,
        before_metadata: Dict[str, Any],
        after_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute file-level differences.
        
        Args:
            before_metadata: Metadata from before snapshot
            after_metadata: Metadata from after snapshot
            
        Returns:
            Dictionary with file change information
        """
        before_files = before_metadata.get("total_files", 0)
        after_files = after_metadata.get("total_files", 0)
        before_loc = before_metadata.get("loc_count", 0)
        after_loc = after_metadata.get("loc_count", 0)
        
        new_files = max(0, after_files - before_files)
        deleted_files = max(0, before_files - after_files)
        loc_change = after_loc - before_loc
        
        return {
            "new_files": new_files,
            "deleted_files": deleted_files,
            "modified_files": 0,  # Would need file-level tracking for this
            "loc_change": loc_change,
            "files_before": before_files,
            "files_after": after_files
        }
    
    def _endpoint_signature(self, endpoint: Dict[str, Any]) -> str:
        """Create unique signature for an endpoint."""
        path = endpoint.get("path", "")
        method = endpoint.get("method", "").upper()
        return f"{method}:{path}"
    
    def _api_call_signature(self, api_call: Dict[str, Any]) -> str:
        """Create unique signature for an API call."""
        url = api_call.get("url", "")
        method = api_call.get("method", "").upper()
        file_path = api_call.get("file", "")
        return f"{method}:{url}:{file_path}"
    
    def _endpoint_modified(self, before: Dict[str, Any], after: Dict[str, Any]) -> bool:
        """Check if endpoint was modified."""
        # Simple check - compare file and line number
        before_file = before.get("file", "")
        after_file = after.get("file", "")
        before_line = before.get("line", 0)
        after_line = after.get("line", 0)
        
        return before_file != after_file or before_line != after_line
    
    def _api_call_modified(self, before: Dict[str, Any], after: Dict[str, Any]) -> bool:
        """Check if API call was modified."""
        # Check if method changed
        before_method = before.get("method", "").upper()
        after_method = after.get("method", "").upper()
        
        if before_method != after_method:
            return True
        
        # Check if file/line changed
        before_file = before.get("file", "")
        after_file = after.get("file", "")
        before_line = before.get("line", 0)
        after_line = after.get("line", 0)
        
        return before_file != after_file or before_line != after_line
    
    def _calculate_time_elapsed(self, before: datetime, after: datetime) -> str:
        """Calculate human-readable time elapsed between two timestamps."""
        delta = after - before
        
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

