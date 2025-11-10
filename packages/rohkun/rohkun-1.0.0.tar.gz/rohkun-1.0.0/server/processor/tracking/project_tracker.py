"""
Project tracker - main orchestrator for project tracking.

Handles project initialization, snapshot creation, and diff computation.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .models import Project, Snapshot, Diff
from .file_manager import RohkunFileManager
from .snapshot_manager import SnapshotManager
from .diff_calculator import DiffCalculator
from .drift_calculator import DriftCalculator
from .hash_generator import generate_project_hash

logger = logging.getLogger(__name__)


class ProjectTracker:
    """Main project tracking orchestrator."""
    
    def __init__(self, project_dir: str):
        """
        Initialize project tracker.
        
        Args:
            project_dir: Root directory of the project
        """
        self.project_dir = Path(project_dir).resolve()
        self.file_manager = RohkunFileManager(str(self.project_dir))
        self.snapshot_manager = SnapshotManager(self.file_manager)
        self.diff_calculator = DiffCalculator()
        self.drift_calculator = DriftCalculator()
    
    def initialize_or_load_project(self) -> Project:
        """
        Initialize new project or load existing one.
        
        Returns:
            Project instance
        """
        # Check if project already exists
        if self.file_manager.project_exists():
            logger.info("Existing project detected, loading...")
            return self.load_project()
        
        # Initialize new project
        logger.info("No existing project detected, initializing new project...")
        return self.initialize_project()
    
    def initialize_project(self) -> Project:
        """
        Initialize a new Rohkun project.
        
        Creates:
        - .rohkun/ directory structure
        - project.json with unique hash
        - README.md with tracking info
        
        Returns:
            Project instance
        """
        project_hash = generate_project_hash()
        project_name = self._detect_project_name()
        
        project = Project(
            project_hash=project_hash,
            project_name=project_name,
            root_dir=str(self.project_dir),
            created_at=datetime.now(),
            total_snapshots=0,
            tracking_days=0
        )
        
        # Create directory structure
        self.file_manager.create_rohkun_directory()
        
        # Save project file
        self.file_manager.save_project_json(project.to_dict())
        
        # Create README
        self.file_manager.create_readme(project)
        
        logger.info(f"Initialized new project: {project_name} ({project_hash})")
        return project
    
    def load_project(self) -> Optional[Project]:
        """
        Load existing project.
        
        Returns:
            Project instance or None if project doesn't exist
        """
        project_data = self.file_manager.load_project_json()
        if not project_data:
            return None
        
        project = Project.from_dict(project_data)
        project.root_dir = str(self.project_dir)  # Ensure root_dir is set
        
        logger.info(f"Loaded project: {project.project_name} ({project.project_hash})")
        return project
    
    def create_snapshot(
        self,
        project: Project,
        analysis_result: Dict[str, Any]
    ) -> Snapshot:
        """
        Create a new snapshot from analysis result.
        
        Args:
            project: Project instance
            analysis_result: Analysis result dictionary
            
        Returns:
            Snapshot instance
        """
        is_baseline = project.total_snapshots == 0
        
        # Create snapshot
        snapshot = self.snapshot_manager.create_snapshot(
            project=project,
            analysis_result=analysis_result,
            is_baseline=is_baseline
        )
        
        # Load last snapshot for comparison
        last_snapshot = None
        if not is_baseline:
            last_snapshot = self.snapshot_manager.get_last_snapshot(project)
            if last_snapshot:
                snapshot.compared_to = last_snapshot.id
        
        # Compute diff if not baseline
        diff = None
        if last_snapshot:
            diff = self.diff_calculator.compute_diff(last_snapshot, snapshot)
            
            # Calculate drift
            drift_score = self.drift_calculator.calculate_drift(diff)
            snapshot.drift_score = drift_score.score
            snapshot.status = drift_score.status
            
            # Save diff
            self.file_manager.save_diff_json(
                last_snapshot.id,
                snapshot.id,
                diff.to_dict()
            )
        else:
            snapshot.drift_score = 0.0
            snapshot.status = "baseline"
        
        # Save snapshot
        self.snapshot_manager.save_snapshot(snapshot)
        
        # Update snapshot index
        self.snapshot_manager.update_snapshot_index(project, snapshot)
        
        # Update project metadata
        if is_baseline:
            project.first_snapshot = snapshot.id
        project.last_snapshot = snapshot.id
        project.total_snapshots += 1
        
        # Calculate tracking days
        if project.first_snapshot:
            days = (snapshot.timestamp - project.created_at).days
            project.tracking_days = max(0, days)
        
        # Save updated project
        self.file_manager.save_project_json(project.to_dict())
        
        logger.info(f"Created snapshot {snapshot.id} (sequence {snapshot.sequence})")
        return snapshot
    
    def compute_diff(self, before: Snapshot, after: Snapshot) -> Diff:
        """
        Compute structural diff between snapshots.
        
        Args:
            before: Previous snapshot
            after: Current snapshot
            
        Returns:
            Diff instance
        """
        return self.diff_calculator.compute_diff(before, after)
    
    def calculate_drift(self, diff: Diff) -> float:
        """
        Calculate drift score from diff.
        
        Args:
            diff: Diff instance
            
        Returns:
            Drift score (0.0 - 1.0)
        """
        drift_score = self.drift_calculator.calculate_drift(diff)
        return drift_score.score
    
    def get_last_snapshot(self, project: Project) -> Optional[Snapshot]:
        """
        Get the most recent snapshot for a project.
        
        Args:
            project: Project instance
            
        Returns:
            Last snapshot or None
        """
        return self.snapshot_manager.get_last_snapshot(project)
    
    def list_snapshots(self, project: Project) -> list:
        """
        List all snapshots for a project.
        
        Args:
            project: Project instance
            
        Returns:
            List of snapshot index entries
        """
        return self.snapshot_manager.list_snapshots(project.project_hash)
    
    def _detect_project_name(self) -> str:
        """
        Detect project name from directory or config files.
        
        Returns:
            Project name string
        """
        # Try package.json
        package_json = self.project_dir / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    name = data.get("name", "")
                    if name:
                        return name
            except Exception:
                pass
        
        # Try pyproject.toml
        pyproject_toml = self.project_dir / "pyproject.toml"
        if pyproject_toml.exists():
            try:
                import tomli
                with open(pyproject_toml, 'rb') as f:
                    data = tomli.load(f)
                    name = data.get("project", {}).get("name", "")
                    if name:
                        return name
            except Exception:
                pass
        
        # Fallback to directory name
        return self.project_dir.name

