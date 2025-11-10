"""
Snapshot management for project tracking.

Handles creation, storage, and retrieval of snapshots.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from .models import Snapshot, Project
from .file_manager import RohkunFileManager
from .hash_generator import generate_snapshot_id

logger = logging.getLogger(__name__)


class SnapshotManager:
    """Manages snapshot operations."""
    
    def __init__(self, file_manager: RohkunFileManager):
        """
        Initialize snapshot manager.
        
        Args:
            file_manager: RohkunFileManager instance
        """
        self.file_manager = file_manager
    
    def create_snapshot(
        self,
        project: Project,
        analysis_result: Dict[str, Any],
        is_baseline: bool = False
    ) -> Snapshot:
        """
        Create a new snapshot from analysis result.
        
        Args:
            project: Project instance
            analysis_result: Analysis result dictionary with endpoints, api_calls, etc.
            is_baseline: Whether this is the first baseline snapshot
            
        Returns:
            Snapshot instance
        """
        snapshot_id = generate_snapshot_id()
        timestamp = datetime.now()
        
        # Extract data from analysis result
        endpoints = analysis_result.get("endpoints", [])
        api_calls = analysis_result.get("api_calls", [])
        summary = analysis_result.get("summary", {})
        
        # Build snapshot data structure
        backend_data = {
            "endpoints": endpoints,
            "endpoints_count": len(endpoints),
            "framework": summary.get("framework", "Unknown"),
            "detected_technologies": summary.get("detected_technologies", {})
        }
        
        frontend_data = {
            "api_calls": api_calls,
            "api_calls_count": len(api_calls),
            "libraries": self._detect_libraries(api_calls)
        }
        
        metadata = {
            "files_processed": summary.get("files_processed", 0),
            "lines_analyzed": summary.get("lines_analyzed", 0),
            "total_files": summary.get("files_processed", 0),
            "loc_count": summary.get("lines_analyzed", 0),
            "confidence_score": summary.get("confidence_score", 0.0)
        }
        
        # Determine sequence number
        sequence = 1 if is_baseline else project.total_snapshots + 1
        
        snapshot = Snapshot(
            id=snapshot_id,
            project_hash=project.project_hash,
            timestamp=timestamp,
            sequence=sequence,
            backend=backend_data,
            frontend=frontend_data,
            metadata=metadata,
            compared_to=None,  # Will be set later if not baseline
            drift_score=0.0 if is_baseline else 0.0,  # Will be calculated later
            status="baseline" if is_baseline else "healthy"
        )
        
        logger.info(f"Created snapshot {snapshot_id} (sequence {sequence})")
        return snapshot
    
    def save_snapshot(self, snapshot: Snapshot) -> Path:
        """
        Save snapshot to disk.
        
        Args:
            snapshot: Snapshot instance
            
        Returns:
            Path to saved file
        """
        snapshot_data = snapshot.to_dict()
        return self.file_manager.save_snapshot_json(snapshot.id, snapshot_data)
    
    def load_snapshot(self, snapshot_id: str) -> Optional[Snapshot]:
        """
        Load snapshot from disk.
        
        Args:
            snapshot_id: Snapshot ID
            
        Returns:
            Snapshot instance or None if not found
        """
        snapshot_data = self.file_manager.load_snapshot_json(snapshot_id)
        if not snapshot_data:
            return None
        
        return Snapshot.from_dict(snapshot_data)
    
    def update_snapshot_index(self, project: Project, snapshot: Snapshot) -> None:
        """
        Update snapshot index with new snapshot.
        
        Args:
            project: Project instance
            snapshot: Snapshot instance
        """
        index_data = self.file_manager.load_snapshot_index()
        
        # Initialize if empty
        if "snapshots" not in index_data:
            index_data["snapshots"] = []
        
        # Set project_hash if not set or empty
        if not index_data.get("project_hash"):
            index_data["project_hash"] = project.project_hash
        
        # Create index entry
        index_entry = {
            "id": snapshot.id,
            "timestamp": snapshot.timestamp.isoformat(),
            "sequence": snapshot.sequence,
            "endpoints": snapshot.backend.get("endpoints_count", 0),
            "api_calls": snapshot.frontend.get("api_calls_count", 0),
            "files": snapshot.metadata.get("total_files", 0),
            "drift": snapshot.drift_score,
            "status": snapshot.status,
            "report_file": f"reports/report_{snapshot.id.replace('snapshot_', '')}.md",
            "compared_to": snapshot.compared_to
        }
        
        # Add to index
        index_data["snapshots"].append(index_entry)
        
        # Sort by sequence
        index_data["snapshots"].sort(key=lambda x: x["sequence"])
        
        # Save updated index
        self.file_manager.save_snapshot_index(index_data)
        logger.debug(f"Updated snapshot index with {snapshot.id}")
    
    def list_snapshots(self, project_hash: str) -> List[Dict[str, Any]]:
        """
        List all snapshots for a project.
        
        Args:
            project_hash: Project hash
            
        Returns:
            List of snapshot index entries
        """
        index_data = self.file_manager.load_snapshot_index()
        
        if index_data.get("project_hash") != project_hash:
            return []
        
        return index_data.get("snapshots", [])
    
    def get_last_snapshot(self, project: Project) -> Optional[Snapshot]:
        """
        Get the most recent snapshot for a project.
        
        Args:
            project: Project instance
            
        Returns:
            Last snapshot or None if no snapshots exist
        """
        if not project.last_snapshot:
            return None
        
        return self.load_snapshot(project.last_snapshot)
    
    def _detect_libraries(self, api_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect libraries used in API calls.
        
        Args:
            api_calls: List of API call dictionaries
            
        Returns:
            Dictionary of detected libraries
        """
        libraries = {
            "fetch": {"detected": False, "count": 0},
            "axios": {"detected": False, "count": 0},
            "apollo_client": {"detected": False, "count": 0},
            "socket_io": {"detected": False, "count": 0}
        }
        
        for api_call in api_calls:
            library = api_call.get("library", "").lower()
            
            if "fetch" in library or library == "native":
                libraries["fetch"]["detected"] = True
                libraries["fetch"]["count"] += 1
            elif "axios" in library:
                libraries["axios"]["detected"] = True
                libraries["axios"]["count"] += 1
            elif "apollo" in library or "graphql" in library:
                libraries["apollo_client"]["detected"] = True
                libraries["apollo_client"]["count"] += 1
            elif "socket" in library or "websocket" in library:
                libraries["socket_io"]["detected"] = True
                libraries["socket_io"]["count"] += 1
        
        return libraries

