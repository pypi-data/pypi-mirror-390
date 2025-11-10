"""
File I/O operations for .rohkun/ directory.

Handles creation and management of the .rohkun/ directory structure.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class RohkunFileManager:
    """Manages file operations for .rohkun/ directory."""
    
    def __init__(self, project_dir: str):
        """
        Initialize file manager for a project.
        
        Args:
            project_dir: Root directory of the project
        """
        self.project_dir = Path(project_dir)
        self.rohkun_dir = self.project_dir / ".rohkun"
        self.snapshots_dir = self.rohkun_dir / "snapshots"
        self.diffs_dir = self.snapshots_dir / "diffs"
        self.reports_dir = self.rohkun_dir / "reports"
    
    def create_rohkun_directory(self) -> None:
        """Create .rohkun/ directory structure."""
        try:
            self.rohkun_dir.mkdir(exist_ok=True)
            self.snapshots_dir.mkdir(exist_ok=True)
            self.diffs_dir.mkdir(exist_ok=True)
            self.reports_dir.mkdir(exist_ok=True)
            logger.info(f"Created .rohkun/ directory structure in {self.project_dir}")
        except Exception as e:
            logger.error(f"Failed to create .rohkun/ directory: {e}")
            raise
    
    def save_project_json(self, project_data: Dict[str, Any]) -> Path:
        """
        Save project.json file.
        
        Args:
            project_data: Project data dictionary
            
        Returns:
            Path to saved file
        """
        project_file = self.rohkun_dir / "project.json"
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        logger.debug(f"Saved project.json to {project_file}")
        return project_file
    
    def load_project_json(self) -> Optional[Dict[str, Any]]:
        """
        Load project.json file.
        
        Returns:
            Project data dictionary or None if file doesn't exist
        """
        project_file = self.rohkun_dir / "project.json"
        if not project_file.exists():
            return None
        
        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load project.json: {e}")
            return None
    
    def save_snapshot_json(self, snapshot_id: str, snapshot_data: Dict[str, Any]) -> Path:
        """
        Save snapshot JSON file.
        
        Args:
            snapshot_id: Snapshot ID (e.g., snapshot_20250109_143022)
            snapshot_data: Snapshot data dictionary
            
        Returns:
            Path to saved file
        """
        snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
        logger.debug(f"Saved snapshot to {snapshot_file}")
        return snapshot_file
    
    def load_snapshot_json(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """
        Load snapshot JSON file.
        
        Args:
            snapshot_id: Snapshot ID
            
        Returns:
            Snapshot data dictionary or None if file doesn't exist
        """
        snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"
        if not snapshot_file.exists():
            return None
        
        try:
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load snapshot {snapshot_id}: {e}")
            return None
    
    def save_diff_json(self, from_snapshot: str, to_snapshot: str, diff_data: Dict[str, Any]) -> Path:
        """
        Save diff JSON file.
        
        Args:
            from_snapshot: Source snapshot ID
            to_snapshot: Target snapshot ID
            diff_data: Diff data dictionary
            
        Returns:
            Path to saved file
        """
        # Extract timestamps from snapshot IDs
        from_ts = from_snapshot.replace("snapshot_", "")
        to_ts = to_snapshot.replace("snapshot_", "")
        diff_file = self.diffs_dir / f"diff_{from_ts}_to_{to_ts}.json"
        
        with open(diff_file, 'w', encoding='utf-8') as f:
            json.dump(diff_data, f, indent=2, ensure_ascii=False)
        logger.debug(f"Saved diff to {diff_file}")
        return diff_file
    
    def save_report_md(self, snapshot_id: str, report_content: str) -> Path:
        """
        Save markdown report file.
        
        Args:
            snapshot_id: Snapshot ID
            report_content: Report markdown content
            
        Returns:
            Path to saved file
        """
        # Extract timestamp from snapshot ID
        timestamp = snapshot_id.replace("snapshot_", "")
        report_file = self.reports_dir / f"report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        logger.debug(f"Saved report to {report_file}")
        return report_file
    
    def load_snapshot_index(self) -> Dict[str, Any]:
        """
        Load snapshot index JSON file.
        
        Returns:
            Snapshot index dictionary (empty dict if file doesn't exist)
        """
        index_file = self.snapshots_dir / "snapshot_index.json"
        if not index_file.exists():
            return {"project_hash": "", "snapshots": []}
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load snapshot index: {e}")
            return {"project_hash": "", "snapshots": []}
    
    def save_snapshot_index(self, index_data: Dict[str, Any]) -> Path:
        """
        Save snapshot index JSON file.
        
        Args:
            index_data: Snapshot index data dictionary
            
        Returns:
            Path to saved file
        """
        index_file = self.snapshots_dir / "snapshot_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        logger.debug(f"Saved snapshot index to {index_file}")
        return index_file
    
    def create_readme(self, project: "Project") -> Path:
        """
        Create README.md file in .rohkun/ directory.
        
        Args:
            project: Project instance
            
        Returns:
            Path to created README file
        """
        readme_file = self.rohkun_dir / "README.md"
        
        readme_content = f"""# Rohkun Project Tracking

**Project:** {project.project_name}  
**Hash:** {project.project_hash}  
**Created:** {project.created_at.strftime('%Y-%m-%d %H:%M:%S')}  
**Snapshots:** {project.total_snapshots}  
**Tracking Days:** {project.tracking_days}

## What is this?

This directory contains chronological snapshots of your project's API surface.
Rohkun tracks how your backend endpoints and frontend API calls evolve over time.

## Directory Structure

- `project.json` - Project identity and metadata
- `snapshots/` - Individual snapshot files
  - `snapshot_index.json` - Chronological index of all snapshots
  - `snapshot_*.json` - Individual snapshot data
  - `diffs/` - Diff files between snapshots
- `reports/` - Generated markdown reports

## Usage

- View latest report: `cat .rohkun/reports/report_*.md | tail -1`
- View snapshot history: `cat .rohkun/snapshots/snapshot_index.json`
- Compare snapshots: Check `.rohkun/snapshots/diffs/` directory

## Learn More

Visit https://rohkun.dev for documentation and guides.
"""
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        logger.debug(f"Created README.md at {readme_file}")
        return readme_file
    
    def project_exists(self) -> bool:
        """Check if .rohkun/ directory exists."""
        return self.rohkun_dir.exists() and (self.rohkun_dir / "project.json").exists()

