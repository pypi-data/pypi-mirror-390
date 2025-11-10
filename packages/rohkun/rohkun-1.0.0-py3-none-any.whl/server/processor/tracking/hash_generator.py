"""
Hash generation utilities for project tracking.

Generates unique identifiers for projects and snapshots.
"""

import secrets
from datetime import datetime


def generate_project_hash() -> str:
    """
    Generate unique project hash.
    
    Format: RHKN-XXXXXX (6 hex characters)
    Example: RHKN-27F037
    
    Collision probability: ~1 in 16 million
    Short enough for CLI display, unique enough for production.
    
    Returns:
        str: Project hash in format RHKN-XXXXXX
    """
    random_hex = secrets.token_hex(3).upper()
    return f"RHKN-{random_hex}"


def generate_snapshot_id() -> str:
    """
    Generate snapshot ID with timestamp.
    
    Format: snapshot_YYYYMMDD_HHMMSS
    Example: snapshot_20250109_143022
    
    Sortable chronologically and human-readable.
    
    Returns:
        str: Snapshot ID with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"snapshot_{timestamp}"

