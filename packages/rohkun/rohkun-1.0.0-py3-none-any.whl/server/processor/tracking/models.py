"""
Data models for project tracking.

Defines Project, Snapshot, Diff, and DriftScore data structures.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class Project:
    """Project identity and metadata."""
    project_hash: str
    project_name: str
    root_dir: str
    created_at: datetime
    first_snapshot: Optional[str] = None
    last_snapshot: Optional[str] = None
    total_snapshots: int = 0
    tracking_days: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "project_hash": self.project_hash,
            "project_name": self.project_name,
            "created_at": self.created_at.isoformat(),
            "first_snapshot": self.first_snapshot,
            "last_snapshot": self.last_snapshot,
            "total_snapshots": self.total_snapshots,
            "tracking_days": self.tracking_days,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Create Project from dictionary."""
        created_at = datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"]
        return cls(
            project_hash=data["project_hash"],
            project_name=data["project_name"],
            root_dir=data.get("root_dir", ""),
            created_at=created_at,
            first_snapshot=data.get("first_snapshot"),
            last_snapshot=data.get("last_snapshot"),
            total_snapshots=data.get("total_snapshots", 0),
            tracking_days=data.get("tracking_days", 0),
            metadata=data.get("metadata", {})
        )


@dataclass
class Snapshot:
    """Snapshot of codebase state at a point in time."""
    id: str
    project_hash: str
    timestamp: datetime
    sequence: int
    backend: Dict[str, Any] = field(default_factory=dict)
    frontend: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    compared_to: Optional[str] = None
    drift_score: float = 0.0
    status: str = "healthy"  # baseline, healthy, caution, high
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "project_hash": self.project_hash,
            "timestamp": self.timestamp.isoformat(),
            "sequence": self.sequence,
            "backend": self.backend,
            "frontend": self.frontend,
            "metadata": self.metadata,
            "compared_to": self.compared_to,
            "drift_score": self.drift_score,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Snapshot":
        """Create Snapshot from dictionary."""
        timestamp = datetime.fromisoformat(data["timestamp"]) if isinstance(data["timestamp"], str) else data["timestamp"]
        return cls(
            id=data["id"],
            project_hash=data["project_hash"],
            timestamp=timestamp,
            sequence=data["sequence"],
            backend=data.get("backend", {}),
            frontend=data.get("frontend", {}),
            metadata=data.get("metadata", {}),
            compared_to=data.get("compared_to"),
            drift_score=data.get("drift_score", 0.0),
            status=data.get("status", "healthy")
        )


@dataclass
class Diff:
    """Structural diff between two snapshots."""
    from_snapshot: str
    to_snapshot: str
    time_elapsed: str
    backend_changes: Dict[str, Any] = field(default_factory=dict)
    frontend_changes: Dict[str, Any] = field(default_factory=dict)
    file_changes: Dict[str, Any] = field(default_factory=dict)
    drift_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "from_snapshot": self.from_snapshot,
            "to_snapshot": self.to_snapshot,
            "time_elapsed": self.time_elapsed,
            "backend_changes": self.backend_changes,
            "frontend_changes": self.frontend_changes,
            "file_changes": self.file_changes,
            "drift_score": self.drift_score,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Diff":
        """Create Diff from dictionary."""
        return cls(
            from_snapshot=data["from_snapshot"],
            to_snapshot=data["to_snapshot"],
            time_elapsed=data["time_elapsed"],
            backend_changes=data.get("backend_changes", {}),
            frontend_changes=data.get("frontend_changes", {}),
            file_changes=data.get("file_changes", {}),
            drift_score=data.get("drift_score", 0.0),
            metadata=data.get("metadata", {})
        )


@dataclass
class DriftScore:
    """Drift score with interpretation."""
    score: float
    status: str  # healthy, caution, high
    components: Dict[str, float] = field(default_factory=dict)
    interpretation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "score": self.score,
            "status": self.status,
            "components": self.components,
            "interpretation": self.interpretation
        }

